import re,collections,json,sys
from common import *
CANON={'BerandaM4','RecCreateM4','SkuDetailM4','UlasanM4Salinan','ProdukIndexM4','KategoriM4','SalinanBlogM4','SalinanArtikel2M4',
 'DesktopBerandaM4','DesktopProdukM4','DesktopSkuM4','DesktopUlasanM4','DesktopProdukIndexM4','DesktopKategoriM4','DesktopBlogM4','DesktopArtikelM4'}
CANON={c+'.dc.html' for c in CANON}
def strip_js(s):
    s=RE_CSSCOMMENT.sub('',s)
    out=[]
    for l in s.split('\n'):
        out.append(re.sub(r"(?<![:'\"\\])//(?!['\"]).*$",'',l) if '//' in l and not re.search(r"https?://",l.split('//')[0]+'//') else l)
    return '\n'.join(out)
def decls(style):
    # split on ; outside parens
    res=[];d=0;cur='';q=None
    for ch in style:
        if q:
            cur+=ch
            if ch==q:q=None
            continue
        if ch in '\'"': q=ch;cur+=ch;continue
        if ch=='(':d+=1
        if ch==')':d=max(0,d-1)
        if ch==';' and d==0: res.append(cur);cur=''
        else: cur+=ch
    res.append(cur)
    o=[]
    for r in res:
        if ':' in r and '{{' not in r.split(':')[0]:
            k,v=r.split(':',1); k=k.strip().lower();v=re.sub(r'\s+',' ',v.strip())
            if re.fullmatch(r'-{0,2}[a-z][a-z0-9-]*',k) and v: o.append((k,v))
    return o
def parse_board(src):
    src2=RE_HTMLCOMMENT.sub('',src)
    h,m,sc=split(src2)
    h=RE_CSSCOMMENT.sub('',h)
    sc=strip_js(sc)
    recs=[]
    tok={}
    tokmq={}
    # helmet: walk rules
    css=''.join(re.findall(r'<style[^>]*>(.*?)</style>',h,re.S))
    rules=[]
    def walk(css,ctx):
        i=0;n=len(css);buf=''
        while i<n:
            c=css[i]
            if c=='{':
                sel=buf.strip();buf='';d=1;j=i+1
                while j<n and d:
                    if css[j]=='{':d+=1
                    elif css[j]=='}':d-=1
                    j+=1
                body=css[i+1:j-1]
                if sel.startswith('@media') or sel.startswith('@supports') or sel.startswith('@container'):
                    walk(body,ctx+[sel])
                elif sel.startswith('@keyframes') or sel.startswith('@-webkit-keyframes'):
                    rules.append((ctx,sel,body))
                else:
                    rules.append((ctx,sel,body))
                i=j
            elif c==';' and buf.strip().startswith('@'):
                rules.append((ctx,buf.strip(),''));buf='';i+=1
            elif c=='}':
                i+=1
            else: buf+=c;i+=1
    walk(css,[])
    for ctx,sel,body in rules:
        if sel==':root' or sel.startswith(':root'):
            for k,v in decls(body):
                if k.startswith('--'):
                    if ctx: tokmq.setdefault(k,[]).append((' '.join(ctx),v))
                    else: tok[k]=v
            continue
        if sel.startswith('@'): continue
        for k,v in decls(body):
            recs.append(('helmet',sel,' '.join(ctx),k,v))
    # inline
    m2=m
    for st in re.findall(r'\bstyle="([^"]*)"',m2):
        for k,v in decls(st): recs.append(('inline','','',k,v))
    # script string literals containing css
    for q in re.findall(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"",sc):
        t=q[0] or q[1]
        if re.match(r'\s*;?\s*-{0,2}[a-z][a-z-]*\s*:\s*[^/]',t) and not t.startswith('http'):
            for k,v in decls(t):
                recs.append(('script','','',k,v))
    # svg attrs
    svg=[]
    for tag,attrs in re.findall(r'<(svg|path|circle|rect|ellipse|line|polyline|polygon|g|stop)\b([^>]*)>',m2):
        svg.append((tag,dict(re.findall(r'([\w:-]+)="([^"]*)"',attrs))))
    return dict(helmet=h,css=css,markup=m2,script=sc,recs=recs,tok=tok,tokmq=tokmq,svg=svg,rules=rules)
def resolve(v,tok,depth=0):
    if depth>6: return v
    def rep(mm):
        name=mm.group(1);fb=mm.group(2)
        if name in tok: return tok[name]
        return fb.strip() if fb else mm.group(0)
    new=re.sub(r'var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)',rep,v)
    return resolve(new,tok,depth+1) if new!=v else new
def px(s):
    """convert single length token to px float or None"""
    m=re.fullmatch(r'(-?[\d.]+)(rem|px|em)?',s.strip())
    if not m: return None
    n=float(m.group(1));u=m.group(2)
    if u=='rem': return round(n*10,3)
    if u=='px' or (u is None and n==0): return n
    return None
def calc_eval(s):
    # calc(a / 2), calc(a * b), calc(a + b) with rem/px -> px
    m=re.fullmatch(r'calc\((.*)\)',s.strip())
    if not m: return None
    e=m.group(1)
    e=re.sub(r'(-?[\d.]+)rem',lambda x:str(float(x.group(1))*10),e)
    e=re.sub(r'(-?[\d.]+)px',lambda x:x.group(1),e)
    e=re.sub(r'calc\(',' (',e)
    if re.fullmatch(r'[\d.\s+\-*/()]+',e):
        try: return round(eval(e,{'__builtins__':{}}),3)
        except Exception: return None
    return None
def split_vals(v):
    res=[];d=0;cur=''
    for ch in v:
        if ch=='(':d+=1
        if ch==')':d-=1
        if ch==' ' and d==0:
            if cur:res.append(cur);cur=''
        else:cur+=ch
    if cur:res.append(cur)
    return res
def load_all(project):
    files,canvas=load(project)
    out={}
    for f,s in files.items():
        out[f]=parse_board(s); out[f]['bp']='m' if canvas['boards'][f]['w']==360 else 'd'
        out[f]['title']=canvas['boards'][f]['title']; out[f]['raw']=s
    return out,canvas

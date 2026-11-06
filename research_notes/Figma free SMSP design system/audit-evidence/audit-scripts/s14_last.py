import sys,re,collections
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
print('## headings')
for bp in('m','d'):
    for h in('h1','h2','h3'):
        C=collections.Counter()
        for f,b in B.items():
            if f not in CANON or b['bp']!=bp: continue
            for mm in re.finditer(r'<'+h+r'\b([^>]*)>',b['markup']):
                st=re.search(r'style="([^"]*)"',mm.group(1));d=dict(decls(st.group(1))) if st else {}
                C[(px(resolve(d.get('font-size','-'),b['tok'])) or d.get('font-size','-'),resolve(d.get('font-weight','-'),b['tok']),d.get('text-transform','-')[:5],resolve(d.get('color','inherit'),b['tok'])[:8],d.get('letter-spacing','-'),d.get('line-height','-'))]+=1
        print(bp,h,C.most_common(9))
raw=sum(len(b['raw']) for b in B.values())
st=sum(len(RE_CSSCOMMENT.sub('',RE_HTMLCOMMENT.sub('',b['raw']))) for b in B.values())
rawc=sum(len(b['raw']) for f,b in B.items() if f in CANON);stc=sum(len(RE_CSSCOMMENT.sub('',RE_HTMLCOMMENT.sub('',b['raw']))) for f,b in B.items() if f in CANON)
print('raw',raw,'stripped',st,'%.1f%% comment'%(100*(raw-st)/raw),'| canon raw',rawc,'stripped',stc,'%.1f%%'%(100*(rawc-stc)/rawc))
print('lang',collections.Counter(re.search(r'<html lang="([^"]*)"',b['raw']).group(1) for b in B.values()))
s=B['RecCreateM4.dc.html']['script'];m=re.search(r'this\._d = \[(.*?)\];',s,re.S)
print('RecCreate SKU rows',len(re.findall(r'\[[\d.]+,[\d.]+,[\d.]+,[\d.]+,\d+\]',m.group(1))) if m else None)
s=B['DesktopProdukIndexM4.dc.html']['script'];p=re.findall(r"\['([^']+)',(\d+),",s);print('product index',len(p),sum(int(x[1]) for x in p),p)
for tok in('font-weight','border-radius','line-height','letter-spacing'):
    t=l=0
    for f,b in B.items():
        if f in CANON:
            for src,s_,cx,k,v in b['recs']:
                if k==tok and '{{' not in v:
                    if 'var(' in v:t+=1
                    else:l+=1
    print(tok,'token',t,'literal',l)
def lin(x):
    x/=255;return x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4
def L(c): return .2126*lin(c[0])+.7152*lin(c[1])+.0722*lin(c[2])
def cr(a,b):
    la,lb=L(a),L(b)
    if la<lb:la,lb=lb,la
    return (la+.05)/(lb+.05)
print('c9c9cb on ececec',round(cr((201,201,203),(236,236,236)),2),'dcdcde on white',round(cr((220,220,222),(255,255,255)),2),'4ade80 white',round(cr((74,222,128),(255,255,255)),2),'5f5f5f on fdecec',round(cr((95,95,95),(253,236,236)),2),'white on rgb(255,30,0)',round(cr((255,255,255),(255,30,0)),2))
print('reduced motion boards canon',sum('prefers-reduced-motion' in b['css'] for f,b in B.items() if f in CANON),'all',sum('prefers-reduced-motion' in b['css'] for b in B.values()))
print('outline none canon',sum(1 for f,b in B.items() if f in CANON for r in b['recs'] if r[3]=='outline' and r[4].startswith('none')))
print('text-align justify canon',sum(1 for f,b in B.items() if f in CANON for r in b['recs'] if r[3]=='text-align' and r[4]=='justify'),'hyphens',sum(1 for f,b in B.items() if f in CANON for r in b['recs'] if r[3]=='hyphens'),'line-clamp',sum(1 for f,b in B.items() if f in CANON for r in b['recs'] if 'line-clamp' in r[3]))
print('sticky/fixed canon per board:')
for f,b in sorted(B.items()):
    if f in CANON:
        c=collections.Counter(r[4] for r in b['recs'] if r[3]=='position' and r[4] in('sticky','fixed'));print(' ',f[:-8],dict(c))
print('Blog titles: h1 in variants')
for n in('SalinanBlogM4','SalinanBlogM4Salinan','SalinanBlog2M4','SalinanBlog3M4','SalinanBlog4M4','SalinanBlog5M4'):
    m=re.search(r'<h1\b[^>]*>(.*?)</h1>',B[n+'.dc.html']['markup'],re.S);print(' ',n,re.sub(r'<[^>]+>|\s+',' ',m.group(1)).strip()[:80] if m else None)

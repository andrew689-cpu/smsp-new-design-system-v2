import sys,re,collections,hashlib
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
def boards(t,bp=None):
    for f,b in B.items():
        if t=='canon' and f not in CANON: continue
        if bp and b['bp']!=bp: continue
        yield f,b
print('## fonts')
for f,b in sorted(B.items()):
    l=re.findall(r'fonts\.googleapis\.com[^"\'\s)]*',b['raw'] and RE_HTMLCOMMENT.sub('',RE_CSSCOMMENT.sub('',b['raw'])))
    fh=b['tok'].get('--font-harga','')[:30]
    print(f,fh,set(l))
print('## font-face',sum('@font-face' in b['css'] for b in B.values()))
print('## --font-harga usage count per board canon')
for f,b in sorted(boards('canon')):
    print(f,len(re.findall(r'var\(--font-harga\)',b['markup']+b['script'])))
print('## svg icons')
RE_SVG=re.compile(r'<svg\b([^>]*)>(.*?)</svg>',re.S)
def sig(inner):
    s=re.sub(r'\s(stroke|fill|stroke-width|stroke-linecap|stroke-linejoin|style|opacity|aria-hidden|class)="[^"]*"','',inner)
    return re.sub(r'\s+',' ',s).strip()
ic=collections.Counter();icc=collections.Counter();ex={};ctxs=collections.defaultdict(collections.Counter)
sw=collections.Counter();swc=collections.Counter();size=collections.Counter();sizec=collections.Counter();vb=collections.Counter();vbc=collections.Counter();mode=collections.Counter();modec=collections.Counter();icboards=collections.defaultdict(set)
filled=stroked=0
for f,b in B.items():
    m=b['markup']
    for mm in RE_SVG.finditer(m):
        a=dict(re.findall(r'([\w:-]+)="([^"]*)"',mm.group(1)));inner=mm.group(2)
        k=sig(inner)
        v=a.get('viewBox','')
        key=v+'|'+k
        ic[key]+=1;ex[key]=(a,inner);icboards[key].add(f)
        w=a.get('width','?')+'x'+a.get('height','?')
        size[w]+=1;vb[v]+=1
        sws=set(re.findall(r'stroke-width="([^"]+)"',mm.group(0)))
        hasstroke='stroke="' in mm.group(0) and not all(x=='none' for x in re.findall(r'stroke="([^"]+)"',mm.group(0)))
        md='stroke' if hasstroke else 'fill'
        mode[md]+=1
        for s in sws: sw[s]+=1
        pre=m[max(0,mm.start()-300):mm.start()]
        lab=re.findall(r'aria-label="([^"{]+)"',pre)
        if lab: ctxs[key][lab[-1][:30]]+=1
        if f in CANON:
            icc[key]+=1;sizec[w]+=1;vbc[v]+=1;modec[md]+=1
            for s in sws: swc[s]+=1
print('total svg all',sum(ic.values()),'distinct geometry',len(ic),'| canon total',sum(icc.values()),'distinct',len(icc))
print('mode all',mode,'canon',modec)
print('stroke-widths all',sw.most_common(30));print('stroke-widths canon',swc.most_common(30))
print('sizes canon',sizec.most_common(40));print('viewBox canon',vbc.most_common(25));print('viewBox all',vb.most_common(25))
print('top icons canon:')
for k,v in icc.most_common(55):
    a,inner=ex[k]
    print(v,'all=%d'%ic[k],'boards=%d'%len(icboards[k]),a.get('viewBox'),a.get('width'),re.sub(r'\s+',' ',sig(inner))[:95],'CTX',ctxs[k].most_common(2))
print('## library signature tests (from memory of each library path grammar)')
sigs={'lucide chevron-right':'m9 18 6-6-6-6','lucide chevron-down':'m6 9 6 6 6-6','lucide x':'M18 6 6 18','lucide search':'m21 21-4.3-4.3','lucide check':'M20 6 9 17l-5-5','lucide arrow-right':'m12 5 7 7-7 7','lucide phone':'M22 16.92v3','lucide menu':'M4 12h16','feather chevron polyline':'points="9 18 15 12 9 6"','heroicons outline 24 ch-down':'M19.5 8.25l-7.5 7.5-7.5-7.5','heroicons x':'M6 18L18 6M6 6l12 12','material zero box':'M0 0h24v24H0z','tabler zero box':'M0 0h24v24H0z','phosphor viewbox':'viewBox="0 0 256 256"','remix':'viewBox="0 0 24 24" fill="currentColor"'}
all_markup=''.join(b['markup'] for b in B.values())
for k,v in sigs.items(): print(k,all_markup.count(v))
print('icon font / sprite use: <use',all_markup.count('<use '),'material-symbols',all_markup.count('material-symbols'),'class="lucide',all_markup.count('lucide'))
print('## images')
for t in('canon','all'):
    for bp in('m','d'):
        tot=empty=withalt=noalt=lazy=eager=dim=0;blob=set();dyn=0;altlit=0;altdyn=0
        for f,b in boards(t,bp):
            for a in re.findall(r'<img\b([^>]*)>',b['markup']):
                tot+=1
                alt=re.search(r'\balt="([^"]*)"',a)
                if not alt: noalt+=1
                elif alt.group(1)=='': empty+=1
                elif '{{' in alt.group(1): altdyn+=1
                else: altlit+=1
                if 'loading="lazy"' in a: lazy+=1
                if 'loading="eager"' in a: eager+=1
                if re.search(r'\bwidth="',a) : dim+=1
                if '{{' in (re.search(r'\bsrc="([^"]*)"',a) or [None,''])[1]: dyn+=1
            blob|=set(re.findall(r'/_blob/([0-9a-f]+)',b['markup']+b['script']+b['css']))
        print(t,bp,'img tags',tot,'alt-missing',noalt,'alt-empty',empty,'alt-literal',altlit,'alt-dynamic',altdyn,'lazy',lazy,'eager',eager,'width attr',dim,'src-dynamic',dyn,'distinct blobs',len(blob))
ext=collections.Counter()
for f,b in B.items():
    for u in re.findall(r'(?:src|url\()\s*=?\s*"?(https?://[^"\')\s]+)',b['markup']+b['css']+b['script']): ext[u.split('/')[2]]+=1
print('external img hosts',ext)
print('## semantics')
SEM=['header','nav','main','section','article','aside','footer','figure','figcaption','ul','ol','li','table','h1','h2','h3','h4','button','a','input','select','textarea','label','form','dialog','details','summary','blockquote','div','span','p','strong']
print('board|'+'|'.join(SEM))
tc=collections.Counter()
for f,b in sorted(B.items(),key=lambda kv:(kv[0] not in CANON,kv[0])):
    c=collections.Counter(re.findall(r'<([a-zA-Z][a-zA-Z0-9-]*)',b['markup']))
    if f in CANON: tc.update(c)
    print(('*' if f in CANON else ' ')+f+'|'+'|'.join(str(c[t]) for t in SEM))
print('canon totals',{t:tc[t] for t in SEM})
sem=sum(tc[t] for t in['header','nav','main','section','article','aside','footer','figure','ul','ol','li','table','h1','h2','h3','h4','button','a','input','label','blockquote','p']);print('semantic-ish',sem,'div+span',tc['div']+tc['span'])
print('## aria/role')
rc=collections.Counter();ac=collections.Counter()
for f,b in boards('canon'):
    rc.update(re.findall(r'\brole="([^"]+)"',b['markup']))
    ac.update(re.findall(r'\s(aria-[a-z]+)=',b['markup']))
print('roles canon',rc.most_common());print('aria attrs canon',ac.most_common())
print('## headings per board (h1 count, first texts)')
for f,b in sorted(boards('canon')):
    hs=re.findall(r'<(h[1-4])\b[^>]*>(.*?)</\1>',b['markup'],re.S)
    seq=''.join(h[0][1] for h in hs)
    print(f,'h1=%d'%sum(h[0]=='h1' for h in hs),seq[:60],'| main',b['markup'].count('<main'),'footer',b['markup'].count('<footer'),'header',b['markup'].count('<header'))
print('## interactive sizes (canon): explicit box sizes on <button>/<a>')
rows=collections.Counter();small=collections.Counter()
for bp in('m','d'):
    cnt=collections.Counter();sm=collections.Counter()
    for f,b in boards('canon',bp):
        for tag,attrs in re.findall(r'<(button|a)\b([^>]*)>',b['markup']):
            st=re.search(r'style="([^"]*)"',attrs); d=dict(decls(st.group(1))) if st else {}
            def v(k):
                x=d.get(k)
                if not x: return None
                return px(resolve(x,b['tok']).split()[0])
            h=v('height') or v('min-height');w=v('width') or v('min-width')
            if h is None and w is None: cnt['no explicit size']+=1;continue
            hh=h if h is not None else w
            if hh>=44: cnt['>=44']+=1
            elif hh>=24: cnt['24-43.9']+=1;sm[hh]+=1
            else: cnt['<24']+=1;sm[hh]+=1
    print(bp,cnt,'heights<44:',sm.most_common(15))
print('## inputs')
tc2=collections.Counter()
for f,b in boards('canon'):
    for a in re.findall(r'<input\b([^>]*)>',b['markup']):
        ty=re.search(r'type="([^"]+)"',a);tc2[ty.group(1) if ty else 'none']+=1
        tc2['with aria-label']+= 'aria-label' in a
        tc2['with id']+= ' id=' in a
        tc2['placeholder']+='placeholder=' in a
        tc2['disabled']+=' disabled' in a
print(tc2,'label tags',sum(b['markup'].count('<label') for f,b in boards('canon')),'for=',sum(b['markup'].count(' for=') for f,b in boards('canon')))
print('disabled attrs canon',sum(len(re.findall(r'\sdisabled=',b['markup'])) for f,b in boards('canon')))
print('## divs with onClick (non-semantic click targets)')
for t in('canon',):
    c=collections.Counter()
    for f,b in boards(t):
        for tag in re.findall(r'<([a-zA-Z0-9-]+)\b[^>]*\sonClick=',b['markup']): c[tag]+=1
    print(c)
print('## token defined vs used (all boards)')
toks=collections.Counter();use=collections.Counter()
for f,b in B.items():
    toks.update(b['tok'].keys())
    for t in re.findall(r'var\(\s*(--[\w-]+)',b['markup']+b['script']+b['css']): use[t]+=1
canonuse=collections.Counter()
for f,b in boards('canon'):
    for t in re.findall(r'var\(\s*(--[\w-]+)',b['markup']+b['script']+b['css']): canonuse[t]+=1
for t,n in sorted(toks.items(),key=lambda kv:use[kv[0]]):
    print(t,'def_boards=%d'%n,'uses_all=%d'%use[t],'uses_canon=%d'%canonuse[t])
print('## hex in JS outside style decls (canon)')
c=collections.Counter()
for f,b in boards('canon'):
    c.update(x.lower() for x in re.findall(r'#[0-9a-fA-F]{6}\b',b['script']))
print(c.most_common(30))

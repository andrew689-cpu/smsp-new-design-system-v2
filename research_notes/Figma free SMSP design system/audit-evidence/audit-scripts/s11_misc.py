import sys,re,collections
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
print('## spacing/type token values per canonical board')
keys=['--sisi','--talang','--seksi','--jarak-y-antar','--jarak-y-dalam','--dalam','--rapat','--jarak-x-dua','--jarak-x-tiga','--selokan-ubin','--teks-section','--teks-page','--teks-lead','--teks-chip','--teks-price','--teks-price-lg']
print('board|'+'|'.join(keys))
for f,b in sorted(B.items(),key=lambda kv:(kv[0] not in CANON,kv[1]['bp'],kv[0])):
    print(('*' if f in CANON else ' ')+f[:-8]+'|'+'|'.join((b['tok'].get(k,'-')[:22]) for k in keys))
print('## page root sizing (first style with width: 36rem/144rem or data root)')
c=collections.Counter()
for f,b in B.items():
    for st in re.findall(r'style="([^"]*)"',b['markup']):
        d=dict(decls(st))
        if d.get('width') in('36rem','144rem') and d.get('max-width')=='100%':
            c[(b['bp'],d['width'],d.get('margin'),d.get('min-height'))]+=1
print(c.most_common(10))
print('vw/vh/svh/% usage across boards',{u:sum(len(re.findall(r'[\d.]'+u+r'\b',b['markup']+b['css'])) for b in B.values()) for u in('vw','vh','svh','dvh','cqw')})
print('## @media rules bodies')
for f,b in B.items():
    for ctx,s,body in b['rules']:
        if ctx and any('min-width' in c for c in ctx): print(f,ctx,s[:60],re.sub(r'\s+',' ',body)[:200])
print('## keyframes (canon, one each)')
seen=set()
for f,b in B.items():
    if f not in CANON: continue
    for ctx,s,body in b['rules']:
        if s.startswith('@keyframes') and s not in seen:
            seen.add(s);print(s,re.sub(r'\s+',' ',body)[:230])
print('## reduced motion rules example');
for f,b in B.items():
    r=[(s,re.sub(r'\s+',' ',body)[:100]) for ctx,s,body in b['rules'] if ctx and 'reduced' in ctx[0]]
    if f=='RecCreateM4.dc.html': print(f,len(r),r[:8])
print('## low-contrast text decl counts (color property, canon)')
c=collections.Counter()
for f,b in B.items():
    if f not in CANON: continue
    for src,s,ctx,k,v in b['recs']:
        if k=='color':
            r=resolve(v,b['tok']).lower()
            c[r]+=1
print(c.most_common(35))
print('## context of selected text colours (canon) - 3 samples each, with enclosing text')
for needle in ['rgba(255,255,255,0.68)','rgba(255,0,0,0.8)','var(--whatsapp)','color: var(--ink-4)']:
    n=0
    for f,b in B.items():
        if f not in CANON: continue
        for mm in re.finditer(re.escape(needle),b['markup']):
            ctx=b['markup'][max(0,mm.start()-160):mm.end()+160]
            print(needle,f,re.sub(r'\s+',' ',ctx));n+=1
            break
        if n>=2:break
print('## footer sample')
b=B['DesktopKategoriM4.dc.html']
i=b['markup'].find('kolomFooter');print(re.sub(r'\s+',' ',b['markup'][i-1200:i+700]))
print('## CTA samples')
for f,pat in (('DesktopProdukM4.dc.html',r'<a\b[^>]*background: var\(--brand\)[^>]*>.{0,300}'),('RecCreateM4.dc.html',r'<a\b[^>]*background: var\(--brand\)[^>]*>.{0,300}'),('RecCreateM4.dc.html',r'<a\b[^>]*background: #157f3c[^>]*>.{0,300}')):
    m=re.search(pat,B[f]['markup'],re.S)
    if m: print(f,re.sub(r'\s+',' ',m.group(0))[:760])
print('## CTA text inventory (anchors/buttons w/ brand bg, all canon)')
c=collections.Counter()
for f,b in B.items():
    if f not in CANON: continue
    for mm in re.finditer(r'<(a|button)\b[^>]*background: (?:var\(--brand\)|#157f3c|var\(--ink\)|#0a0a0a)[^>]*>(.*?)</\1>',b['markup'],re.S):
        t=re.sub(r'<svg.*?</svg>|<[^>]+>','',mm.group(2),flags=re.S);c[re.sub(r'\s+',' ',t).strip()[:40]]+=1
print(c.most_common(25))
print('## 1 literal colours only in non-canon boards')
HEX=re.compile(r'#[0-9a-fA-F]{6}\b')
inc=set();nonc=collections.Counter();where=collections.defaultdict(set)
for f,b in B.items():
    t=''.join(v for s,sel,ctx,k,v in b['recs'])+' '.join(' '.join(a.values()) for g,a in b['svg'] if 1)
    for h in HEX.findall(t):
        h=h.lower()
        if f in CANON: inc.add(h)
        else: nonc[h]+=1;where[h].add(f[:-8])
for h,n in nonc.most_common():
    if h not in inc: print(h,n,sorted(where[h])[:5])
print('## sc-for/sc-if/{{ }} canon',[ (t,sum(b['markup'].count(t) for f,b in B.items() if f in CANON)) for t in('<sc-for','<sc-if','{{')],'dc-import',sum('dc-import' in b['raw'] for b in B.values()),'support.js',sum('support.js' in b['raw'] for b in B.values()))
print('## scripts setState / refs / listeners canon');
for t in ('setState(','addEventListener(','IntersectionObserver','ResizeObserver','scrollTo(','localStorage','fetch(','setInterval(','setTimeout(','matchMedia('):
    print(t,sum(b['script'].count(t) for f,b in B.items() if f in CANON),'all',sum(b['script'].count(t) for b in B.values()))
print('## renderVals key rough count: lines "key: " at depth'); 
print('## rel attr sanity; target=_blank');print(collections.Counter(re.findall(r'rel="([^"]+)"',''.join(b['markup'] for f,b in B.items() if f in CANON))).most_common(5))
print('## external link samples');c=collections.Counter()
for f,b in B.items():
    if f in CANON:
        c.update(re.findall(r'https://www\.smsperkasa\.com/[\w/-]*',b['markup']+b['script']))
print(c.most_common(12))
print('## img aspect rules: images wrappers');
print('## product list from JS'); s=B['DesktopProdukIndexM4.dc.html']['script']; print(re.sub(r'\s+',' ',s)[:900])
s=B['RecCreateM4.dc.html']['script'];m=re.search(r'data\(\)\s*\{',s);print(re.sub(r'\s+',' ',s[m.start():m.start()+1100]))

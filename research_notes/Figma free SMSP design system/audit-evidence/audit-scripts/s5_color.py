import sys,re,collections,math
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
HEX=re.compile(r'#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b')
FN=re.compile(r'(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\([^()]*\)')
NAMED=set('white black red green blue gray grey orange yellow transparent currentcolor silver maroon navy teal lime gold pink purple tomato'.split())
def norm(c):
    c=c.strip()
    if c.startswith('#'):
        c=c.lower()
        if len(c) in(4,5): c='#'+''.join(x*2 for x in c[1:])
        return c
    if c.startswith(('rgb','hsl','okl','lab','lch','color')):
        return re.sub(r'\s+','',c.lower()).replace('rgba(','rgba(')
    return c.lower()
def rgb(c):
    if c.startswith('#') and len(c) in (7,9):
        return tuple(int(c[i:i+2],16) for i in (1,3,5))+((int(c[7:9],16)/255,) if len(c)==9 else (1.0,))
    m=re.match(r'rgba?\(([\d.]+),([\d.]+),([\d.]+)(?:,([\d.%]+))?\)',c)
    if m:
        a=m.group(4); a=1.0 if a is None else (float(a[:-1])/100 if a.endswith('%') else float(a))
        return (float(m.group(1)),float(m.group(2)),float(m.group(3)),a)
    if c=='white':return(255,255,255,1.0)
    if c=='black':return(0,0,0,1.0)
    return None
def lin(x):
    x/=255;return x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4
def L(c): return .2126*lin(c[0])+.7152*lin(c[1])+.0722*lin(c[2])
def cr(a,b):
    la,lb=L(a),L(b)
    if la<lb: la,lb=lb,la
    return (la+.05)/(lb+.05)
def lab(c):
    def f(t): return t**(1/3) if t>0.008856 else 7.787*t+16/116
    r,g,b=[lin(x) for x in c[:3]]
    X=(.4124*r+.3576*g+.1805*b)/.95047;Y=.2126*r+.7152*g+.0722*b;Z=(.0193*r+.1192*g+.9505*b)/1.08883
    return (116*f(Y)-16,500*(f(X)-f(Y)),200*(f(Y)-f(Z)))
def de(a,b):
    A,Bb=lab(a),lab(b);return math.dist(A,Bb)
ROLE={'color':'text','background':'surface','background-color':'surface','background-image':'surface','border':'border','border-color':'border','border-top':'border','border-bottom':'border','border-left':'border','border-right':'border','outline':'border','outline-color':'border','box-shadow':'shadow/ring','filter':'shadow/ring','text-shadow':'shadow/ring','fill':'icon','stroke':'icon','stop-color':'icon','text-decoration-color':'text','caret-color':'text','accent-color':'control','-webkit-text-fill-color':'text','-webkit-tap-highlight-color':'other','border-top-color':'border','border-bottom-color':'border'}
cnt=collections.defaultdict(lambda:{'all':0,'canon':0,'m':0,'d':0,'boards':set(),'cb':set(),'role':collections.Counter(),'src':collections.Counter()})
tokuse=collections.defaultdict(lambda:collections.Counter())
def add(c,f,role,src):
    e=cnt[c];e['all']+=1;e['boards'].add(f);e['role'][role]+=1;e['src'][src]+=1
    if f in CANON:
        e['canon']+=1;e['cb'].add(f);e[B[f]['bp']]+=1
tokendef=collections.defaultdict(set)
for f,b in B.items():
    colortok=set()
    for k,v in b['tok'].items():
        if HEX.fullmatch(v.strip()): colortok.add(k);tokendef[k].add(norm(v))
    for src,sel,ctx,k,v in b['recs']:
        if k.startswith('--'): continue
        role=ROLE.get(k,'other:'+k)
        for c in HEX.findall(v): 
            if 'url(' in v and c in v.split('url(')[1][:60]: continue
            add(norm(c),f,role,src)
        for c in FN.findall(v): add(norm(c),f,role,src)
        if k in ROLE or k in('color',):
            for w in re.findall(r'(?<![\w#-])([a-zA-Z]+)(?![\w(-])',v):
                if w.lower() in NAMED: add(w.lower(),f,role,src)
        for t in re.findall(r'var\(\s*(--[\w-]+)',v):
            if t in colortok:
                tokuse[t][role]+=1
                add('var('+t+')',f,role,src)
    for tag,a in b['svg']:
        for k in('fill','stroke','stop-color','flood-color','color'):
            if k in a:
                v=a[k].strip()
                if v.lower() in('none',''):continue
                role='icon'
                for c in HEX.findall(v): add(norm(c),f,role,'svg')
                for c in FN.findall(v): add(norm(c),f,role,'svg')
                if v.lower() in NAMED: add(v.lower(),f,role,'svg')
                m=re.match(r'var\(\s*(--[\w-]+)',v)
                if m and m.group(1) in colortok:
                    tokuse[m.group(1)]['icon']+=1
                    add('var('+m.group(1)+')',f,role,'svg')
print('## canonical boards',len(CANON),sorted(CANON))
print('## distinct literal colours (all boards):',sum(1 for c in cnt if not c.startswith('var(')))
print('## distinct literal colours (canonical):',sum(1 for c,e in cnt.items() if not c.startswith('var(') and e['canon']))
print('## opaque hex distinct canonical:',sum(1 for c,e in cnt.items() if c.startswith('#') and e['canon'] and len(c)==7))
print('value|all|canon|mob|desk|boards_all|boards_canon|roles|src')
for c,e in sorted(cnt.items(),key=lambda kv:(-kv[1]['canon'],-kv[1]['all'])):
    print('|'.join(map(str,[c,e['all'],e['canon'],e['m'],e['d'],len(e['boards']),len(e['cb']),dict(e['role'].most_common(4)),dict(e['src'])])))
print('## token→hex',{k:list(v) for k,v in tokendef.items()})
print('## clusters of opaque colours, deltaE76<=6 (all boards)')
ops=[c for c in cnt if not c.startswith('var(') and rgb(c) and rgb(c)[3]==1.0]
par={c:c for c in ops}
def fd(x):
    while par[x]!=x:x=par[x]
    return x
for i,a in enumerate(ops):
    for b2 in ops[i+1:]:
        if de(rgb(a),rgb(b2))<=6: par[fd(a)]=fd(b2)
cl=collections.defaultdict(list)
for c in ops:cl[fd(c)].append(c)
for k,v in sorted(cl.items(),key=lambda kv:-sum(cnt[c]['all'] for c in kv[1])):
    if len(v)>1: print([(c,cnt[c]['canon'],cnt[c]['all']) for c in sorted(v,key=lambda c:-cnt[c]['all'])])
print('## contrast')
pairs=[('#0a0a0a','#ffffff','ink/surface'),('#5f5f5f','#ffffff','ink-2/surface'),('#c9c9cb','#ffffff','ink-4/surface'),('#d70100','#ffffff','brand/surface (text or button)'),('#ff0000','#ffffff','brand-hero/surface'),('#ffffff','#d70100','white on brand'),('#ffffff','#ff0000','white on brand-hero'),('#15763b','#ffffff','price/surface'),('#15763b','#eaf7ee','price/price-bg'),('#d70100','#fdecec','brand/brand-subtle'),('#a84c46','#fdecec','nav-aktif/brand-subtle'),('#a84c46','#ffffff','nav-aktif/surface'),('#5f5f5f','#ececec','ink-2/line(sunken)'),('#0a0a0a','#ececec','ink/line(sunken)'),('#9ca3af','#ffffff','chat-mati on white'),('#ffffff','#9ca3af','white on chat-mati'),('#2563eb','#ffffff','chat-ikon/white'),('#16a34a','#ffffff','online-ikon/white'),('#25d366','#ffffff','whatsapp/white'),('#ffffff','#25d366','white on whatsapp'),('#ffb800','#ffffff','star/white'),('#9a6700','#ffffff','star-stroke/white'),('#ececec','#ffffff','line/white'),('#d4d4d4','#ffffff','line-kuat/white'),('#16357a','#eef1f9','biru-tinta/biru-dasar'),('#ff0000','#0a0a0a','brand-hero/ink')]
for a,b2,n in pairs:
    print(n,a,b2,round(cr(rgb(a),rgb(b2)),2))

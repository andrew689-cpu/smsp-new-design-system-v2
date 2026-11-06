import sys,re,collections
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
def ctx(f,pat,before=0,after=520,n=1):
    m=B[f+'.dc.html']['markup'];o=[]
    for mm in list(re.finditer(pat,m))[:n]:
        o.append(re.sub(r'\s+',' ',re.sub(r'<svg.*?</svg>','<svg/>',m[max(0,mm.start()-before):mm.end()+after],flags=re.S)))
    return o
for label,f,pat,b4,af in [
 ('SKU row mobile','RecCreateM4',r'\{\{ r\.pNum \}\}',1300,250),
 ('SKU row desktop','DesktopProdukM4',r'\{\{ r\.pNum \}\}',1100,200),
 ('Product card home mobile','BerandaM4',r'Rp \{\{ c\.rp \}\}',900,120),
 ('Index tile desktop','DesktopProdukIndexM4',r'<sc-for list="\{\{ produk',0,900),
 ('Review card home','BerandaM4',r'data-rev-card',0,900),
 ('FAQ row','RecCreateM4',r'faq[A-Za-z]*\b[^>]*aria-expanded|aria-expanded="\{\{ f',500,500),
 ('Bottom bar','RecCreateM4',r'data-bar',0,800),
 ('Desktop pulau','DesktopProdukM4',r'data-pulau',0,700),
 ('Sheet','RecCreateM4',r'data-sheet',0,500),
 ('Blog row','SalinanBlogM4',r'<sc-for list="\{\{ artikelBaru',0,900),
 ('Fraud mobile','RecCreateM4',r'Waspada penipuan',700,200),
 ('Header mobile','RecCreateM4',r'<header\b',0,400),
 ('H1 Produk mobile','RecCreateM4',r'<h1\b',0,300),('h2 style m','RecCreateM4',r'<h2\b',0,220),('h2 style d','DesktopProdukM4',r'<h2\b',0,220),('h1 style d','DesktopProdukM4',r'<h1\b',0,220),
 ('Art body m','SalinanArtikel2M4',r'\{\{ b\.teks \}\}',350,60),('Art body d','DesktopArtikelM4',r'\{\{ b\.teks \}\}',300,60)]:
    for x in ctx(f,pat,b4,af): print('['+label+']',x[:1500]);print()
print('## undefined var refs (true)')
c=collections.Counter()
for f,b in B.items():
    defined=set(b['tok'])|set(b['tokmq'])|set(re.findall(r'(--[\w-]+)\s*:',b['markup']+b['script']))
    for mm in re.finditer(r'var\(\s*(--[\w-]+)\s*(,[^)]*)?\)',b['markup']+b['script']+b['css']):
        if mm.group(1) not in defined: c[(f[:-8],mm.group(1),(mm.group(2) or '')[:20])]+=1
for k,v in sorted(c.items()): print(k,v)
print('## token vs literal colours (canon)')
tv=collections.Counter()
for f,b in B.items():
    if f not in CANON: continue
    for src,s,cx,k,v in b['recs']:
        if k in('color','background','background-color','border','border-color','border-top','border-bottom','fill','stroke','box-shadow'):
            if re.search(r'#[0-9a-fA-F]{3,8}\b|rgba?\(',v): tv[k+':literal']+=1
            elif 'var(' in v: tv[k+':token']+=1
print(sorted(tv.items()))
def lin(x):
    x/=255;return x/12.92 if x<=.03928 else ((x+.055)/1.055)**2.4
def L(c): return .2126*lin(c[0])+.7152*lin(c[1])+.0722*lin(c[2])
def cr(a,b):
    la,lb=L(a),L(b)
    if la<lb:la,lb=lb,la
    return (la+.05)/(lb+.05)
def over(fg,a,bg): return tuple(fg[i]*a+bg[i]*(1-a) for i in range(3))
print('white .68 on ink',round(cr(over((255,255,255),.68,(10,10,10)),(10,10,10)),2),'red .8 on white',round(cr(over((255,0,0),.8,(255,255,255)),(255,255,255)),2),'rgb(255,30,0) w white',round(cr((255,30,0),(255,255,255)),2),'#157f3c white',round(cr((21,127,60),(255,255,255)),2),'#6d28d9/#faf5ff',round(cr((109,40,217),(250,245,255)),2),'ink-2 on ink-? white on 7c3aed',round(cr((255,255,255),(124,58,237)),2))
print('## rgba(255,0,0,.8) context');
for f,b in B.items():
    if f in CANON:
        mm=re.search(r'rgba\(255, ?0, ?0, ?0\.8\)',b['markup'])
        if mm: print(f,re.sub(r'\s+',' ',b['markup'][mm.start()-300:mm.end()+260]));break
print('## c9c9cb in scripts');
c=collections.Counter()
for f,b in B.items():
    if f in CANON:
        for l in b['script'].split('\n'):
            if '#c9c9cb' in l or '#dcdcde' in l or '#d6d6db' in l: c[re.sub(r'\s+',' ',l)[:130]]+=1
print(c.most_common(8))
print('## #4ade80 / #1d4ed8 / #7c3aed contexts')
for needle in['#4ade80','#1d4ed8','#7c3aed']:
    for f,b in B.items():
        if f in CANON:
            t=b['markup']+b['script'];i=t.find(needle)
            if i>=0: print(needle,f,re.sub(r'\s+',' ',t[max(0,i-200):i+80]));break
print('## hover string in script/markup canon', sum(len(re.findall(r'[Hh]over',b['markup']+b['script'])) for f,b in B.items() if f in CANON))
print('## tabs active style patterns: aria-current',collections.Counter(re.findall(r'aria-current="([^"]+)"',''.join(b['markup'] for f,b in B.items() if f in CANON))).most_common(5))
print('## script-size share canon: bytes of comments?')
print('## font-weight on data-harga 800?')

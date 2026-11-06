import sys,re,collections
sys.path.insert(0,sys.argv[2])
from parse import *
txt=open(sys.argv[3]).read()
def kw(p,n=6,b=260,a=420):
    seen=set();c=0
    for m in re.finditer(p,txt):
        s=re.sub(r'\s+',' ',txt[max(0,m.start()-b):m.end()+a])
        k=s[b//2:b//2+80]
        if k in seen: continue
        seen.add(k);print('>>',s);c+=1
        if c>=n:break
for p,n in [(r'baris hidup|BARIS HIDUP',3),(r'baris beku|membekukan|dibekukan|DIBEKUKAN|Dibekukan',5),(r'Lato',3),(r'BerandaM4',4),(r'aturan 50/50|ATURAN 50/50',1),(r'y=-1200|y -1200',3)]:
    print('\n#####',p);kw(p,n)
B,canvas=load_all(sys.argv[1])
print('\n##### sensitivity: font-size & colours with live-row swap')
import copy
ALT=(CANON-{'BerandaM4.dc.html','SalinanBlogM4.dc.html'})|{'SalinanBeranda2M4.dc.html','SalinanBlog5M4.dc.html'}
for name,S in(('canon',CANON),('alt',ALT)):
    fs=collections.Counter();col=collections.Counter();rad=collections.Counter()
    for f in S:
        b=B[f]
        if b['bp']!='m':continue
        for src,s,cx,k,v in b['recs']:
            if k=='font-size' and '{{' not in v:
                p=px(resolve(v,b['tok']));
                if p: fs[p]+=1
            if k.endswith('radius') and '{{' not in v: 
                p=px(resolve(v,b['tok']));
                if p is not None: rad[p]+=1
            if k in('color','background','background-color'):
                for c in re.findall(r'#[0-9a-fA-F]{6}\b',resolve(v,b['tok'])): col[c.lower()]+=1
    print(name,'fs',fs.most_common(12));print(name,'rad',rad.most_common(8));print(name,'col',col.most_common(12))
print('awas-bg def:',[f for f,b in B.items() if '--awas-bg' in b['tok']])
print('## total stripped vs comment % canon', sum(len(b['raw']) for f,b in B.items() if f in CANON))
print('## alt text sample');
c=collections.Counter()
for f,b in B.items():
    if f in CANON:
        c.update(re.findall(r'\balt="([^"{]{1,50})"',b['markup']))
print(c.most_common(8))
print('## Footer colour on mobile?');
b=B['KategoriM4.dc.html'];i=b['markup'].find('data-kaki');print(re.sub(r'\s+',' ',b['markup'][i:i+350]))
print('## Page counts titles'); 
c=collections.Counter(re.sub(r'\s*\d+$','',b['title']) for b in B.values()); print(c.most_common(6))

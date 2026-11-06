import sys,re,collections
sys.path.insert(0,sys.argv[2])
from common import *
files,canvas=load(sys.argv[1]); b=canvas['boards']
st={f:RE_CSSCOMMENT.sub('',RE_HTMLCOMMENT.sub('',s)) for f,s in files.items()}
print('## link graph (hrefs to .dc.html in stripped source incl. script)')
inb=collections.Counter(); outb={}
for f,s in sorted(st.items()):
    t=collections.Counter(re.findall(r'([A-Za-z0-9]+\.dc\.html)',s))
    outb[f]=t
    for k in t: 
        if k!=f: inb[k]+=1
    print(f,dict(t))
print('## inbound board count')
for f in sorted(files,key=lambda x:-inb[x]): print(f,inb[f])
print('## targets not on canvas')
miss=collections.Counter()
for f,t in outb.items():
    for k,v in t.items():
        if k not in files: miss[k]+=v
print(miss)
print('## external link hosts')
c=collections.Counter()
for f,s in st.items():
    for h in re.findall(r'https?://([^/"\'\s)<]+)',s): c[h]+=1
print(c.most_common(30))
print('## :root tokens matrix')
tok=collections.defaultdict(lambda: collections.defaultdict(list))
for f,s in st.items():
    h,_,_=split(s)
    for rb in re.findall(r':root\s*\{(.*?)\}',h,re.S):
        for m in re.finditer(r'(--[\w-]+)\s*:\s*([^;]+);',rb):
            tok[m.group(1)][re.sub(r'\s+',' ',m.group(2).strip())].append(f)
print('total distinct tokens',len(tok))
for k in sorted(tok,key=lambda k:-sum(len(v) for v in tok[k].values())):
    vals=tok[k]
    print(k,'boards=%d'%sum(len(v) for v in vals.values()),'|',' || '.join('%s [%d]'%(v[:70],len(fs)) for v,fs in sorted(vals.items(),key=lambda kv:-len(kv[1]))))
print('## var() usage (all boards) and undefined refs')
use=collections.Counter(); undefined=collections.Counter()
for f,s in st.items():
    h,_,_=split(s); defined=set(re.findall(r'(--[\w-]+)\s*:',h))
    for v in re.findall(r'var\(\s*(--[\w-]+)',s):
        use[v]+=1
        if v not in defined: undefined[(f,v)]+=1
print(use.most_common(120))
print('undefined per-board (may be set by script/inline):',undefined.most_common(40))
print('tokens per board:')
for f,s in sorted(st.items()):
    h,_,_=split(s)
    d=set(re.findall(r'(--[\w-]+)\s*:',h))
    print(f,len(d))

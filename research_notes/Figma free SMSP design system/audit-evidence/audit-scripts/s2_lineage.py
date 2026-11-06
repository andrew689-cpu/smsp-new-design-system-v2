import sys,re,hashlib,difflib,collections,itertools,os
sys.path.insert(0,sys.argv[2]); out=sys.argv[3]
from common import *
files,canvas=load(sys.argv[1]); b=canvas['boards']
def strip(s):
    s=RE_HTMLCOMMENT.sub('',s); s=RE_CSSCOMMENT.sub('',s)
    return s
st={f:strip(s) for f,s in files.items()}
for f,s in st.items():
    open(os.path.join(out,'stripped',f),'w').write(s)
toks={}
def tokenise(s):
    return [t.strip() for t in re.split(r'(?<=>)|(?=<)|\n',s) if t.strip()]
for f,s in st.items(): toks[f]=tokenise(s)
sets={f:collections.Counter(t) for f,t in toks.items()}
def jac(a,b):
    A,B=sets[a],sets[b]
    i=sum((A&B).values()); u=sum((A|B).values()); return i/u
fs=sorted(files)
print('## stripped sizes/hash')
for f in fs: print(f, len(files[f]), len(st[f]), hashlib.md5(st[f].encode()).hexdigest()[:8], b[f]['title'])
# Dates in comments per file
print('## dates in comments: min/max/count')
for f in fs:
    d=re.findall(r'20\d\d-\d\d-\d\d',''.join(RE_HTMLCOMMENT.findall(files[f])+RE_CSSCOMMENT.findall(files[f])))
    print(f, min(d) if d else None, max(d) if d else None, len(d), len(set(d)))
print('## best matches')
pairs=[]
for a,c in itertools.combinations(fs,2):
    pairs.append((jac(a,c),a,c))
pairs.sort(reverse=True)
for j,a,c in pairs[:50]: print(round(j,3),a,c)
print('## nearest neighbour per file')
for f in fs:
    best=max(((jac(f,g),g) for g in fs if g!=f))
    print(f,'->',best[1],round(best[0],3))
print('## clusters (J>=0.5)')
par={f:f for f in fs}
def find(x):
    while par[x]!=x: x=par[x]
    return x
for j,a,c in pairs:
    if j>=0.5: par[find(a)]=find(c)
cl=collections.defaultdict(list)
for f in fs: cl[find(f)].append(f)
for k,v in cl.items(): print(v)

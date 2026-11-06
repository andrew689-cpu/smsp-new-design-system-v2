import sys,re,collections
sys.path.insert(0,sys.argv[2])
from common import *
files,canvas=load(sys.argv[1])
U=collections.defaultdict(set);tot=0
for f,s in files.items():
    for c in RE_HTMLCOMMENT.findall(s)+RE_CSSCOMMENT.findall(s)+re.findall(r'(?m)^\s*//.*$',s):
        U[re.sub(r'\s+',' ',c).strip()].add(f);tot+=len(c)
print('total comment bytes',tot,'of',sum(len(s) for s in files.values()),'unique comments',len(U),'unique bytes',sum(len(k) for k in U))
d=collections.Counter()
for c in U:
    for x in set(re.findall(r'20\d\d-\d\d-\d\d',c)): d[x]+=1
print(sorted(d.items()))
open(sys.argv[3],'w').write('\n\n'.join('[%d boards e.g. %s] %s'%(len(v),sorted(v)[0],k) for k,v in sorted(U.items(),key=lambda kv:-len(kv[0]))))
for kw in ['tokens/','mobbin3.ts','Figma','design system','TANGGA','M3 ','Mobbin 4','kanon','referensi utama','repo ']:
    print(kw,sum(kw in c for c in U))

import sys,re,difflib
sys.path.insert(0,sys.argv[2])
from common import *
files,canvas=load(sys.argv[1])
def comments(s): return RE_HTMLCOMMENT.findall(s)+RE_CSSCOMMENT.findall(s)
def stripped(s): return RE_CSSCOMMENT.sub('',RE_HTMLCOMMENT.sub('',s))
def tok(s): return [t.strip() for t in re.split(r'(?<=>)|(?=<)|\n',s) if t.strip()]
pairs=[l.split() for l in sys.argv[3].split(',')]
for a,b in pairs:
    a+='.dc.html'; b+='.dc.html'
    A,B=tok(stripped(files[a])),tok(stripped(files[b]))
    sm=difflib.SequenceMatcher(None,A,B,autojunk=False) if len(A)<30000 else None
    print('\n=====',a,'vs',b, 'tokens',len(A),len(B))
    if sm:
        ops=[o for o in sm.get_opcodes() if o[0]!='equal']
        print('ops',len(ops), 'A changed',sum(o[2]-o[1] for o in ops),'B changed',sum(o[4]-o[3] for o in ops))
        for o in ops[:int(sys.argv[4])]:
            print(o[0],'A:',' '.join(A[o[1]:o[2]])[:260]); print('     B:',' '.join(B[o[3]:o[4]])[:260])
    ca,cb=set(comments(files[a])),set(comments(files[b]))
    print('comments only in',a,len(ca-cb),'only in',b,len(cb-ca))
    for c in sorted(cb-ca,key=len,reverse=True)[:3]: print('  B+',re.sub(r'\s+',' ',c)[:600])
    for c in sorted(ca-cb,key=len,reverse=True)[:2]: print('  A+',re.sub(r'\s+',' ',c)[:400])

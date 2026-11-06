import sys,re,hashlib,difflib,collections
sys.path.insert(0,sys.argv[2])
from common import *
files,canvas=load(sys.argv[1])
b=canvas['boards']
print('file|title|w|x|y|bytes|helmet|markup|script|cssCommentBytes|htmlCommentBytes|sc-for|sc-if|dc-import|style=|class=|<title>')
for f,s in sorted(files.items(),key=lambda kv:(b[kv[0]]['w'],b[kv[0]]['y'],b[kv[0]]['x'])):
    h,m,sc=split(s)
    t=re.search(r'<title>(.*?)</title>',s)
    cc=sum(len(x) for x in RE_CSSCOMMENT.findall(s)); hc=sum(len(x) for x in RE_HTMLCOMMENT.findall(s))
    print('|'.join(map(str,[f,b[f]['title'],b[f]['w'],b[f]['x'],b[f]['y'],len(s),len(h),len(m),len(sc),cc,hc,m.count('<sc-for'),m.count('<sc-if'),s.count('<dc-import'),len(re.findall(r'\bstyle="',m)),len(re.findall(r'\bclass="',m)),t.group(1) if t else ''])))
print()
print('data-props sample:')
for f,s in files.items():
    mm=re.search(r"data-props='(.*?)'",s,re.S)
    print(f,(mm.group(1)[:200] if mm else None))
# element tag sets
print()
c=collections.Counter()
for f,s in files.items():
    h,m,sc=split(s)
    for t in re.findall(r'<([a-zA-Z][a-zA-Z0-9-]*)',decomment(m)): c[t]+=1
print(c.most_common(60))
# custom attributes
c=collections.Counter()
for f,s in files.items():
    h,m,sc=split(s)
    for t in re.findall(r'\s([a-zA-Z@:_][\w:.\-]*)=["\']',decomment(m)): c[t]+=1
print(c.most_common(70))

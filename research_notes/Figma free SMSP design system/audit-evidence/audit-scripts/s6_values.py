import sys,re,collections
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
def tab(C,n=40,fmt=None):
    return ', '.join('%s×%d'%(k,v) for k,v in C.most_common(n))
def sel(tier,bp=None):
    for f,b in B.items():
        if tier=='canon' and f not in CANON: continue
        if bp and b['bp']!=bp: continue
        yield f,b
def collect(prop_pred,tier,bp,fn):
    C=collections.Counter()
    for f,b in sel(tier,bp):
        for src,s,ctx,k,v in b['recs']:
            if prop_pred(k): fn(C,f,b,src,k,v)
    return C
def report(name,pred,fn,n=45):
    print('\n###',name)
    for t in('canon','all'):
        for bp in('m','d'):
            C=collect(pred,t,bp,fn)
            print(t,bp,'total=%d distinct=%d:'%(sum(C.values()),len(C)),tab(C,n))
# font size
def fs(C,f,b,src,k,v):
    if '{{' in v: C['dynamic']+=1;return
    r=resolve(v,b['tok'])
    p=px(r); C[(str(p)+'px') if p is not None else r]+=1
report('font-size resolved',lambda k:k=='font-size',fs)
def fsmode(C,f,b,src,k,v):
    if '{{' in v: C['dynamic']+=1
    elif 'var(' in v: C['token']+=1
    else: C['literal']+=1
report('font-size token vs literal',lambda k:k=='font-size',fsmode)
def fslit(C,f,b,src,k,v):
    if 'var(' not in v and '{{' not in v:
        p=px(v);C[(str(p)+'px') if p is not None else v]+=1
report('font-size LITERAL values only',lambda k:k=='font-size',fslit)
def rawv(C,f,b,src,k,v):
    C[v]+=1
report('font-size tokens used raw',lambda k:k=='font-size',lambda C,f,b,src,k,v:(C.__setitem__(v,C[v]+1) if 'var(' in v else None))
def resv(C,f,b,src,k,v):
    if '{{' in v: C['dynamic']+=1;return
    C[resolve(v,b['tok'])]+=1
report('font-weight resolved',lambda k:k=='font-weight',resv)
report('line-height',lambda k:k=='line-height',resv)
report('letter-spacing',lambda k:k=='letter-spacing',resv)
report('font-family',lambda k:k in('font-family','font'),lambda C,f,b,src,k,v:C.__setitem__(v[:60],C[v[:60]]+1))
report('text-transform',lambda k:k=='text-transform',resv)
report('font-variant-numeric/feature',lambda k:k in('font-variant-numeric','font-feature-settings'),resv)
# spacing
def spacing(C,f,b,src,k,v):
    if '{{' in v: C['dynamic']+=1;return
    r=resolve(v,b['tok'])
    for t in split_vals(r):
        if t=='!important':continue
        p=px(t)
        if p is None: p=calc_eval(t)
        if p is None: C[t]+=1
        else: C[abs(p)]+=1
SP_PROPS=lambda k:k in('padding','padding-top','padding-bottom','padding-left','padding-right','padding-inline','padding-block','margin','margin-top','margin-bottom','margin-left','margin-right','margin-inline','margin-block','gap','row-gap','column-gap')
for name,pred in(('padding*',lambda k:k.startswith('padding')),('margin*',lambda k:k.startswith('margin')),('gap*',lambda k:k in('gap','row-gap','column-gap')),('ALL spacing',SP_PROPS)):
    report(name,pred,spacing,60)
# grid-fit of spacing
print('\n### spacing grid fit (numeric, non-zero)')
for t in('canon','all'):
  for bp in('m','d'):
    C=collect(SP_PROPS,t,bp,spacing)
    nums={k:v for k,v in C.items() if isinstance(k,(int,float)) and k>0}
    tot=sum(nums.values())
    for base in (2,4,8,5,3,6):
        print(t,bp,'base',base,'%.1f%%'%(100*sum(v for k,v in nums.items() if abs(k/base-round(k/base))<1e-6)/tot),end=' ; ')
    print('distinct',len(nums),'total',tot,'fraction px',sum(v for k,v in nums.items() if k!=int(k)))
# literal vs token spacing
def spmode(C,f,b,src,k,v):
    if '{{' in v: C['dynamic']+=1
    elif 'var(' in v: C['token']+=1
    else: C['literal']+=1
report('spacing token vs literal',SP_PROPS,spmode)
report('spacing tokens raw',SP_PROPS,lambda C,f,b,src,k,v:[C.__setitem__(x,C[x]+1) for x in re.findall(r'var\(--[\w-]+\)',v)],25)
# widths
report('max-width',lambda k:k=='max-width',resv,30)
report('min-width',lambda k:k=='min-width',resv,20)
report('width',lambda k:k=='width',resv,40)
report('height',lambda k:k=='height',resv,40)
report('min-height',lambda k:k=='min-height',resv,20)
report('grid-template-columns',lambda k:k=='grid-template-columns',resv,30)
report('flex (basis)',lambda k:k in('flex','flex-basis'),resv,25)
report('display',lambda k:k=='display',resv,12)
report('position',lambda k:k=='position',resv,8)
report('aspect-ratio',lambda k:k=='aspect-ratio',resv,20)
report('object-fit',lambda k:k=='object-fit',resv,5)
report('overflow',lambda k:k.startswith('overflow'),resv,8)
report('scroll-snap',lambda k:k.startswith('scroll-snap'),resv,8)
# shape
def rad(C,f,b,src,k,v):
    if '{{' in v: C['dynamic']+=1;return
    r=resolve(v,b['tok'])
    ts=split_vals(r); C[' '.join(str(px(t) if px(t) is not None else t) for t in ts)]+=1
report('border-radius resolved px',lambda k:k.startswith('border') and k.endswith('radius'),rad)
report('border-radius tokens raw',lambda k:k.startswith('border') and k.endswith('radius'),lambda C,f,b,src,k,v:C.__setitem__(v if 'var(' in v else 'LITERAL',C[v if 'var(' in v else 'LITERAL']+1),25)
def bord(C,f,b,src,k,v):
    if '{{' in v: C['dyn']+=1;return
    r=resolve(v,b['tok'])
    C[re.sub(r'\s+',' ',r)]+=1
report('border (all)',lambda k:k in('border','border-top','border-bottom','border-left','border-right'),bord,30)
report('border-width',lambda k:k.endswith('-width') and k.startswith('border'),resv,10)
report('box-shadow raw',lambda k:k=='box-shadow',lambda C,f,b,src,k,v:C.__setitem__(v[:110],C[v[:110]]+1),35)
report('opacity',lambda k:k=='opacity',resv,25)
report('z-index',lambda k:k=='z-index',resv,30)
report('backdrop-filter',lambda k:k in('backdrop-filter','-webkit-backdrop-filter'),lambda C,f,b,src,k,v:C.__setitem__(v[:50],C[v[:50]]+1),10)
report('filter',lambda k:k=='filter',lambda C,f,b,src,k,v:C.__setitem__(v[:50],C[v[:50]]+1),10)
report('background gradients',lambda k:k in('background','background-image'),lambda C,f,b,src,k,v:(C.__setitem__(v[:90],C[v[:90]]+1) if 'gradient' in v else None),18)
report('transition',lambda k:k=='transition',lambda C,f,b,src,k,v:C.__setitem__(v[:80],C[v[:80]]+1),30)
report('animation',lambda k:k=='animation',lambda C,f,b,src,k,v:C.__setitem__(v[:80],C[v[:80]]+1),20)
report('transform',lambda k:k=='transform',lambda C,f,b,src,k,v:C.__setitem__(v[:50],C[v[:50]]+1),15)
report('cursor',lambda k:k=='cursor',resv,8)
report('outline',lambda k:k.startswith('outline'),resv,10)
report('color-scheme',lambda k:k=='color-scheme',resv,5)
# rules
print('\n### Helmet selectors & media')
MQ=collections.Counter();KF=collections.Counter();PS=collections.Counter();MQc=collections.Counter();KFc=collections.Counter();PSc=collections.Counter()
for f,b in B.items():
    for ctx,s,body in b['rules']:
        for c in ctx: 
            MQ[c]+=1
            if f in CANON: MQc[c]+=1
        if s.startswith('@keyframes'):
            KF[s]+=1
            if f in CANON: KFc[s]+=1
        for p in re.findall(r'::?[a-z-]+',s):
            PS[p]+=1
            if f in CANON: PSc[p]+=1
print('media all',MQ.most_common(60));print('media canon',MQc.most_common(40))
print('keyframes all',KF.most_common(50));print('keyframes canon',KFc.most_common(50))
print('pseudos all',PS.most_common(40));print('pseudos canon',PSc.most_common(40))
print('css hover/focus rules (canon, sample)')
seen=collections.Counter()
for f,b in B.items():
    if f not in CANON: continue
    for ctx,s,body in b['rules']:
        if re.search(r':(hover|focus|active|disabled|checked)',s): seen[(s[:70],re.sub(r'\s+',' ',body)[:120])]+=1
for k,v in seen.most_common(50): print(v,k)
print('### js-driven events');
ev=collections.Counter()
for f,b in B.items():
    for e in re.findall(r'\son([A-Z][a-zA-Z]+)=',b['markup']): ev[e]+=1
print(ev.most_common())
print('### mq token overrides');
c=collections.Counter()
for f,b in B.items():
    for k,l in b['tokmq'].items():
        for ctx,v in l: c[(k,ctx,v[:40])]+=1
print(c.most_common(40))

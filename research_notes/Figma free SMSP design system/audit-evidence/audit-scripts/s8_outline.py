import sys,re,collections
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
order=['BerandaM4','RecCreateM4','SkuDetailM4','UlasanM4Salinan','ProdukIndexM4','KategoriM4','SalinanBlogM4','SalinanArtikel2M4','DesktopBerandaM4','DesktopProdukM4','DesktopSkuM4','DesktopUlasanM4','DesktopProdukIndexM4','DesktopKategoriM4','DesktopBlogM4','DesktopArtikelM4']
for n in order:
    f=n+'.dc.html';b=B[f];m=b['markup']
    print('\n=====',f,b['title'])
    ev=[]
    for mm in re.finditer(r'<(h[1-4])\b[^>]*>(.*?)</\1>|<(nav|section|aside|article|header|main|ul|table|figure)\b([^>]*)>|role="(dialog|tablist|radiogroup|region|group|log|status)"[^>]*aria-label="([^"]*)"',m,re.S):
        if mm.group(1):
            ev.append((mm.group(1)+':'+re.sub(r'<[^>]+>|\s+',' ',mm.group(2)).strip()[:60]))
        elif mm.group(3):
            al=re.search(r'aria-label="([^"]*)"',mm.group(4))
            if al or mm.group(3) in('main','section','aside'): ev.append(mm.group(3)+'['+(al.group(1)[:40] if al else '')+']')
        else: ev.append('role='+mm.group(5)+'['+mm.group(6)[:40]+']')
    print(' > '.join(ev)[:2400])
    da=collections.Counter(re.findall(r'\s(data-[\w-]+)=',m))
    print('data-*:',dict(da.most_common(30)))
    sc=b['script']
    st=re.search(r'this\.state\s*=\s*\{(.*?)\};',sc,re.S)
    keys=re.findall(r'(\w+)\s*:',st.group(1)) if st else []
    meth=re.findall(r'^\s{2}(_?\w+)\s*\([^)]*\)\s*\{',sc,re.M)
    print('state keys(%d):'%len(keys),keys[:50])
    print('methods(%d):'%len(meth),[x for x in meth if x not in('if','for','while','switch','function','catch')][:45])
    print('props:',re.search(r"data-props='(.*?)'",b['raw'],re.S).group(1)[:300] if re.search(r"data-props='(.*?)'",b['raw'],re.S) else '')

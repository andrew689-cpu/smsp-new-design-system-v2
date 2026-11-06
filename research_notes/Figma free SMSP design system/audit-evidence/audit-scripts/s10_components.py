import sys,re,collections,hashlib
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
order=['BerandaM4','RecCreateM4','SkuDetailM4','UlasanM4Salinan','ProdukIndexM4','KategoriM4','SalinanBlogM4','SalinanArtikel2M4','DesktopBerandaM4','DesktopProdukM4','DesktopSkuM4','DesktopUlasanM4','DesktopProdukIndexM4','DesktopKategoriM4','DesktopBlogM4','DesktopArtikelM4']
others=[f[:-8] for f in sorted(B) if f not in CANON]
D={ 'fraud banner':r'Waspada penipuan|WASPADA PENIPUAN','header tag':r'<header\b','search field':r'placeholder="Cari','search dialog':r'Cari di seluruh','on-screen keyboard':r'aria-label="Keyboard"','category btn':r'Buka kategori','hamburger':r'Buka menu|Opsi lainnya','footer block':r'data-kaki|kolomFooter','breadcrumb':r'Remah roti','price marker data-harga':r'data-harga','rupiah fn':r'rupiah\(|Rp','SKU price list':r'Daftar Harga','view toggle table/card':r'Tampilan daftar','filter panel':r'Filter Besi|<h3[^>]*>Filter','sort':r'Urutkan daftar','pagination':r'Halaman berikutnya','FAQ accordion':r'faqBuka','star rating':r'M8 1\.5l1\.9|bintang','review carousel':r'data-rev-card','review marquee':r'data-pita','hero/banner carousel':r'Pilih spanduk','photo gallery':r'Pilih foto','before-after':r'data-banding','WhatsApp link':r'wa\.me','help centre (bantu)':r'Pusat bantuan SMS','live chat log':r'role="log"','bottom sheet':r'data-sheet','scrim':r'data-scrim','bottom island bar':r'data-bar','desktop island':r'data-pulau','chips rail':r'data-keping-rel|data-kat-rel','segmented':r'data-seg-thumb','sticky compact header':r'data-hdr-thumb','back to top':r'keAtas','share':r'Bagikan','copy':r'disalin','calc CTA':r'[Kk]alkulator','UPVC promo':r'data-hero-upvc|Atap UPVC','sales CTA banner':r'[Kk]onsultasi|Hubungi Sales','video poster':r'youtube','partners':r'Dipercaya Mitra','related products':r'Produk Terkait','related articles':r'Artikel Terkait|Artikel Lainnya','TOC':r'Daftar isi','blockquote':r'<blockquote','data table':r'<table','range slider':r'type="range"','radio':r'type="radio"','lazy spinner':r'lazy-spin','empty state':r'Tidak ada SKU|Tidak ada|tidak ditemukan|Belum ada','toast/copied':r'role="status"|aria-live','CSAT':r'Beri nilai','form (name/wa/email)':r'type="tel"','tabs role':r'role="tab"','sektor grid':r'Cari berdasarkan Sektor','product rail':r'data-rel|Produk unggulan' }
print('component|'+'|'.join(order))
for k,rx in D.items():
    row=[]
    for n in order:
        b=B[n+'.dc.html'];t=b['markup']+b['script']+b['css']
        row.append(str(len(re.findall(rx,t))))
    print(k+'|'+'|'.join(row))
print('\nboards-present across ALL 34 per component')
for k,rx in D.items():
    print(k,sum(1 for f,b in B.items() if re.search(rx,b['markup']+b['script']+b['css'])))
print('\n## Duplication')
def norm(s): return re.sub(r'\s+',' ',s).strip()
def h(s): return hashlib.md5(norm(s).encode()).hexdigest()[:6]
snip={}
snip['header']=lambda b:re.findall(r'<header\b.*?</header>',b['markup'],re.S)
snip['fraud banner']=lambda b:re.findall(r'<div[^>]*>\s*<svg[^>]*>(?:(?!</svg>).)*</svg>\s*<p[^>]*>\s*<strong[^>]*>Waspada.*?</button>',b['markup'],re.S)
snip[':root']=lambda b:re.findall(r':root\s*\{.*?\}',b['css'],re.S)[:1]
snip['_jarakSeksi']=lambda b:re.findall(r'_jarakHitung\(atas.*?_jarakLepas\(\)\s*\{.*?\n  \}',b['script'],re.S)
snip['_jamKerja']=lambda b:re.findall(r'_jamKerja\([^)]*\)\s*\{.*?\n  \}',b['script'],re.S)
snip['help-centre']=lambda b:re.findall(r'aria-label="Pusat bantuan SMS Perkasa".*?role="log"',b['markup'],re.S)
for k,fn in snip.items():
    for tier in('canon','all'):
        C=collections.Counter();sz=[]
        for f,b in B.items():
            if tier=='canon' and f not in CANON: continue
            for s in fn(b): C[h(s)]+=1;sz.append(len(s))
        print(k,tier,'instances',sum(C.values()),'distinct',len(C),'avg_bytes',(sum(sz)//len(sz) if sz else 0),'bytes_total',sum(sz))
# line duplication across canon
lines=collections.Counter();tot=0;ub=0
for f,b in B.items():
    if f not in CANON: continue
    for l in set(norm(x) for x in re.split(r'\n',b['markup']+b['script']+b['css'])):
        if len(l)>30: lines[l]+=1
all_b=sum(len(l)*n for l,n in lines.items());uniq=sum(len(l) for l in lines)
shared=sum(len(l)*n for l,n in lines.items() if n>1)
print('canon line dup: total bytes(>30ch lines)',all_b,'unique',uniq,'bytes in lines shared by >=2 boards',shared,'%.1f%%'%(100*shared/all_b))
print('\n## half-gutter calc() counts (canon)')
for bp in('m','d'):
    C=collections.Counter()
    for f,b in B.items():
        if f in CANON and b['bp']==bp:
            for src,s,ctx,k,v in b['recs']:
                if k.startswith('margin') or k in('gap','row-gap','column-gap'):
                    if 'calc(' in v: C[k.split('-')[0]+':'+v]+=1
    print(bp,C.most_common(20))
print('\n## literal marginL/R pairs equal (half gutter literal) canon')
for bp in('m','d'):
    C=collections.Counter()
    for f,b in B.items():
        if f in CANON and b['bp']==bp:
            for st in re.findall(r'\bstyle="([^"]*)"',b['markup']):
                d=dict(decls(st))
                ml,mr=d.get('margin-left'),d.get('margin-right')
                if ml and ml==mr:
                    r=resolve(ml,b['tok'])
                    p=px(r) if px(r) is not None else calc_eval(r)
                    C['gutter %s'%(p*2 if p is not None else r)]+=1
                mt,mb=d.get('margin-top'),d.get('margin-bottom')
                if mt and mt==mb:
                    r=resolve(mt,b['tok'])
                    p=px(r) if px(r) is not None else calc_eval(r)
                    C['Ygutter %s'%(p*2 if p is not None else r)]+=1
    print(bp,C.most_common(30))
print('\n## Button recipes: elements with filled background (canon)')
R=collections.Counter()
for f,b in B.items():
    if f not in CANON: continue
    for tag,attrs in re.findall(r'<(button|a)\b([^>]*)>',b['markup']):
        st=re.search(r'style="([^"]*)"',attrs)
        if not st: continue
        d=dict(decls(st.group(1)))
        bg=d.get('background') or d.get('background-color')
        if not bg or bg in('transparent','none'): continue
        key=(b['bp'],tag,bg[:24],d.get('color','-')[:16],d.get('height') or d.get('min-height') or '-',d.get('border-radius','-'),d.get('font-size','-'),d.get('font-weight','-'))
        R[key]+=1
for k,v in R.most_common(40): print(v,k)
print('\n## price samples')
for n in('RecCreateM4','DesktopProdukM4','SkuDetailM4','BerandaM4'):
    b=B[n+'.dc.html']
    for mm in list(re.finditer(r'<[a-z]+\b[^>]*data-harga[^>]*>',b['markup']))[:2]:
        print(n,mm.group(0)[:300],'...',re.sub(r'\s+',' ',b['markup'][mm.end():mm.end()+420]))
for f in ('RecCreateM4.dc.html','DesktopProdukM4.dc.html'):
    print(f,'data-harga css:',[ (s,re.sub(r'\s+',' ',bd)[:160]) for ctx,s,bd in B[f]['rules'] if 'harga' in s][:4])
print('\n## price colours: Rp context')
c=collections.Counter()
for f,b in B.items():
    if f in CANON:
        for mm in re.finditer(r'style="([^"]*)"[^>]*>\s*(?:<[^>]+>)*\s*Rp',b['markup']):
            d=dict(decls(mm.group(1)));c[(d.get('color','-'),d.get('font-size','-'),d.get('font-weight','-'))]+=1
print(c.most_common(20))
print('\n## domain data')
ALL=''.join(b['markup']+b['script'] for b in B.values())
print('Rp samples',collections.Counter(re.findall(r'Rp\s?[\d.,]+',ALL)).most_common(15))
print('wa.me',collections.Counter(re.findall(r'wa\.me/[0-9]*',ALL)).most_common(6))
print('units',{u:len(re.findall(r'/\s?'+u+r'\b',ALL)) for u in['btg','kg','m','lbr','pcs','batang','roll']})
print('tel',collections.Counter(re.findall(r'(?:\+62|021|08)[\d\s-]{6,}',ALL)).most_common(6))
print('longest visible strings (markup text)')
txt=[]
for f,b in B.items():
    if f in CANON:
        t=re.sub(r'<svg.*?</svg>','',b['markup'],flags=re.S)
        for s in re.findall(r'>([^<>{}]{50,})<',t): txt.append(norm(s))
print(len(txt));print([s[:160] for s in sorted(set(txt),key=len,reverse=True)[:5]])

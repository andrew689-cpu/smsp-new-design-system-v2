import sys,re,collections
sys.path.insert(0,sys.argv[2])
from parse import *
B,canvas=load_all(sys.argv[1])
def vis(b):
    return re.sub(r'<svg.*?</svg>','',b['markup'],flags=re.S)+b['script']
for name,rx in [('cart',r'[Kk]eranjang|[Cc]heckout|\bcart\b'),('account',r'[Ll]ogin|Masuk ke akun|Daftar akun|[Kk]ata sandi'),('error',r'[Gg]agal|[Cc]oba lagi|\berror\b|Terjadi kesalahan'),('stock',r'[Ss]tok|[Hh]abis|Hubungi untuk harga|harga hubungi'),('pdf/print',r'\bPDF\b|[Cc]etak|window\.print|Unduh'),('skeleton',r'[Ss]keleton'),('toast',r'[Tt]oast'),('checkbox',r'type="checkbox"'),('switch',r'role="switch"'),('tooltip',r'role="tooltip"|[Tt]ooltip'),('focus()',r'\.focus\('),('Tab key',r"'Tab'|\"Tab\""),('Escape',r"'Escape'"),('aria-modal',r'aria-modal'),('validation msg',r'[Ww]ajib diisi|tidak valid|Format .* salah'),('prefers-color-scheme',r'prefers-color-scheme'),('title attr',r'\stitle="')]:
    canon=[f[:-8] for f,b in B.items() if f in CANON and re.search(rx,vis(b)+b['css'])]
    n=sum(len(re.findall(rx,vis(b)+b['css'])) for f,b in B.items() if f in CANON)
    al=sum(1 for b in B.values() if re.search(rx,vis(b)+b['css']))
    ex=''
    for f,b in B.items():
        if f in CANON:
            m=re.search(rx,vis(b))
            if m: ex=re.sub(r'\s+',' ',vis(b)[max(0,m.start()-60):m.end()+60]);break
    print(name,'canon_hits',n,'canon_boards',len(canon),'all_boards',al,'| ex:',ex[:170])
print('--- desktop produk diff ops')

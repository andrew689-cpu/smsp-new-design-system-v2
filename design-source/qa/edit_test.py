#!/usr/bin/env python3
"""Simulate real component edits on a temp copy and count which screens pick them up.

Each edit plants a unique marker. A text edit is 'reached' when the marker text renders.
A style edit is 'reached' when an element renders with the marker color.
"""
import collections
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
LIVE = SCRATCH / "workspace/project"
TMP = SCRATCH / "qa/edit-tmp"
canvas = json.load(open(SCRATCH / "workspace/project/canvas.json", encoding="utf-8"))
screens = sorted(k[:-8] for k, v in canvas["boards"].items() if v.get("page") == "salinan4")
if TMP.exists():
    shutil.rmtree(TMP)
shutil.copytree(LIVE, TMP)

ORIG = {}


def edit(comp, old, new, count=0):
    p = TMP / f"{comp}.dc.html"
    t = p.read_text("utf-8")
    n = t.count(old)
    if not n:
        print(f"!! {comp}: '{old[:40]}' not found")
        return 0
    p.write_text(t.replace(old, new) if not count else t.replace(old, new, count), "utf-8")
    return n


# Text edits: the kind of thing a person changes in a component.
TEXT = [
    ("FraudRibbon", "Waspada penipuan", "ZZRIBBOND"),
    ("Footer", "Kalkulator Material", "ZZFOOTM"),
    ("Footer", "Bantuan dan FAQ", "ZZFOOTD"),
    ("Footer", "Kebijakan Privasi", "ZZFOOTP"),
    ("CategoryNav", "Semua Produk", "ZZNAV"),
    ("ConsultationBanner", "Konsultasi Sekarang", "ZZKONSUL"),
    ("Price", "per batang", "ZZUNIT"),
    ("ProductSummary", "Lihat Selengkapnya", "ZZMORE"),
]
print("--- where each text lives (files containing it, comments excluded)")
for needle in ["Waspada penipuan", "Kalkulator Material", "Bantuan dan FAQ", "Kebijakan Privasi", "Hati-hati Penipuan", "Konsultasi Sekarang", "per batang", "Lihat Selengkapnya", "Lokasi Gudang", "hati-hati-penipuan", "+628112689889", "sales@smsperkasa.com", "Jl. BKR Pelajar 51"]:
    files = [p.stem.replace(".dc", "") for p in LIVE.glob("*.dc.html") if needle in re.sub(r"<!--.*?-->", "", p.read_text("utf-8"), flags=re.S) and not p.name.startswith("Sheet")]
    sc = [f for f in files if f in screens]
    co = [f for f in files if f not in screens]
    print(f"  {needle:26s} {len(sc):2d} screens, components: {co}")

for c, a, b in TEXT:
    edit(c, a, b)

# Style edits: the root color of components, using a color no design uses.
MARK = {"Price": "rgb(1, 2, 3)", "Heading": "rgb(4, 5, 6)", "Button": "rgb(7, 8, 9)"}
pt = TMP / "Price.dc.html"
t = pt.read_text("utf-8")
pt.write_text(t.replace('data-harga="{{ dataHarga }}" style="', 'data-harga="{{ dataHarga }}" style="color: rgb(1, 2, 3) !important; '), "utf-8")
ph = TMP / "Heading.dc.html"
t = ph.read_text("utf-8")
ph.write_text(re.sub(r'(<h[123]\b[^>]*?style=")', r"\1outline: 1px solid rgb(4, 5, 6); ", t), "utf-8") if re.search(r'<h[123]\b[^>]*?style="', t) else None
pb = TMP / "Button.dc.html"
t = pb.read_text("utf-8")
pb.write_text(t.replace("const dasar = '", "const dasar = 'outline: 1px solid rgb(7, 8, 9); "), "utf-8")
pi = TMP / "Icon.dc.html"
t = pi.read_text("utf-8")
pi.write_text(t.replace('<svg ', '<svg data-edit-icon="1" '), "utf-8")
pl = TMP / "Footer.dc.html"
t = pl.read_text("utf-8")
print("Footer root sample:", re.search(r"<(footer|div)\b[^>]*>", t.split("</helmet>")[-1]).group(0)[:120])

js = r"""
const http=require('http'),fs=require('fs'),path=require('path');
const {createRequire}=require('module');const {execSync}=require('child_process');
const req=createRequire(path.join(execSync('npm root -g').toString().trim(),'@playwright/cli/package.json'));
const {chromium}=req('playwright');
const [dir,screensFile,outFile]=process.argv.slice(2);const screens=JSON.parse(fs.readFileSync(screensFile,'utf8'));
const real=process.env.REAL_IMAGES;const M={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.svg':'image/svg+xml'};
const sv=http.createServer((q,s)=>{const u=decodeURIComponent(q.url.split('?')[0]);
 if(u.endsWith('/support.js')){s.writeHead(200,{'content-type':M['.js']});return s.end(fs.readFileSync(process.env.DC_RUNTIME));}
 const b=u.match(/\/_blob\/([0-9a-f]+)/);if(b){const h=fs.readdirSync(real).find(f=>f.startsWith(b[1]+'.'));if(h){s.writeHead(200,{'content-type':M[path.extname(h)]});return s.end(fs.readFileSync(path.join(real,h)));}s.writeHead(404);return s.end('');}
 const f=path.join(dir,u.replace(/^\/+/,''));if(!fs.existsSync(f)||fs.statSync(f).isDirectory()){s.writeHead(404);return s.end('');}
 s.writeHead(200,{'content-type':M[path.extname(f)]||'application/octet-stream'});s.end(fs.readFileSync(f));});
(async()=>{await new Promise(r=>sv.listen(0,'127.0.0.1',r));const port=sv.address().port;const br=await chromium.launch();const out={};let i=0;
async function w(){while(i<screens.length){const b=screens[i++];const W=/^Desktop/.test(b)?1440:360;const c=await br.newContext({viewport:{width:W,height:W===360?800:900},reducedMotion:'reduce'});const p=await c.newPage();
 await p.goto(`http://127.0.0.1:${port}/${b}.dc.html`,{waitUntil:'load',timeout:60000});await p.waitForTimeout(3000);
 out[b]=await p.evaluate(()=>{const vis=e=>{const s=getComputedStyle(e);const r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;};
  const text=document.body.innerText;const own=e=>{const h=e.closest('[data-sc-name]');return h?h.getAttribute('data-sc-name'):'?';};
  const zz={};(text.match(/ZZ[A-Z]+/g)||[]).forEach(z=>zz[z]=(zz[z]||0)+1);
  const pr={};let prT=0,prE=0;document.querySelectorAll('[data-harga]').forEach(e=>{if(!vis(e)||!e.textContent.trim())return;prT++;if(getComputedStyle(e).color==='rgb(1, 2, 3)')prE++;else{const o=own(e);pr[o]=(pr[o]||0)+1;}});
  const hd={};let hT=0,hE=0;document.querySelectorAll('h1,h2,h3').forEach(e=>{if(!vis(e))return;hT++;if(getComputedStyle(e).outlineColor==='rgb(4, 5, 6)'&&getComputedStyle(e).outlineStyle==='solid')hE++;else{const o=own(e);hd[o]=(hd[o]||0)+1;}});
  let ic=0,icT=0;const ico={};document.querySelectorAll('svg').forEach(e=>{if(!vis(e))return;icT++;if(e.hasAttribute('data-edit-icon'))ic++;else{const o=own(e);ico[o]=(ico[o]||0)+1;}});
  const bt=[...document.querySelectorAll('a,button')].filter(e=>vis(e)&&getComputedStyle(e).outlineColor==='rgb(7, 8, 9)'&&getComputedStyle(e).outlineStyle==='solid').length;
  const remain=['Kalkulator Material','Bantuan dan FAQ','Kebijakan Privasi','Waspada penipuan','Konsultasi Sekarang','per batang','Lihat Selengkapnya'].filter(x=>text.toLowerCase().includes(x.toLowerCase()));
  return {zz,prT,prE,pr,hT,hE,hd,icT,ic,ico,bt,remain};});
 await c.close();}}
await Promise.all(Array.from({length:6},w));fs.writeFileSync(outFile,JSON.stringify(out));await br.close();sv.close();})();
"""
(SCRATCH / "qa/edit_run.cjs").write_text(js)
sl, ol = SCRATCH / "qa/e-screens.json", SCRATCH / "qa/e-out.json"
json.dump(screens, open(sl, "w"))
env = {**os.environ, "DC_RUNTIME": str(SCRATCH / "runtime/dc-runtime.js"), "REAL_IMAGES": str(SCRATCH / "images")}
subprocess.run(["node", str(SCRATCH / "qa/edit_run.cjs"), str(TMP), str(sl), str(ol)], env=env, check=True, timeout=500)
r = json.load(open(ol))

print("\n--- text edits made INSIDE the component: screens where the new text renders")
names = {"ZZRIBBOND": "FraudRibbon text", "ZZFOOTM": "Footer 'Kalkulator Material'", "ZZFOOTD": "Footer 'Bantuan dan FAQ'", "ZZFOOTP": "Footer 'Kebijakan Privasi'", "ZZNAV": "'Semua Produk' in header", "ZZKONSUL": "'Konsultasi Sekarang'", "ZZUNIT": "Price 'per batang'", "ZZMORE": "'Lihat Selengkapnya'"}
for z, label in names.items():
    hit = [s for s in screens if z in r[s]["zz"]]
    print(f"  {label:32s} reached {len(hit):2d} screens")
print("  Old text still rendering after the component edit:")
rem = collections.Counter(x for s in screens for x in r[s]["remain"])
for k, v in rem.most_common():
    print(f"    '{k}' still on {v} screens: {[s for s in screens if k in r[s]['remain']][:7]}")

print("\n--- style edit to Price: visible price text that changed")
tot = sum(r[s]["prT"] for s in screens)
ok = sum(r[s]["prE"] for s in screens)
own = collections.Counter()
for s in screens:
    own.update(r[s]["pr"])
print(f"  {ok}/{tot} changed. Not changed, by owner: {own.most_common()}")
print("  screens where some price did not change:", {s: r[s]["pr"] for s in screens if r[s]["pr"]})

print("\n--- style edit to Heading: visible headings that changed")
tot = sum(r[s]["hT"] for s in screens)
ok = sum(r[s]["hE"] for s in screens)
own = collections.Counter()
for s in screens:
    own.update(r[s]["hd"])
print(f"  {ok}/{tot} changed. Not changed, by owner: {own.most_common()}")

print("\n--- edit to Icon: visible icons that changed")
tot = sum(r[s]["icT"] for s in screens)
ok = sum(r[s]["ic"] for s in screens)
own = collections.Counter()
for s in screens:
    own.update(r[s]["ico"])
print(f"  {ok}/{tot} changed. Not changed, by owner (Logo is expected): {own.most_common()}")
print("  by screen:", {s: r[s]["ico"] for s in screens if set(r[s]["ico"]) - {"Logo"}})

print("\n--- style edit to Button: screens with Button instances that changed")
print("  ", {s: r[s]["bt"] for s in screens})
shutil.rmtree(TMP)
price_ok = sum(r[s]["prE"] for s in screens) == sum(r[s]["prT"] for s in screens)
head_ok = sum(r[s]["hE"] for s in screens) == sum(r[s]["hT"] for s in screens)
icon_rest = collections.Counter()
for s in screens:
    icon_rest.update(r[s]["ico"])
icon_ok = set(icon_rest) <= {"Logo"}
ok = price_ok and head_ok and icon_ok
print("\nREACH", "PASS" if ok else "FAIL", {"Price": price_ok, "Heading": head_ok, "Icon": icon_ok})
sys.exit(0 if ok else 1)

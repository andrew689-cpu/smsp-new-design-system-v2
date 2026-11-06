#!/usr/bin/env python3
"""Audit: does an edit to a component reach every screen? Read-only.

Usage: python3 audit.py <live project dir> <published local dir> <canvas.json>
"""
import collections
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

live, local = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
canvas = json.load(open(sys.argv[3], encoding="utf-8"))
SCRATCH = pathlib.Path(__file__).resolve().parent.parent
screens = sorted(k[:-8] for k, v in canvas["boards"].items() if v.get("page") == "salinan4")
docs = {"DocSpec", "Colors", "FontSizes", "IconSheet"}


def nocomment(t):
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)


def read(name):
    return nocomment((live / f"{name}.dc.html").read_text("utf-8"))


print("=== A. live vs what I published")
changed = []
for p in sorted(live.glob("*")):
    q = local / p.name
    if not q.exists():
        changed.append((p.name, "not in my copy"))
    elif p.read_bytes() != q.read_bytes():
        changed.append((p.name, f"{q.stat().st_size} -> {p.stat().st_size} bytes"))
print("files differing:", changed or "none")

comps = sorted(p.name[:-8] for p in live.glob("*.dc.html") if p.name[:-8] not in screens and not p.name.startswith("Sheet"))
imp = {}
for n in screens + comps:
    tpl = read(n)
    names = set(re.findall(r'<dc-import\b[^>]*\bname="([^"{]+)"', tpl))
    # Components imported indirectly through a prop, such as Rail komponen="CategoryTile".
    names |= set(re.findall(r'\bkomponen="([A-Z][A-Za-z]+)"', tpl))
    names |= {m for m in re.findall(r"komponen\s*[:=]\s*'([A-Z][A-Za-z]+)'", tpl)}
    imp[n] = names


def closure(n, seen=None):
    seen = seen if seen is not None else set()
    for c in imp.get(n, ()):
        if c not in seen:
            seen.add(c)
            closure(c, seen)
    return seen


print("\n=== B. static import graph")
reach = {s: closure(s) for s in screens}
used_by = collections.Counter(c for s in screens for c in reach[s])
print("screens with zero imports:", [s for s in screens if not imp[s]])
print("component count:", len(comps))
print("reached by NO screen:", sorted(c for c in comps if not used_by[c] and c not in docs))
print("most shared:", used_by.most_common(14))

print("\n=== C. runtime: marker planted in every component file")
env = {**os.environ, "DC_RUNTIME": str(SCRATCH / "runtime/dc-runtime.js"),
       "REAL_IMAGES": str(SCRATCH / "images")}
sl, ol = SCRATCH / "qa/a-screens.json", SCRATCH / "qa/a-runtime.json"
json.dump(screens, open(sl, "w"))
subprocess.run(["node", str(SCRATCH / "qa/audit_runtime.cjs"), str(live), str(sl), str(ol)], env=env, check=True, timeout=500)
rt = json.load(open(ol))
print("screen                       comps-rendered  text-in-components  text-on-screen-itself  errors")
for s in screens:
    r = rt[s]
    names = [k for k in r["probes"]]
    print(f"{s:32s}{len(names):4d}{r['compText']:10d}{r['rootText']:10d}   {r['errors'][:1] or ''}")
missing = {s: sorted(set(rt[s]["hosts"]) - set(rt[s]["probes"]) - {rt[s]["rootName"]}) for s in screens}
print("rendered component whose marker did NOT arrive:", {k: v for k, v in missing.items() if v} or "none")
seen_runtime = set(k for s in screens for k in rt[s]["probes"])
print("components that render on at least one screen by default:", len(seen_runtime))
print("reachable but closed by default (overlays, branches):", sorted(set(used_by) - seen_runtime))

print("\n=== D. who owns each visible element, all 34 screens, default state")


def agg(key):
    c = collections.Counter()
    for s in screens:
        c.update(rt[s][key])
    return c


for key, ok, label in [("svg", {"Icon", "Logo"}, "icons (svg)"), ("button", {"Button", "IconButton", "GlassButton", "Chip", "Segmented", "Accordion"}, "buttons"),
                       ("input", {"TextField", "SearchField", "Radio"}, "inputs"), ("heading", {"Heading"}, "headings"), ("harga", {"Price"}, "price text")]:
    c = agg(key)
    tot = sum(c.values())
    good = sum(v for k, v in c.items() if k in ok)
    bad = [(k, v) for k, v in c.most_common() if k not in ok][:12]
    print(f"{label}: {good}/{tot} inside {sorted(ok)} ({100*good/max(tot,1):.0f}%). Outside: {bad}")

print("\n=== E. local copies inside component files (static, all states)")
ATOMS = {"Icon", "Logo", "Button", "IconButton", "GlassButton", "Chip", "Tag", "Heading", "TextField", "SearchField", "Radio", "Rating", "Spinner", "Segmented", "Price"}
rows = []
for c in comps:
    if c in docs:
        continue
    t = read(c)
    tpl = t.split("<x-dc>")[-1].split("</x-dc>")[0]
    row = {"svg": len(re.findall(r"<svg\b", tpl)) if c not in {"Icon", "Logo", "Rating"} else 0,
           "button": len(re.findall(r"<button\b", tpl)) if c not in ATOMS else 0,
           "heading": len(re.findall(r"<h[1-4]\b", tpl)) if c != "Heading" else 0,
           "harga": len(re.findall(r"data-harga", tpl)) if c != "Price" else 0,
           "input": len(re.findall(r"<input\b", tpl)) if c not in {"TextField", "SearchField", "Radio", "Chip", "Segmented"} else 0}
    if sum(row.values()):
        rows.append((sum(row.values()), c, row, used_by[c]))
for tot, c, row, u in sorted(rows, key=lambda r: -r[0])[:24]:
    print(f"  {c:22s} {tot:3d} local copies on {u:2d} screens  {({k: v for k, v in row.items() if v})}")
print("components containing local copies:", len(rows), "of", len(comps))

print("\n=== F. values that bypass tokens")
col = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\([^)]*\)|\bhsla?\([^)]*\)")
cl = []
for c in comps:
    if c in docs or c in {"Icon", "SocialLoginButtons"}:
        continue
    t = read(c)
    vals = [v for v in col.findall(t.split("<x-dc>")[-1].split("</body>")[0]) if not re.match(r"#(bab|kat|whatsapp|m-|produk)", v)]
    if vals:
        cl.append((len(vals), c, collections.Counter(vals).most_common(2)))
print("components with literal colors:", len(cl), sorted(cl, key=lambda x: -x[0])[:12])
fs = []
for c in comps:
    if c in docs:
        continue
    t = read(c)
    lit = [v.strip() for v in re.findall(r"font-size:\s*([^;\"'{]+)", t) if "var(" not in v and v.strip() and "inherit" not in v]
    if lit:
        fs.append((len(lit), c, collections.Counter(lit).most_common(2)))
print("components with literal font sizes:", len(fs), sorted(fs, key=lambda x: -x[0])[:10])
over = {}
for s in screens:
    raw = (live / f"{s}.dc.html").read_text("utf-8")
    tpl = raw.split("<x-dc>")[-1].split("</x-dc>")[0]
    o = sorted(set(re.findall(r"(?:^|[;\"\s])(--[\w-]+)\s*:", tpl)))
    if o:
        over[s] = o
print("screens overriding tokens locally:", over or "none")

print("\n=== G. content repeated in screens instead of living in a component")
blocks = collections.defaultdict(set)
for s in screens:
    raw = read(s)
    js = raw.split("data-dc-script")[-1]
    for m in re.finditer(r"(?:const|var|let)\s+([A-Z_a-z]+)\s*=\s*\[|([a-zA-Z]+)\s*:\s*\[", js):
        name = m.group(1) or m.group(2)
        i = m.end() - 1
        d, k, q = 0, i, None
        while k < len(js):
            ch = js[k]
            if q:
                if ch == "\\":
                    k += 1
                elif ch == q:
                    q = None
            elif ch in "'\"`":
                q = ch
            elif ch == "[":
                d += 1
            elif ch == "]":
                d -= 1
                if d == 0:
                    break
            k += 1
        body = js[i:k + 1]
        if len(body) < 60:
            continue
        h = hashlib.md5(re.sub(r"\s+", "", body).encode()).hexdigest()[:8]
        blocks[(name, h)].add(s)
rep = sorted(((len(v), k[0], len(k[1]), k[1]) for k, v in blocks.items() if len(v) >= 2), reverse=True)
byname = collections.defaultdict(set)
for k, v in blocks.items():
    byname[k[0]] |= v
print("identical data blocks copied across screens:")
for n, name, _, h in rep[:24]:
    print(f"  {name:18s} identical on {n} screens")
variants = {k: sum(1 for kk in blocks if kk[0] == k) for k in ("FOOT_CATS", "FOOT_INFO", "SOSIAL", "KOLOM", "kolomFooter", "navTautan", "ULASAN", "MITRA", "KATEGORI", "BANNER", "UNGGULAN")}
print("distinct versions of each block (more than 1 = screens already differ):", {k: v for k, v in variants.items() if v})
print("screens holding each block:", {k: len(byname[k]) for k in variants if byname[k]})
attrs = collections.defaultdict(lambda: collections.defaultdict(set))
for s in screens:
    for comp, body in re.findall(r'<dc-import\b[^>]*?\bname="([^"]+)"([^>]*)>', read(s)):
        for a, v in re.findall(r'([a-zA-Z-]+)="([^"{]+)"', body):
            if a not in ("hint-size", "name", "tata", "style"):
                attrs[(comp, a)][v].add(s)
print("the same literal prop written on many screens:")
ra = sorted(((len(ss), c, a, v) for (c, a), vs in attrs.items() for v, ss in vs.items() if len(ss) >= 6), reverse=True)[:16]
for n, c, a, v in ra:
    print(f"  {c}.{a}=\"{v[:44]}\" on {n} screens")

print("\n=== H. variant branches: an edit to one branch does not reach the others")
for c, pat in [("Button", r"variant"), ("ProductCard", r"jenis"), ("Heading", r"varian"), ("Chip", r"jenis"), ("BlogRow", r"jenis"), ("Price", r"ukuran"), ("IconButton", r"bentuk")]:
    t = read(c)
    opts = re.search(rf'"{pat}":\{{"editor":"enum","options":\[([^\]]*)\]', t)
    n = len(re.findall(r'"([^"]+)"', opts.group(1))) if opts else "?"
    print(f"  {c}: {n} declared values of {pat}")
lama = collections.defaultdict(list)
for c in comps + screens:
    t = read(c)
    if re.search(r"\blama\b", t):
        lama[c] = len(re.findall(r"\blama\b", t))
print("files mentioning the legacy 'lama' branch:", dict(lama))
for s in ("RecCreateM4Salinan1", "SalinanProdukPageM4", "SalinanSkuPageM4", "RecCreateM4", "SkuDetailM4"):
    t = read(s)
    style_hits = len(re.findall(r"(?:background|color|box-shadow|border|font-size)[:\s]", t.split("data-dc-script")[-1]))
    print(f"  {s}: screen {len(t)//1024} KB, logic style strings {style_hits}")
hs = []
for c in comps:
    tpl = read(c).split("<x-dc>")[-1].split("</x-dc>")[0]
    n = len(re.findall(r'style="\s*\{\{[^}]+\}\}\s*"', tpl))
    if n:
        hs.append((n, c))
print("\n=== I. visual-panel editing risk: elements whose whole style is computed in JS")
print("components:", len(hs), "of", len(comps), "| elements:", sum(n for n, _ in hs), "| top:", sorted(hs, reverse=True)[:10])

#!/usr/bin/env python3
"""Repack sheets by real height and write canvas.json from the live index.

Usage: python3 final_layout.py <live canvas.json>
Writes sheet parts, canvas.json and publish-files.json in the workspace. Takes a few minutes.
"""
import json
import os
import pathlib
import re
import subprocess
import sys

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
ROOT = SCRATCH / "workspace"
PROJECT = ROOT / "project"
MAX_H = 8000
CAP = 7500
env = {**os.environ, "DC_RUNTIME": str(SCRATCH / "runtime/dc-runtime.js"),
       "REAL_IMAGES": str(SCRATCH / "images")}


def measure(items):
    lst, out = SCRATCH / "qa/m-list.json", SCRATCH / "qa/m-out.json"
    json.dump(items, open(lst, "w"))
    subprocess.run(["node", str(SCRATCH / "qa/measure.cjs"), str(PROJECT), str(lst), str(out)], env=env, check=True, timeout=560)
    return json.load(open(out))


live = json.load(open(sys.argv[1], encoding="utf-8"))
screens = {f for f, v in live["boards"].items() if v.get("page") == "salinan4"}
stems = ["SheetAtoms", "SheetShell", "SheetCommerce", "SheetContent", "SheetHelp"]


def parts_of(stem):
    return sorted(PROJECT.glob(f"{stem}[0-9]*.dc.html"), key=lambda p: int(re.search(r"(\d+)\.dc\.html$", p.name).group(1)))


def section_spans(tpl, start):
    spans, depth, begin = [], 0, None
    for m in re.finditer(r"<section\b|</section>", tpl[start:]):
        pos = m.start() + start
        if m.group(0) == "<section":
            if depth == 0:
                begin = pos
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                spans.append((begin, pos + len("</section>")))
    return spans


removed = []
heights = measure([{"board": p.name[:-8], "w": 1200} for s in stems for p in parts_of(s)])
for stem in stems:
    files = parts_of(stem)
    sections, sec_h = [], []
    head = tail = pre = closing = None
    for pf in files:
        raw = pf.read_text("utf-8")
        h_, rest = raw.split("<x-dc>", 1)
        tpl, t_ = rest.split("</x-dc>", 1)
        start = tpl.index('<div style="width: 1200px')
        spans = section_spans(tpl, start)
        if head is None:
            head, tail = h_, t_
            pre = tpl[: spans[0][0]]
            closing = tpl[spans[-1][1]:]
        got = heights[pf.name[:-8]].get("sections", [])
        if len(got) != len(spans):
            sys.exit(f"{pf.name}: measured {len(got)} sections, found {len(spans)}")
        sections += [tpl[a:b] for a, b in spans]
        sec_h += got
    packs, cur, cur_h = [], [], 200
    for s, sh in zip(sections, sec_h):
        if cur and cur_h + sh + 48 > CAP:
            packs.append(cur)
            cur, cur_h = [], 200
        cur.append(s)
        cur_h += sh + 48
    packs.append(cur)
    for i, secs in enumerate(packs, 1):
        suffix = f" · bagian {i} dari {len(packs)}"
        p2 = re.sub(r" · bagian \d+ dari \d+", suffix, pre)
        new = head + "<x-dc>" + p2 + "\n\n".join(secs) + "\n" + closing.lstrip("\n") + "</x-dc>" + tail
        new = re.sub(r" · bagian \d+ dari \d+", suffix, new, count=1) if "<title>" not in new else re.sub(r"(<title>.*?)( · bagian \d+ dari \d+)(</title>)", rf"\g<1>{suffix}\g<3>", new, count=1)
        (PROJECT / f"{stem}{i}.dc.html").write_text(new, "utf-8")
    for pf in files[len(packs):]:
        pf.unlink()
        removed.append(pf.name)
    print(stem, "sections", len(sections), "parts", len(packs), "largest section", max(map(round, sec_h)))

manifest_names = ["atoms", "shell", "commerce", "content", "help", "props-atoms", "refactor-katalog", "refactor-artikel", "refactor-beranda", "refactor-harga", "refactor-blog", "refactor-sku", "props-content", "props-screens", "props-harga", "learning"]
groups, seen = {}, set()
for n in manifest_names:
    mp = ROOT / "_manifests" / f"{n}.json"
    if not mp.exists():
        print("no manifest:", n)
        continue
    for b in json.load(open(mp, encoding="utf-8"))["boards"]:
        if b.get("kind") == "sheet" or b["file"] in seen or b["file"] in screens or not (PROJECT / b["file"]).exists():
            continue
        seen.add(b["file"])
        groups.setdefault(n, []).append(b)
groups.setdefault("atoms", []).append({"file": "DocSpec.dc.html", "title": "DocSpec · alat dokumentasi", "w": 240, "h": 60})
seen.add("DocSpec.dc.html")

sheet_files = ["Colors.dc.html", "FontSizes.dc.html", "IconSheet.dc.html", "SheetPriceList.dc.html"] + [p.name for s in stems for p in parts_of(s)]
disk = {p.name for p in PROJECT.glob("*.dc.html")}
orphans = sorted(disk - screens - seen - set(sheet_files))
if orphans:
    print("on disk with no manifest, added to Seksi halaman:", orphans)
    for f in orphans:
        groups.setdefault("refactor-lain", []).append({"file": f, "title": f[:-8], "w": 360, "h": 200})
        seen.add(f)

items = [{"board": f[:-8], "w": 1200} for f in sheet_files] + [{"board": b["file"][:-8], "w": b["w"]} for bs in groups.values() for b in bs]
real = measure(items)
bad = {k: (v.get("error") or v.get("errors")) for k, v in real.items() if v.get("error") or v.get("errors")}
print("boards with runtime errors:", bad)

canvas = live
PAGE = "components"
for f in [k for k, v in canvas["boards"].items() if v.get("page") == PAGE]:
    del canvas["boards"][f]
canvas["order"] = [f for f in canvas["order"] if f in canvas["boards"]]
for key in [k for k, v in canvas["notes"].items() if v.get("page") == PAGE]:
    del canvas["notes"][key]


def fit(f, fallback):
    h = real.get(f[:-8], {}).get("height") or fallback
    return max(40, min(MAX_H, int(h) + 2))


def add(f, title, x, y, w, h, inter=False):
    e = {"title": title, "page": PAGE, "x": x, "y": y, "w": max(40, min(MAX_H, w)), "h": h}
    if inter:
        e["is_interactive"] = True
    canvas["boards"][f] = e
    canvas["order"].append(f)


def note(key, text, x, y, max_w):
    canvas["notes"][key] = {"kind": "title1", "page": PAGE, "text": text, "x": x, "y": y, "maxW": max_w}


SHEET_TITLES = {"SheetAtoms": "Pecahan · Komponen kecil", "SheetShell": "Pecahan · Kerangka", "SheetCommerce": "Pecahan · Katalog", "SheetContent": "Pecahan · Konten", "SheetHelp": "Pecahan · Bantuan"}
base = {"Colors.dc.html": "Fondasi · Warna", "FontSizes.dc.html": "Fondasi · Ukuran huruf", "IconSheet.dc.html": "Fondasi · Ikon", "SheetPriceList.dc.html": "Pecahan · Baris harga dan tombol"}
x, tallest = 0, 0
for f in sheet_files:
    h = fit(f, 2000)
    m = re.match(r"(Sheet[A-Za-z]+)(\d+)\.dc\.html", f)
    title = base.get(f) or f"{SHEET_TITLES[m.group(1)]} {m.group(2)}"
    add(f, title, x, 0, 1200, h, f.startswith("Sheet"))
    x += 1280
    tallest = max(tallest, h)
note("n-components-pecahan", "Fondasi dan lembar pecahan", 0, -300, x - 80)

TITLES = {"atoms": "Komponen kecil", "shell": "Kerangka dan navigasi", "commerce": "Katalog dan harga", "content": "Ulasan, beranda, blog, artikel", "help": "Pusat bantuan"}
y = tallest + 500
WRAP = 5200
order = ["atoms", "shell", "commerce", "content", "help"]
page_groups = [g for g in groups if g not in order]
band = [(g, TITLES[g]) for g in order if g in groups] + [("__seksi", "Seksi halaman")]
for key, title in band:
    bs = groups.get(key, []) if key != "__seksi" else [b for g in page_groups for b in groups[g]]
    if not bs:
        continue
    note(f"n-components-{key.strip('_')}", title, 0, y, WRAP)
    cx, cy, row = 0, y + 300, 0
    for b in bs:
        w, h = max(40, min(MAX_H, b["w"])), fit(b["file"], b["h"])
        if cx and cx + w > WRAP:
            cx, cy, row = 0, cy + row + 120, 0
        add(b["file"], b["title"], cx, cy, w, h, bool(b.get("interactive")))
        cx += w + 80
        row = max(row, h)
    y = cy + row + 500

json.dump(canvas, open(PROJECT / "canvas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
disk = {p.name for p in PROJECT.glob("*.dc.html")}
listed = set(canvas["boards"])
print("disk", len(disk), "index", len(listed), "unlisted", sorted(disk - listed), "missing", sorted(listed - disk))
print("screens kept", sum(v.get("page") == "salinan4" for v in canvas["boards"].values()), "components page", sum(v.get("page") == PAGE for v in canvas["boards"].values()))
print("over 8000:", [(k, v["h"]) for k, v in canvas["boards"].items() if v["h"] > MAX_H or v["w"] > MAX_H])
print("page size:", x, "x", y)
print("sheet heights:", [(f[:-8], canvas["boards"][f]["h"]) for f in sheet_files])
print("removed files:", removed)
files = {f"project/{n}": f"project/{n}" for n in sorted(disk) + ["tokens.css"]}
json.dump(files, open(ROOT / "publish-files.json", "w"))
print("publish files:", len(files), "bytes", sum((PROJECT / k.split('/')[1]).stat().st_size for k in files))

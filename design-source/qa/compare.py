#!/usr/bin/env python3
"""Compare a board with the approved baseline: pixels, text, links, images, type styles.
Use --orig-dir design-source/mobbin4-originals-2026-11-03 to compare with the first originals instead.

Usage: python3 compare.py <Board> [--steps steps.json] [--label name] [--no-orig-cache]

Writes to qa/runs/<Board>[-label]/: orig.png new.png side.png diff.png report.json
Prints a verdict. Exit 0 only when every gate passes.
"""
import argparse
import collections
import json
import os
import pathlib
import subprocess
import sys

from PIL import Image, ImageChops

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
ORIG = SCRATCH / "baseline"  # the last version the owner approved
NEW = SCRATCH / "workspace" / "project"
RUNTIME = SCRATCH / "runtime/dc-runtime.js"
CAPTURE = SCRATCH / "qa" / "capture.cjs"

MAX_PIXEL_PCT = 0.6      # % of pixels that may differ visibly
MAX_HEIGHT_PX = 2        # page height difference
TOLERANCE = 24           # per-channel difference ignored as anti-aliasing noise

ap = argparse.ArgumentParser()
ap.add_argument("board")
ap.add_argument("--steps")
ap.add_argument("--label", default="")
ap.add_argument("--no-orig-cache", action="store_true")
ap.add_argument("--orig-dir", default=str(ORIG))
ap.add_argument("--new-dir", default=str(NEW))
args = ap.parse_args()

for d in (args.orig_dir, args.new_dir):
    if not (pathlib.Path(d) / f"{args.board}.dc.html").exists():
        sys.exit(f"FAIL {args.board}: no such board in {d}")

canvas = json.load(open(SCRATCH / "workspace/project/canvas.json", encoding="utf-8"))
entry = canvas["boards"].get(args.board + ".dc.html", {})
w = int(entry.get("w") or 360)
h = int(entry.get("h") or 800)
run = SCRATCH / "qa" / "runs" / (args.board + (f"-{args.label}" if args.label else ""))
run.mkdir(parents=True, exist_ok=True)
env = {**os.environ, "DC_RUNTIME": str(RUNTIME)}


def capture(project, prefix):
    cmd = ["node", str(CAPTURE), project, args.board, str(w), str(h), str(prefix)]
    if args.steps:
        cmd.append(args.steps)
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=400)
    if r.returncode:
        sys.exit(f"capture failed for {project}: {r.stderr.strip()[:500]}")


op = run / "orig"
if args.no_orig_cache or not (run / "orig.png").exists() or args.steps:
    capture(args.orig_dir, op)
capture(args.new_dir, run / "new")
o_fp = json.load(open(run / "orig.json"))
n_fp = json.load(open(run / "new.json"))

gates = {}
details = {}

gates["no_errors"] = not n_fp["errors"] and not n_fp["logicErrors"]
details["errors"] = (n_fp["logicErrors"] + n_fp["errors"])[:8]

dh = n_fp["height"] - o_fp["height"]
gates["height"] = abs(dh) <= MAX_HEIGHT_PX
details["height"] = {"orig": o_fp["height"], "new": n_fp["height"], "delta": dh}
gates["width"] = n_fp["width"] == o_fp["width"]
details["width"] = {"orig": o_fp["width"], "new": n_fp["width"]}


def multiset_diff(a, b):
    ca, cb = collections.Counter(a), collections.Counter(b)
    return list((ca - cb).elements()), list((cb - ca).elements())


t_o = [x["t"] for x in o_fp["texts"]]
t_n = [x["t"] for x in n_fp["texts"]]
# Compare the page's words, since a node may legitimately split or merge.
w_miss, w_extra = multiset_diff(" ".join(t_o).split(), " ".join(t_n).split())
gates["text"] = not w_miss and not w_extra
details["text"] = {"missing": w_miss[:40], "extra": w_extra[:40]}

miss, extra = multiset_diff(o_fp["hrefs"], n_fp["hrefs"])
gates["links"] = not miss and not extra
details["links"] = {"missing": miss[:25], "extra": extra[:25]}

miss, extra = multiset_diff(o_fp["imgs"] + o_fp["bgs"], n_fp["imgs"] + n_fp["bgs"])
gates["images"] = not miss and not extra
details["images"] = {"missing": miss[:25], "extra": extra[:25]}


def style_key(x):
    return (x["t"], x["fs"], x["c"], x["w"], x["ff"], x["lh"], x["ls"], x["tt"])


so, sn = {}, {}
for x in o_fp["texts"]:
    so.setdefault(x["t"], collections.Counter())[style_key(x)[1:]] += 1
for x in n_fp["texts"]:
    sn.setdefault(x["t"], collections.Counter())[style_key(x)[1:]] += 1
names = ("font-size", "color", "weight", "family", "line-height", "letter-spacing", "transform")
style_diffs = []
for t in so:
    if t in sn and so[t] != sn[t]:
        a = (so[t] - sn[t]).most_common(1)
        b = (sn[t] - so[t]).most_common(1)
        if a and b:
            ch = {nm: [p, q] for nm, p, q in zip(names, a[0][0], b[0][0]) if p != q}
            style_diffs.append({"text": t[:60], "changed": ch})
gates["type_styles"] = not style_diffs
details["type_styles"] = style_diffs[:30]
details["type_styles_count"] = len(style_diffs)

a = Image.open(run / "orig.png").convert("RGB")
b = Image.open(run / "new.png").convert("RGB")
cw, ch_ = min(a.width, b.width), min(a.height, b.height)
ca, cb = a.crop((0, 0, cw, ch_)), b.crop((0, 0, cw, ch_))
diff = ImageChops.difference(ca, cb).convert("L").point(lambda v: 255 if v > TOLERANCE else 0)
hist = diff.histogram()
differ = hist[255]
total = cw * ch_
pct = 100 * differ / total
gates["pixels"] = pct <= MAX_PIXEL_PCT and a.size == b.size
bands = []
BAND = 200
for y in range(0, ch_, BAND):
    region = diff.crop((0, y, cw, min(y + BAND, ch_)))
    c = region.histogram()[255]
    if c:
        bands.append((y, round(100 * c / (cw * region.height), 2)))
worst = sorted(bands, key=lambda z: -z[1])[:10]
first = next((y for y, p in bands if p > 0.5), None)
details["pixels"] = {"pct": round(pct, 3), "orig_size": a.size, "new_size": b.size, "first_y_over_0.5pct": first, "worst_bands_y_pct": worst}

diff_vis = Image.composite(Image.new("RGB", diff.size, (255, 0, 80)), ca.point(lambda v: v // 3 + 170), diff)
side = Image.new("RGB", (a.width + b.width + diff_vis.width + 40, max(a.height, b.height)), "white")
side.paste(a, (0, 0))
side.paste(b, (a.width + 20, 0))
side.paste(diff_vis, (a.width + b.width + 40, 0))
side.save(run / "side.png")
diff_vis.save(run / "diff.png")

passed = all(gates.values())
report = {"board": args.board, "viewport": [w, h], "passed": passed, "gates": gates, "details": details}
json.dump(report, open(run / "report.json", "w"), indent=1, ensure_ascii=False)
print(f"{'PASS' if passed else 'FAIL'} {args.board}{' [' + args.label + ']' if args.label else ''}  pixels {pct:.3f}%  height {dh:+d}  styles {len(style_diffs)}")
for k, v in gates.items():
    if not v:
        print(f"  x {k}: {json.dumps(details.get(k), ensure_ascii=False)[:900]}")
print(f"  side-by-side: {run / 'side.png'}")
sys.exit(0 if passed else 1)

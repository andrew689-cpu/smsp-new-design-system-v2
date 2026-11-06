#!/usr/bin/env python3
"""Change prices ONLY in DataHarga on a temp copy, then check every place customers see them."""
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
LIVE = SCRATCH / "workspace/project"
TMP = pathlib.Path(tempfile.mkdtemp(dir=SCRATCH / "qa"))
RUN = SCRATCH / "qa/price-run"
RUN.mkdir(exist_ok=True)
for p in LIVE.iterdir():
    shutil.copy(p, TMP / p.name)

EDITS = {"[15,15,1,2.83,37700]": "[15,15,1,2.83,39000]", "[40,40,2,15.07,188600]": "[40,40,2,15.07,199900]", "[40,40,1.8,13.56,170600]": "[40,40,1.8,13.56,171111]"}
d = TMP / "DataHarga.dc.html"
t = d.read_text("utf-8")
for a, b in EDITS.items():
    assert t.count(a) == 1, a
    t = t.replace(a, b)
d.write_text(t, "utf-8")

print("old prices left in any file except DataHarga:")
for needle in ("37700", "188600", "188.600", "170600", "221800", "239700", "142000"):
    hits = [p.stem.replace(".dc", "") for p in LIVE.glob("*.dc.html") if needle in re.sub(r"<!--.*?-->", "", p.read_text("utf-8"), flags=re.S) and not p.name.startswith(("DataHarga", "Sheet"))]
    print(f"  {needle}: {hits}")

env = {**os.environ, "DC_RUNTIME": str(SCRATCH / "runtime/dc-runtime.js"),
       "REAL_IMAGES": str(SCRATCH / "images"), "SETTLE_MS": "2500"}
SEARCH = RUN / "search.json"
json.dump([{"click": '[aria-label="Cari di seluruh SMS Perkasa"]', "force": True}, {"wait": 700}, {"fill": ["input[type=search], input", "15 15 1"]}, {"wait": 700}], open(SEARCH, "w"))

# (screen, width, height, new text expected, old text that must be gone, steps)
CASES = [
    ("RecCreateM4", 360, 800, "39.000", "37.700", None, "price list, mobile"),
    ("DesktopProdukM4", 1440, 900, "39.000", "37.700", None, "price list, desktop"),
    ("DesktopProdukM4Salinan", 1440, 900, "39.000", "37.700", None, "price list, desktop copy"),
    ("RecCreateM4Salinan1", 360, 800, "39.000", "37.700", None, "old copy 1"),
    ("SalinanProdukPageM4", 360, 800, "39.000", "37.700", None, "old copy 2"),
    ("SkuDetailM4", 360, 800, "199.900", "188.600", None, "SKU page price, mobile"),
    ("DesktopSkuM4", 1440, 900, "199.900", "188.600", None, "SKU page price, desktop"),
    ("DesktopSkuM4Salinan", 1440, 900, "199.900", "188.600", None, "SKU page copy"),
    ("SalinanSkuPageM4", 360, 800, "199.900", "188.600", None, "SKU old copy"),
    ("SkuDetailM4", 360, 800, "171.111", "170.600", None, "other sizes rail, mobile"),
    ("DesktopSkuM4", 1440, 900, "171.111", "170.600", None, "other sizes rail, desktop"),
    ("SalinanSkuPageM4", 360, 800, "171.111", "170.600", None, "other sizes rail, old copy"),
    ("RecCreateM4", 360, 800, "39.000", "37.700", SEARCH, "search results, mobile"),
    ("SalinanProdukPageM4", 360, 800, "39.000", "37.700", SEARCH, "search results, old copy"),
]
fails = 0
for i, (board, w, h, new, old, steps, label) in enumerate(CASES):
    pre = RUN / f"{i}-{board}"
    cmd = ["node", str(SCRATCH / "qa/capture.cjs"), str(TMP), board, str(w), str(h), str(pre)]
    if steps:
        cmd.append(str(steps))
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=200)
    if r.returncode:
        print(f"  ??? {label}: {r.stderr.strip()[:200]}")
        fails += 1
        continue
    fp = json.load(open(str(pre) + ".json"))
    text = " ".join(x["t"] for x in fp["texts"])
    ok = new in text and old not in text
    fails += not ok
    print(f"  {'PASS' if ok else 'FAIL'} {label:30s} {board}: new {new} {'found' if new in text else 'MISSING'}, old {old} {'STILL THERE' if old in text else 'gone'}  errors {len(fp['errors'])}")
shutil.rmtree(TMP)
print("FAILURES:", fails)

#!/usr/bin/env python3
"""Run the interaction tests that apply to one screen, against the approved baseline.

Usage: python3 run_steps.py <Screen> [--jobs 6]
Prints PASS, FAIL or CANT-RUN per step. CANT-RUN means the step's control isn't on this
screen. Exit 1 only if a step fails.
"""
import argparse
import concurrent.futures
import os
import pathlib
import subprocess
import sys

QA = pathlib.Path(__file__).resolve().parent
SRC = QA.parent
STEPS = QA / "steps"

# Which step files apply to which screen. Prefix "" means every file in the family.
MAP = {
    "RecCreateM4": [("harga", "m_")],
    "DesktopProdukM4": [("harga", "d_")],
    "DesktopProdukM4Salinan": [("harga", "d_")],
    "RecCreateM4Salinan1": [("harga", "f_")],
    "SalinanProdukPageM4": [("harga", "f_")],
    "SkuDetailM4": [("sku", "m_"), ("sku", "s_")],
    "SalinanSkuPageM4": [("sku", "f_"), ("sku", "s_")],
    "DesktopSkuM4": [("sku", "d_"), ("sku", "h_")],
    "DesktopSkuM4Salinan": [("sku", "d_"), ("sku", "h_")],
    "UlasanM4Salinan": [("katalog", "")],
    "DesktopUlasanM4": [("katalog", "")],
    "KategoriM4": [("katalog", "")],
    "DesktopKategoriM4": [("katalog", "")],
    "ProdukIndexM4": [("katalog", "")],
    "DesktopProdukIndexM4": [("katalog", "")],
}
for s in ("BerandaM4", "DesktopBerandaM4", "SalinanBerandaM4", "SalinanBeranda2M4", "SalinanBeranda3M4", "SalinanBeranda4M4", "SalinanBeranda5M4", "SalinanBeranda6M4", "SalinanBeranda7M4", "SalinanBeranda8M4", "SalinanBeranda9M4"):
    MAP[s] = [("beranda", "")]
for s in ("SalinanArtikel2M4", "DesktopArtikelM4", "DetailArtikel2M4", "DetailArtikel3M4", "DetailArtikel4M4", "SalinanArtikel2M4Salinan", "SalinanArtikelM4"):
    MAP[s] = [("artikel", "")]
for s in ("SalinanBlogM4", "DesktopBlogM4", "SalinanBlogM4Salinan", "SalinanBlog2M4", "SalinanBlog3M4", "SalinanBlog4M4", "SalinanBlog5M4"):
    MAP[s] = [("blog", s + "-")]

for s in ("LearningM4", "SalinanLearning1M4", "SalinanLearning2M4"):
    MAP[s] = [("belajar", "")]

ap = argparse.ArgumentParser()
ap.add_argument("screen")
ap.add_argument("--jobs", type=int, default=6)
args = ap.parse_args()
if args.screen not in MAP:
    sys.exit(f"Unknown screen {args.screen}. Screens: {', '.join(sorted(MAP))}")

files = []
for fam, prefix in MAP[args.screen]:
    files += sorted(f for f in (STEPS / fam).glob(prefix + "*.json"))
if not files:
    sys.exit(f"No steps found for {args.screen}")

env = {**os.environ, "REAL_IMAGES": str(SRC / "images"), "SETTLE_MS": os.environ.get("SETTLE_MS", "3000")}


def one(f):
    r = subprocess.run([sys.executable, str(QA / "compare.py"), args.screen, "--steps", str(f), "--label", "step-" + f.stem],
                       env=env, capture_output=True, text=True, timeout=500)
    out = (r.stdout + r.stderr).strip()
    if "capture failed" in out:
        return f.stem, "CANT-RUN", ""
    first = out.splitlines()[0] if out else ""
    detail = " | ".join(line.strip()[:150] for line in out.splitlines()[1:] if line.startswith("  x "))
    return f.stem, "PASS" if r.returncode == 0 else "FAIL", (first.split("  ", 1)[-1] if r.returncode else "") + (" " + detail if detail else "")


with concurrent.futures.ThreadPoolExecutor(args.jobs) as ex:
    results = list(ex.map(one, files))
for name, status, detail in results:
    print(f"{status:8s} {name} {detail}".rstrip())
counts = {k: sum(1 for r in results if r[1] == k) for k in ("PASS", "FAIL", "CANT-RUN")}
print(f"{args.screen}: {counts['PASS']} pass, {counts['FAIL']} fail, {counts['CANT-RUN']} can't run")
sys.exit(1 if counts["FAIL"] else 0)

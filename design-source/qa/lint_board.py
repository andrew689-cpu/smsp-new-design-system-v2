#!/usr/bin/env python3
"""MUST-USE-COMPONENTS gate for a refactored screen board.

A screen may only contain: <dc-import>, <sc-for>, <sc-if>, and layout wrappers with layout-only styling.
All visible UI comes from components. No text, no controls, no icons, no colors, no :root.

Usage: python3 lint_board.py <Board> [<Board> ...]   (also prints a size ratio)
"""
import html.parser
import pathlib
import re
import sys

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
NEW = SCRATCH / "workspace" / "project"
ORIG = SCRATCH / "mobbin4-originals-2026-11-03"

ALLOWED_TAGS = {"dc-import", "sc-for", "sc-if", "div", "section", "main", "article", "aside", "nav", "header", "footer", "ul", "ol", "li", "span"}
LAYOUT_PROPS = re.compile(
    r"^(display|flex(-[a-z-]+)?|grid(-[a-z-]+)?|gap|row-gap|column-gap|align-[a-z]+|justify-[a-z]+|place-[a-z]+|order|"
    r"margin(-[a-z-]+)?|padding(-[a-z-]+)?|width|height|min-width|min-height|max-width|max-height|box-sizing|"
    r"position|top|right|bottom|left|inset|z-index|overflow(-[xy])?|scroll-[a-z-]+|background|background-color|"
    r"list-style|list-style-type|pointer-events|isolation|contain|transform|visibility|opacity)$"
)


class P(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errs = []
        self.imports = 0
        self.depth_helmet = 0

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        if tag == "helmet":
            self.depth_helmet += 1
            return
        if self.depth_helmet:
            if tag == "link":
                href = dict(attrs).get("href", "")
                if "tokens.css" not in href and "fonts.googleapis.com" not in href:
                    self.errs.append(f"line {line}: helmet link not allowed: {href[:60]}")
            else:
                self.errs.append(f"line {line}: <{tag}> in helmet: only font and tokens links are allowed")
            return
        if tag == "dc-import":
            self.imports += 1
        if tag not in ALLOWED_TAGS:
            self.errs.append(f"line {line}: raw <{tag}> on a screen: must come from a component")
        for k, v in attrs:
            if k == "style" and v:
                for decl in v.split(";"):
                    if ":" not in decl or "{{" in decl.split(":")[0]:
                        continue
                    prop, val = decl.split(":", 1)
                    prop = prop.strip().lower()
                    if prop.startswith("--"):
                        continue
                    if not LAYOUT_PROPS.match(prop):
                        self.errs.append(f"line {line}: visual style '{prop}' on a wrapper: must live in a component")
                    if prop in ("background", "background-color") and "{{" not in val and "var(" not in val and val.strip() not in ("none", "transparent"):
                        self.errs.append(f"line {line}: background must be a token")

    def handle_endtag(self, tag):
        if tag == "helmet":
            self.depth_helmet -= 1

    def handle_data(self, data):
        if self.depth_helmet:
            return
        t = data.strip()
        if t:
            self.errs.append(f"line {self.getpos()[0]}: text on a screen: '{t[:50]}' must be a prop of a component")


bad = 0
for board in sys.argv[1:]:
    p = NEW / f"{board}.dc.html"
    if not p.exists():
        print(f"MISSING {board}")
        bad += 1
        continue
    raw = p.read_text("utf-8")
    errs = []
    if '<script src="./support.js"></script>' not in raw:
        errs.append("missing support.js line")
    if raw.count("<x-dc>") != 1:
        errs.append("needs one <x-dc>")
    tpl = raw.split("<x-dc>")[-1].split("</x-dc>")[0]
    if "<!--" in tpl:
        tpl_nc = re.sub(r"<!--.*?-->", "", tpl, flags=re.S)
    else:
        tpl_nc = tpl
    if 'href="tokens.css"' not in raw:
        errs.append("must link tokens.css")
    if ":root" in raw:
        errs.append("':root' on a screen: tokens live in tokens.css")
    parser = P()
    parser.feed(tpl_nc)
    errs += parser.errs
    if parser.imports == 0:
        errs.append("imports no components")
    js_m = re.search(r"data-dc-script[^>]*>(.*?)</script>", raw, re.S)
    js = js_m.group(1) if js_m else ""
    for lit in sorted(set(re.findall(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|\brgba?\([^)]*\)", js)))[:6]:
        errs.append(f"literal color in logic: {lit}")
    for bad_s in ("innerHTML", "appendChild", "createElement"):
        if bad_s in js:
            errs.append(f"forbidden in logic: {bad_s}")
    orig = (ORIG / f"{board}.dc.html").stat().st_size if (ORIG / f"{board}.dc.html").exists() else 0
    tag = "PASS" if not errs else "FAIL"
    print(f"{tag} {board}: {parser.imports} imports, {p.stat().st_size // 1024} KB (was {orig // 1024} KB), issues {len(errs)}")
    for e in errs[:25]:
        print("   ", e)
    bad += bool(errs)
sys.exit(1 if bad else 0)

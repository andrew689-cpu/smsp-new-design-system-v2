#!/usr/bin/env python3
"""The owner's rule: every piece of UI is one component, configured by props, without exception.

Usage: python3 lint_strict.py [--summary] [Name ...]    Exit 1 on any violation.
Control atoms that may hold a raw <button> are listed in qa/control_atoms.txt.
"""
import collections
import hashlib
import html
import json
import pathlib
import re
import sys

SCRATCH = pathlib.Path(__file__).resolve().parent.parent
P = SCRATCH / "workspace" / "project"
canvas = json.load(open(SCRATCH / "workspace/project/canvas.json", encoding="utf-8"))
SCREENS = sorted(k[:-8] for k, v in canvas["boards"].items() if v.get("page") == "salinan4")
DOCS = {"DocSpec", "Colors", "FontSizes", "IconSheet"}
summary = "--summary" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("--")]
controls = set((SCRATCH / "qa/control_atoms.txt").read_text().split()) if (SCRATCH / "qa/control_atoms.txt").exists() else set()

SVG_OK = {"Icon", "Logo", "Rating"}
INPUT_OK = {"TextField", "SearchField", "Radio", "Chip", "Segmented", "BeforeAfter"}
BUTTON_OK = {"Button", "IconButton", "GlassButton", "Chip", "Segmented", "Accordion", "CarouselDots"} | controls
COLOR = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b(?![-\w])|\brgba?\(|\bhsla?\(")
STYLE_IN_LOGIC = re.compile(r"\b(background|color|box-shadow|border(-[a-z]+)?|font-size|font-weight|letter-spacing|line-height)\s*:\s*[^,'\"}]")


def nc(t):
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)


def parts(name):
    raw = nc((P / f"{name}.dc.html").read_text("utf-8"))
    tpl = raw.split("<x-dc>")[-1].split("</x-dc>")[0]
    m = re.search(r"<script type=\"text/x-dc\" data-dc-script data-props='([^']*)'>(.*?)</script>", raw, re.S)
    props = {}
    js = ""
    if m:
        try:
            props = json.loads(html.unescape(m.group(1)))
        except ValueError:
            props = {}
        js = m.group(2)
    return raw, tpl, props, js


names = sorted(p.name[:-8] for p in P.glob("*.dc.html"))
comps = [n for n in names if n not in SCREENS and not n.startswith("Sheet") and n not in DOCS]
V = collections.defaultdict(list)
info = {n: parts(n) for n in names}

# Component rules
for c in comps:
    raw, tpl, props, js = info[c]
    if c not in SVG_OK:
        n = len(re.findall(r"<svg\b", tpl))
        if n:
            V["raw_svg"].append((c, n))
    if c != "Heading":
        n = len(re.findall(r"<h[1-6]\b", tpl))
        if n:
            V["raw_heading"].append((c, n))
    if c != "Price":
        n = len(re.findall(r"data-harga", tpl))
        if n:
            V["raw_price"].append((c, n))
    if c not in INPUT_OK:
        n = len(re.findall(r"<input\b", tpl))
        if n:
            V["raw_input"].append((c, n))
    if c not in BUTTON_OK:
        n = len(re.findall(r"<button\b", tpl))
        if n:
            V["raw_button"].append((c, n))
    used = set(re.findall(r"this\.props\.([A-Za-z_]\w*)", js))
    for dest in re.findall(r"(?:const|let|var)\s*\{([^}]*)\}\s*=\s*this\.props", js):
        used |= {x.split(":")[0].split("=")[0].strip() for x in dest.split(",") if x.strip()}
    undeclared = sorted(u for u in used if u not in props and u != "children")
    if undeclared:
        V["prop_undeclared"].append((c, undeclared[:10], len(undeclared)))
    nodefault = sorted(k for k, v in props.items() if k != "$preview" and isinstance(v, dict) and v.get("editor") not in (None,) and "default" not in v)
    if nodefault:
        V["prop_no_default"].append((c, nodefault[:6]))
    cleaned = COLOR.findall(re.sub(r"rgba\(17,\s*25,\s*33[^)]*\)|rgba\(255,\s*255,\s*255[^)]*\)|rgba\(0,\s*0,\s*0[^)]*\)", "", tpl + js))
    if cleaned and c not in {"Icon", "SocialLoginButtons", "Logo"}:
        V["literal_color"].append((c, len(cleaned)))
    lit = [x.strip() for x in re.findall(r"font-size:\s*([^;\"'{+]+)", tpl + js) if "var(" not in x and x.strip() and "inherit" not in x]
    if lit:
        V["literal_font_size"].append((c, lit[:3]))

# Enum values used by importers must exist on the component.
for n in names:
    raw, tpl, props, js = info[n]
    for comp, body in re.findall(r'<dc-import\b[^>]*?\bname="([^"{]+)"([^>]*)>', tpl):
        if comp not in info:
            continue
        cp = info[comp][2]
        for a, v in re.findall(r'(?<![-\w])([a-zA-Z]+)="([^"{]+)"', body):
            d = cp.get(a)
            if isinstance(d, dict) and d.get("editor") == "enum" and v not in (d.get("options") or []):
                V["enum_value_missing"].append((f"{comp}.{a}", v, n))
            if a not in cp and a not in ("name", "style", "hint", "children") and not a.startswith("aria") and not a.startswith("data"):
                V["import_prop_undeclared"].append((f"{comp}.{a}", n))

# Screen rules
for s in SCREENS:
    raw, tpl, props, js = info[s]
    over = sorted(set(re.findall(r"(?:^|[;\"\s])(--[\w-]+)\s*:", tpl)))
    if over:
        V["screen_token_override"].append((s, over))
    n = len(STYLE_IN_LOGIC.findall(js))
    if n:
        V["screen_style_in_logic"].append((s, n))
    for lit in sorted(set(COLOR.findall(js))):
        V["screen_literal_color"].append((s, lit))

# Same data written on several screens: it belongs in the component's default props.
blocks = collections.defaultdict(set)
for s in SCREENS:
    js = info[s][3]
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
        if len(body) >= 80:
            blocks[hashlib.md5(re.sub(r"\s+", "", body).encode()).hexdigest()[:8]].add((name, s))
for h, v in blocks.items():
    ss = {x[1] for x in v}
    if len(ss) >= 2:
        V["data_repeated_on_screens"].append((sorted({x[0] for x in v})[0], len(ss), sorted(ss)[:4]))

attr = collections.defaultdict(set)
for s in SCREENS:
    for comp, body in re.findall(r'<dc-import\b[^>]*?\bname="([^"]+)"([^>]*)>', info[s][1]):
        cp = info.get(comp, ("", "", {}, ""))[2]
        for a, v in re.findall(r'(?<![-\w])([a-zA-Z]+)="([^"{]+)"', body):
            d = cp.get(a)
            if a in ("name", "hint", "tata", "style", "teks", "judul") or (isinstance(d, dict) and d.get("editor") == "enum"):
                continue
            attr[(comp, a, v)].add(s)
for (comp, a, v), ss in attr.items():
    if len(ss) >= 4:
        V["prop_repeated_should_be_default"].append((f"{comp}.{a}", v[:40], len(ss)))

# Every component must be used.
imports = collections.defaultdict(set)
for n in names:
    tpl, js = info[n][1], info[n][3]
    src = tpl + js
    for c in set(re.findall(r'name="([A-Z]\w+)"', src)) | set(re.findall(r"""komponen["']?\s*[:=]\s*["']([A-Z]\w+)""", src)):
        imports[c].add(n)


def reach(c, seen=None):
    seen = seen if seen is not None else set()
    for u in imports.get(c, ()):
        if u not in seen:
            seen.add(u)
            reach(u, seen)
    return seen


unused = [c for c in comps if not any(u in SCREENS for u in reach(c))]
if unused:
    V["component_unused_by_any_screen"].append(unused)

total = 0
for rule in sorted(V):
    items = V[rule]
    if only:
        items = [i for i in items if any(o in str(i) for o in only)]
        if not items:
            continue
    total += len(items)
    print(f"{rule}: {len(items)}")
    if not summary:
        for it in items[:60]:
            print("   ", str(it)[:170])
print(f"TOTAL violations: {total}")
sys.exit(1 if total else 0)

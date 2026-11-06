"""Static checks for component boards. Exit 1 if any ERROR.

Usage: python3 -I lint_components.py <components project dir> [file.dc.html ...]
With no files, checks every *.dc.html in the directory.
"""
import html
import html.parser
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

root = pathlib.Path(sys.argv[1])
scratch = root.parent.parent
named = sys.argv[2:]
paths = [root / n for n in named] if named else sorted(root.glob("*.dc.html"))

token_files = [root / "tokens.css"] + sorted((root.parent / "_token-requests").glob("*.css"))
defined = set()
for tf in token_files:
    if tf.exists():
        defined |= set(re.findall(r"(--[\w-]+)\s*:", tf.read_text("utf-8")))

blob_ids = set()
store = scratch / "store-ids.txt"
if store.exists():
    blob_ids = set(store.read_text().split())

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SVG_SELF_OK = set()
HOLE_OK = re.compile(r"^\s*(?:[A-Za-z_$][\w$]*(?:\.[\w$]+)*|true|false|null|-?\d+(?:\.\d+)?|'[^']*'|\"[^\"]*\")\s*$")
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
LITERAL_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(")


class Parser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.imports = []
        self.imgs = []

    def handle_starttag(self, tag, attrs):
        if tag == "dc-import":
            d = dict(attrs)
            self.imports.append(d.get("name"))
        if tag == "img":
            d = dict(attrs)
            if "alt" not in d:
                self.errors.append(f"line {self.getpos()[0]}: <img> without alt")
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_startendtag(self, tag, attrs):
        if tag not in VOID:
            self.errors.append(f"line {self.getpos()[0]}: self-closed <{tag}/> (close it explicitly)")
        if tag == "dc-import":
            self.imports.append(dict(attrs).get("name"))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: stray </{tag}>")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        self.errors.append(f"line {self.getpos()[0]}: </{tag}> closes <{self.stack[-1][0]}> from line {self.stack[-1][1]}")
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


all_stems = {p.stem.replace(".dc", "") for p in root.glob("*.dc.html")}
graph = {}
total_errors = 0
node = shutil.which("node")

for path in paths:
    errs, warns = [], []
    raw = path.read_text("utf-8")
    stem = path.name[: -len(".dc.html")]
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", stem):
        errs.append("bad file name")
    if '<script src="./support.js"></script>' not in raw:
        errs.append("missing exact support.js head line")
    if raw.count("<x-dc>") != 1 or raw.count("</x-dc>") != 1:
        errs.append("must have exactly one <x-dc> block")
    m_h = re.search(r"<helmet>(.*?)</helmet>", raw, re.S)
    if not m_h or 'href="tokens.css"' not in m_h.group(1):
        errs.append('helmet must link href="tokens.css"')
    elif "<style" in m_h.group(1):
        errs.append("no <style> in helmet: send shared rules through _token-requests")
    for bad in ("<iframe", "<object", "<embed", "innerHTML", "appendChild", "keydown", "window.addEventListener('key"):
        if bad in raw:
            errs.append(f"forbidden: {bad}")
    if re.search(r"\bwindow\.[A-Za-z_$][\w$]*\s*=", raw):
        errs.append("forbidden: assigning window.X")
    if re.search(r'=\s*(?![\s"\'{])[^\s"\'>=][^\s>]*(?=[\s>])', re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", raw.split("<x-dc>")[-1].split("</x-dc>")[0], flags=re.S).replace(">", "> ")) and False:
        warns.append("possibly unquoted attribute")
    if EMOJI.search(re.sub(r"<!--.*?-->", "", raw, flags=re.S)):
        errs.append("emoji found (use Icon)")

    tpl = raw.split("<x-dc>")[-1].split("</x-dc>")[0] if "<x-dc>" in raw else ""
    tpl_nc = re.sub(r"<!--.*?-->", "", tpl, flags=re.S)
    for hole in re.findall(r"\{\{(.*?)\}\}", tpl_nc, re.S):
        if not HOLE_OK.match(hole):
            errs.append(f"hole is not a dotted path: {{{{{hole.strip()[:50]}}}}}")

    parser = Parser()
    body = raw[raw.find("<body"): raw.rfind("</body>") + 7] if "<body" in raw else raw
    body_tpl = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    parser.feed(body_tpl)
    errs += parser.errors
    if parser.stack:
        errs.append(f"unclosed: {parser.stack[-3:]}")

    names = [n for n in parser.imports]
    graph[stem] = [n for n in names if n and "{{" not in n]
    for n in names:
        if not n:
            errs.append("dc-import without name")
        elif "{{" not in n and n not in all_stems:
            errs.append(f'dc-import name="{n}" has no file')
    for bad_style in re.findall(r'<dc-import[^>]*\sstyle="([^"]*)"', tpl_nc):
        if re.search(r"margin|padding|flex|align-self|grid-", bad_style):
            errs.append("dc-import style only keeps position/size: wrap it for margins or flex")

    m_s = re.search(r"<script type=\"text/x-dc\" data-dc-script data-props='([^']*)'>(.*?)</script>", raw, re.S)
    if not m_s:
        errs.append("missing logic script with single-quoted data-props")
    else:
        try:
            props = json.loads(html.unescape(m_s.group(1)))
            pv = props.get("$preview") or {}
            if not (isinstance(pv.get("width"), (int, float)) and isinstance(pv.get("height"), (int, float))):
                errs.append("$preview needs numeric width and height")
        except ValueError as e:
            errs.append(f"data-props is not JSON: {e}")
        js = m_s.group(2)
        if "class Component extends DCLogic" not in js:
            errs.append("logic must define class Component extends DCLogic")
        if re.search(r"^\s*(import|export)\s", js, re.M):
            errs.append("no import/export in logic")
        if node:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as tmp:
                tmp.write("class DCLogic{}\n" + js)
            r = subprocess.run([node, "--check", tmp.name], capture_output=True, text=True)
            pathlib.Path(tmp.name).unlink(missing_ok=True)
            if r.returncode:
                errs.append("JS syntax: " + " ".join(r.stderr.strip().splitlines()[1:4])[:300])

    nc = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    for v in sorted(set(re.findall(r"var\(\s*(--[\w-]+)", nc)) - defined):
        errs.append(f"token not defined anywhere: {v}")
    for b in sorted(set(re.findall(r"/_blob/([0-9a-f]{32})", nc)) - blob_ids) if blob_ids else []:
        errs.append(f"image id not in this canvas store: {b}")
    for t in re.findall(r"font-size:\s*([^;\"']+)", nc):
        t = t.strip()
        if "var(" not in t and "{{" not in t and "' +" not in t:
            warns.append(f"literal font-size: {t}")
    lit = sorted(set(LITERAL_COLOR.findall(re.sub(r"rgba\(17,\s*25,\s*33[^)]*\)|rgba\(255,\s*255,\s*255[^)]*\)", "", nc))))
    if lit:
        warns.append("literal colors: " + ", ".join(lit[:8]))
    for href in re.findall(r'href="([^"{]+\.dc\.html)"', nc):
        warns.append(f"hard-coded board link: {href}")

    if errs or warns:
        print(f"{path.name}")
        for e in errs:
            print(f"  ERROR {e}")
        for w in warns:
            print(f"  warn  {w}")
    total_errors += len(errs)

# circular imports, across the whole folder
for p in root.glob("*.dc.html"):
    s = p.name[: -len(".dc.html")]
    if s not in graph:
        graph[s] = re.findall(r'<dc-import[^>]*\sname="([^"{]+)"', re.sub(r"<!--.*?-->", "", p.read_text("utf-8"), flags=re.S))


def cycle(n, seen, trail):
    if n in trail:
        return trail[trail.index(n):] + [n]
    if n in seen:
        return None
    seen.add(n)
    for c in graph.get(n, []):
        r = cycle(c, seen, trail + [n])
        if r:
            return r
    return None


seen = set()
for n in list(graph):
    r = cycle(n, seen, [])
    if r:
        print("ERROR circular import:", " -> ".join(r))
        total_errors += 1
        break

print(f"checked {len(paths)} file(s), node={'yes' if node else 'no'}, errors={total_errors}")
sys.exit(1 if total_errors else 0)

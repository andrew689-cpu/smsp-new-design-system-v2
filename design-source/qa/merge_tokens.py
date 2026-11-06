"""Merge _token-requests/*.css into tokens.css, de-duplicating and reporting clashes.

Usage: python3 -I merge_tokens.py <components root>
Writes project/tokens.css from project/tokens.base.css (saved on first run).
"""
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
project = root / "project"
live = project / "tokens.css"
base_copy = root / "tokens.base.css"
if not base_copy.exists():
    base_copy.write_text(live.read_text("utf-8"), "utf-8")
base = base_copy.read_text("utf-8")


def blocks(css):
    """Top-level (prelude, body) pairs, comments removed."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out, i, n = [], 0, len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0:
            break
        depth, k = 1, j + 1
        while k < n and depth:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        out.append((" ".join(css[i:j].split()), css[j + 1:k - 1]))
        i = k
    return out


def decls(body):
    return {m[0]: " ".join(m[1].split()) for m in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);?", body)}


def norm(s):
    return re.sub(r"\s+", "", s)


known = {}
for prelude, body in blocks(base):
    if prelude == ":root":
        known.update(decls(body))

new_tokens, token_src = {}, {}
rules, rule_src = {}, {}
clashes = []
for req in sorted((root / "_token-requests").glob("*.css")):
    group = req.stem
    for prelude, body in blocks(req.read_text("utf-8")):
        if prelude == ":root":
            for name, value in decls(body).items():
                if name in known and norm(known[name]) != norm(value):
                    clashes.append(f"TOKEN {name}: base={known[name]} | {group}={value}")
                elif name in new_tokens and norm(new_tokens[name]) != norm(value):
                    clashes.append(f"TOKEN {name}: {token_src[name]}={new_tokens[name]} | {group}={value}")
                elif name not in known and name not in new_tokens:
                    new_tokens[name] = value
                    token_src[name] = group
        else:
            if prelude.startswith("@media") and prelude in rules:
                if norm(body) not in norm(rules[prelude]):
                    rules[prelude] = rules[prelude].rstrip() + "\n" + body
            elif prelude in rules and norm(rules[prelude]) != norm(body):
                clashes.append(f"RULE {prelude}: {rule_src[prelude]} vs {group}")
                rules[prelude + f" /*{group}*/"] = body
            elif prelude not in rules:
                rules[prelude] = body
                rule_src[prelude] = group

lines = [base.rstrip(), "", "/* ==========================================================================",
         "   TOKEN DAN ATURAN BERSAMA DARI PEMECAHAN KOMPONEN",
         "   ========================================================================== */", "", ":root {"]
for group in sorted(set(token_src.values())):
    lines.append(f"  /* {group} */")
    lines += [f"  {k}: {v};" for k, v in new_tokens.items() if token_src[k] == group]
lines += ["}", ""]
for prelude, body in rules.items():
    if "/*" in prelude:
        lines.append(f"/* BENTROK, TIDAK DIPASANG: {prelude} */")
        continue
    lines.append(f"{prelude} {{{body.rstrip()}\n}}")
live.write_text("\n".join(lines) + "\n", "utf-8")

print(f"new tokens: {len(new_tokens)}; shared rules: {len(rules)}; bytes: {live.stat().st_size}")
print("clashes:" if clashes else "no clashes")
for c in clashes:
    print(" ", c)
vals = {}
for k, v in {**known, **new_tokens}.items():
    vals.setdefault(norm(v), []).append(k)
dups = {v: ks for v, ks in vals.items() if len(ks) > 1 and any(k in new_tokens for k in ks)}
print("same value, different new token:")
for v, ks in dups.items():
    print(f"  {v[:50]}: {', '.join(ks)}")

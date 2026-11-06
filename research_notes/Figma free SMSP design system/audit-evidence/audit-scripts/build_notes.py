import re,sys,ast
A,O,OUT=sys.argv[1:4]
t=open(A+'/notes_template.md').read()
R=[
("each changing a `3` to a `4` or a `d` to an `e`-adjacent version digit. All four are inside the header comment:","two `3`→`4` and two `4`→`5` (the board name and its paired blog number). All four are inside the header comment:"),
("(the logo link on 25 boards, some twice)","(the logo link on 26 boards, twice on 2 of them)"),
("Near-exact: 13 diff ops. Links retargeted to its paired Salinan boards, related-product name size differs","Near-exact: 13 diff ops. Links retargeted to its paired Salinan boards, fraud ribbon at 13px rather than 10px"),
("Only three have conflicting values: `--sisi`, `--seksi` and `--font-harga`.","Apart from `svh`/`vh` fallback pairs, only three have conflicting values: `--sisi`, `--seksi` and `--font-harga`."),
("The price recipe renders in inherited ink, in `--font-harga`. So the green \"price\" token is a leftover.","The price recipe renders in inherited ink, in `--font-harga`, with an occasional `--brand` promo price. So the green \"price\" token is a leftover."),
("`rgb(255,30,0)` article ribbon (25 of 28 uses as surface)","`rgb(255,30,0)` article ribbon (24 of 28 uses as surface, 3 canon)"),
("The 16 boards use 16 distinct values on mobile and 20 on desktop. All boards: 22 and 21.","Distinct values, counting the root rule: canon 16 mobile and 20 desktop; all boards 22 and 21."),
("44 / 700 / -0.01em (6 of 8)","44 / 700 (5 of 8, 4 of them at -0.01em)"),
("28 / 700 / lh 1.2 / -0.01em (5 of 7)","28 / 700 / lh 1.2 (5 of 7, 4 of them at -0.01em)"),
("Regular 400 is rare because body copy inherits it.","Regular 400 is rare, probably because body copy inherits it."),
("Desktop footer. Desktop-only names |","Desktop footer. Desktop-only names. A note calls `--selokan-dalam` unused, yet the code has 12 uses |"),
("**Mobile footer** has `padding-bottom:25rem` (250px) on canon boards, apparently to clear the floating bar.","**Mobile footer** has `padding-bottom:25rem` (250px, ×6 in canon). A note gives the reason: scroll room so the bottom bar does not cover content. It is applied even on `KategoriM4`, which has no bar."),
("| literal others | 2, 4, 8, 12, 20 | 5 | 3 | Drift; a note calls these intentional |","| literal others | 0, 2, 4, 8, 12, 20 | 6 | 5 | Drift; a note calls such values intentional |"),
("0.15rem ×3, 0.2rem ×3.","0.15rem ×3, 0.2rem ×4."),
("Animations at 240, 260, 300, 320, 380, 420, 440, 460, 520ms. Marquees 46s and 48s linear.","Animations at 240, 260, 300, 320, 380, 420, 440, 460, 520ms, spinner 800ms. Marquees 46s and 48s linear."),
("`chip-a`/`chip-b` (same definition; name pair forces restart)","`chip-a`/`chip-b` (same definition)"),
("| `outline:none` | 28 declarations, with no replacement | **Fails keyboard visibility** |","| `outline:none` | 28 declarations; no replacement found beyond the 3 rules above | **Fails keyboard visibility** |"),
("About 35 real components recur","About 40 real components recur"),
("| Bold highlights, Google glyph |","| Bold highlights inside the quote |"),
("| 25 | **Horizontal rail** | Home, Blog, SKU | 48% wide, 30 gutter | Snap, arrows on d |","| 25 | **Horizontal rail** | Home, SKU | 48% wide, 30 gutter | Scroll snap |"),
("| Produk, SKU, Blog, Article | Glass or brand button |","| Home, Produk, SKU, Blog, Article | Brand button |"),
("| 30 | **Section sheet and nav** | Same 4 m boards |","| 30 | **Section sheet and nav** | `RecCreateM4`, `SkuDetailM4`, `SalinanBlogM4` |"),
("| 72 glass, `--island` |","| 72 glass buttons, `--island` panel |"),
("chat log `role=log`, CSAT, form (name, WA, email), emoji |","chat log `role=log`, CSAT, form (name, WA, email), Google and Facebook social glyphs (`bSosial`), emoji. `SkuDetailM4` has only a light `ul` version |"),
("| \"Dipercaya Mitra\", \"Pencarian terkait\" | |","| \"Dipercaya Mitra\" m/d; \"Pencarian terkait\" m only | |"),
("All other boards expose only `$preview`.","All other canon boards expose only `$preview`."),
("as `[w, h, thickness, kg, price]`, for example","as what appears to be `[w, h, thickness, kg, price]` (field order inferred), for example"),
("No cart, checkout, account or order elements are in any canon outline. [s10][s10] [s8][s8]","A scan for cart, checkout and login terms gives 0 hits on all 34 boards. [s10][s10] [s15][s15]"),
("- `html{font-size:62.5%}` overrides user default scaling behaviour in a known-problematic way only if px text is used; here rem makes it scale. Worth keeping or dropping as an explicit decision.\n","- All values were converted from px to rem on 2026-10-28 with `html{font-size:62.5%}`. A note says this matches both the design-system repo and smsperkasa.com. Keep or drop this as an explicit decision.\n"),
("- 6 colour tokens have 0 uses,","- 6 tokens have 0 uses (4 are colours),"),
("| Error states | No error UI found for network, chat, or 404 | **Absent** |","| Error states | No error UI found. The error-term scan has 10 canon hits on 2 boards; the sampled one is article prose, and not all were read | **Absent as far as scanned** |"),
("| Loading | 1 spinner (`lazy-spin`), no skeletons | **Minimal** |","| Loading | 1 spinner (`lazy-spin`), 0 skeleton hits | **Minimal** |"),
("| Empty states | 1 pattern (filter no-results), `Belum ada` not found | **Minimal** |","| Empty states | 1 confirmed pattern (filter no-results) | **Minimal** |"),
("| Toast and notification | `aria-live` ×14, `role=status` ×1; copied label only | **Minimal** |","| Toast and notification | 0 toast hits; `aria-live` ×14, `role=status` ×1 | **Minimal** |"),
("| Checkbox, switch | 0 `checkbox`; radios 3 | **Absent** |","| Checkbox, switch | 0 `checkbox`, 0 `switch`; radios 3 | **Absent** |"),
("| Tooltip, popover | No named pattern | **Not found** |","| Tooltip, popover | 0 tooltip hits; `title` attributes only (15 canon) | **Not found** |"),
("| Accessible modal | No `aria-modal`, no `<dialog>`; focus trap not evident | **Partial** |","| Accessible modal | 0 `aria-modal`, 0 `<dialog>`, 0 `.focus(` calls, 0 `Escape` or `Tab` key strings in canon scripts | **Absent** |"),
("| Print, quote, or PDF price list | Not found | **Absent** |","| Print or PDF price list | 4 canon hits; the sampled one is prose (\"cetak biru\"), not a feature | **Not found** |"),
("| Data states | Long names, 0 prices, out of stock, \"harga hubungi\" not shown | **Not found** |","| Data states | Out-of-stock or ask-for-price UI not found. Stock terms have 13 canon hits; the sampled one is promo copy (\"Cek ketersediaan stok\") | **Not found** |"),
("Absences below are 0-match results from the scripts unless noted. [s6][s6] [s7][s7] [s11][s11] [s10][s10]","Absences below are 0-match results from the scripts unless noted. Text scans can miss differently worded UI. [s6][s6] [s7][s7] [s11][s11] [s10][s10] [s15][s15]"),
("[s14]: file:///","[s15]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s15.txt\n[s14]: file:///"),
]
for a,b in R:
    assert t.count(a)==1,(t.count(a),a[:70])
    t=t.replace(a,b)
# colour table from s5
rows=[]
for l in open(O+'/s5.txt'):
    p=l.rstrip('\n').split('|')
    if len(p)==9 and p[1].isdigit(): rows.append(p)
def fam(c):
    if c.startswith('var('): return None
    if c in('transparent','currentcolor'): return 'Keywords'
    if c.startswith(('rgba(255,255,255','#ffffff','#fefefe','#fbfbfb','#f6f8fa')): return 'White and white alpha'
    if c in('#0a0a0a','#000000','#1e1e1e','#1b191a','#5f5f5f') or c.startswith(('rgba(10,10,10','rgba(9,12,17')): return 'Ink, black and scrims'
    if c.startswith(('rgba(17,25,33','rgba(0,0,0','rgba(88,88,88','rgba(11,39,75')): return 'Shadow tints'
    if c in('#ececec','#f4f4f4','#e4e4e6','#dcdcde','#d6d6db','#c9c9cb','#d4d4d4'): return 'Greys'
    if c in('#fdecec','#a84c46','#fe0100') or c.startswith(('rgba(255,30,0','rgb(255,30,0','rgba(255,0,0','rgba(253,236,236')): return 'Reds and tints'
    if c in('#157f3c',): return 'Greens'
    if c in('#ffb800','#f8aa08','#9a6700'): return 'Rating golds'
    if c in('#4285f4','#34a853','#fbbc05','#ea4335','#1877f2'): return 'Third-party logos'
    if c in('#faf5ff','#ecdcfe','#7c3aed','#6d28d9'): return 'Purple tile'
    if c in('#1d4ed8',): return 'Blues'
    if c in('#253a4a','#517fa4','#37566e','#3f536b','#01132c'): return 'Slates (Salinan boards)'
    return 'Other'
order=['Ink, black and scrims','White and white alpha','Greys','Reds and tints','Greens','Blues','Rating golds','Purple tile','Slates (Salinan boards)','Third-party logos','Shadow tints','Keywords','Other']
G={k:[] for k in order}; n=0
for p in rows:
    f=fam(p[0])
    if f: G[f].append(p); n+=1
out=['%d literal values. Format: `value` all/canon(boards).\n'%n,'| Family | Values |','|---|---|']
for k in order:
    if G[k]:
        out.append('| %s | %s |'%(k,', '.join('`%s` %s/%s(%s)'%(p[0],p[1],p[2],p[6]) for p in G[k])))
toks=[p for p in rows if p[0].startswith('var(')]
out.append('\nColour tokens as used: '+', '.join('`%s` %s/%s(%s)'%(p[0][4:-1],p[1],p[2],p[6]) for p in toks)+'.')
assert n==100,n
t=t.replace('%%COLORTABLE%%','\n'.join(out))
open(OUT,'w').write(t)
print('ok',len(t),{k:len(v) for k,v in G.items()})

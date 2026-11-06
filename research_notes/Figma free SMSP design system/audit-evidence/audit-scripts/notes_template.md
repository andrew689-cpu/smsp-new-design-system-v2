# Source canvas audit: the de facto design language of "Prototype Mobbin 4"

Evidence base and counting rules, which apply to every number below:

- Source: 34 `*.dc.html` artboards plus `canvas.json`. Static analysis only. No board was rendered, because `./support.js` (the runtime, referenced by 34 of 34 boards) is not in the download. [s1][s1] [s11][s11]
- **"Canon" means the 16 boards proposed under question 1 (8 mobile, 8 desktop). "All" means all 34 (24 mobile, 10 desktop).**
- Counts are **declarations in source after stripping comments, not rendered instances**. A card inside `<sc-for>` counts once however many cards it renders.
- Declarations were read from inline `style=""`, `<helmet>` CSS, SVG attributes and JS string literals that begin with a CSS declaration. CSS assembled from concatenated JS fragments is only partly captured, so script-side counts are lower bounds.
- `html{font-size:62.5%}` makes 1rem = 10px. All px values below are rem × 10.
- 46.6% of all source bytes (44.9% of canon bytes) are comments: 3,521 unique notes dated 2026-10-09 to 2026-11-02, written in Indonesian. They were treated as data about intent. Where a note and the code disagree, the code wins and the disagreement is reported. [s14][s14] [s9][comments]

## 1. Artboard lineage: which boards are canonical?

### Takeaway
File names are unreliable, since "Salinan" in a file name does not mean copy: `SalinanBlogM4` is titled "Blog" and `SalinanArtikel2M4` is titled "Detail Artikel". Identity lives in `canvas.json` titles. There is a clean set of 16 canonical screens, but the home and blog pages have an unresolved owner decision between the plainly titled board and newer "Salinan" redesigns.

### Cited Findings

**Proposed canonical set** (rule: a title with no "Salinan" and no trailing number, plus one exception where a page type has no other board). [canvas.json][canvas] [s2][s2]

| Page type | Mobile (360) | Desktop (1440) | Inbound links, m / d | Last dated note, m / d |
|---|---|---|---|---|
| Home (Beranda) | `BerandaM4` "Beranda" (x1440 y-1200) | `DesktopBerandaM4` | 4 / 1 | 10-30 / 10-30 |
| Product price list | `RecCreateM4` "Mobbin 3 · Produk Page" | `DesktopProdukM4` | 8 / 5 | 11-02 / 10-30 |
| SKU detail | `SkuDetailM4` "Mobbin 3 · Detail SKU" | `DesktopSkuM4` | 8 / 1 | 11-02 / 10-30 |
| Reviews (Ulasan) | `UlasanM4Salinan` (**only mobile board for the type**) | `DesktopUlasanM4` | 0 / 2 | 10-30 / 10-30 |
| All products | `ProdukIndexM4` | `DesktopProdukIndexM4` | 5 / 8 | 11-02 / 10-30 |
| Category (Kategori) | `KategoriM4` | `DesktopKategoriM4` | 0 / 0 | 10-30 / 10-30 |
| Blog | `SalinanBlogM4` "Blog" | `DesktopBlogM4` | 0 / 1 | 10-30 / 10-30 |
| Article (Artikel) | `SalinanArtikel2M4` "Detail Artikel" | `DesktopArtikelM4` | 1 / 0 | 10-30 / 10-30 |

**The 18 non-canonical boards.** J is the Jaccard similarity of tags and lines after stripping comments. [s2][s2] [s3][s3]

| Board (title) | Nearest board (J) | What differs |
|---|---|---|
| `DetailArtikel2M4`, `DetailArtikel3M4`, `DetailArtikel4M4` | `SalinanArtikel2M4` (1.000) | **Functional duplicates.** 0 token-level differences from the source. Only a provenance comment differs |
| `SalinanArtikel2M4Salinan` | `SalinanArtikel2M4` (0.945) | Forked 2026-10-29 before the red article ribbon. Keeps a `BlogM3` dead link |
| `SalinanArtikelM4` | `SalinanArtikel2M4Salinan` (0.939) | Older article header ("Particle News" pattern), in the frozen row |
| `DesktopProdukM4Salinan` | `DesktopProdukM4` (0.990) | Near-exact: 13 diff ops. Links retargeted to its paired Salinan boards, related-product name size differs |
| `DesktopSkuM4Salinan` | `DesktopSkuM4` (0.856) | **Deliberate variant:** coverflow review carousel instead of a 3-column grid |
| `RecCreateM4Salinan1`, `SalinanProdukPageM4` | each other (0.976) | Forks from about 2026-10-16. 24 tokens each versus 62 on `RecCreateM4`; `RecCreateM4` now has 4,552 tags and lines versus 1,979 |
| `SalinanSkuPageM4` | `SkuDetailM4` (0.602) | Frozen fork |
| `SalinanBerandaM4` | `SalinanBeranda2M4` (0.861), `BerandaM4` (0.807) | UPVC and calculator sections rebuilt "100% same" as smsperkasa.com, 2026-10-27 |
| `SalinanBeranda2M4` | `SalinanBeranda3M4` (0.951) | Sales banner as a real component, UPVC card recipe reverted. Edited to 11-02 |
| `SalinanBeranda3M4` | `SalinanBeranda2M4` (0.951) | Adds "Produk yang baru Anda lihat" above the banner |
| `SalinanBlogM4Salinan` ("Salinan Blog 2", y=0) | `SalinanBlogM4` (0.927) | Greeting banner as a component, re-measured hero, list rows |
| `SalinanBlog2M4` ("Salinan Blog 2", y=-1200) | `SalinanBlogM4` (0.845) | Frozen row, same title as the board above |
| `SalinanBlog3M4` | `SalinanBlog5M4` (0.962) | "Jelajahi topik" card added 10-30; Topik container removed 11-02; 8 blocks copied from Blog 5 |
| `SalinanBlog4M4` | `SalinanBlog3M4` (0.920) | Head redesigned 10-31: icon chip rail replaced by 4 text tabs with a red underline |
| `SalinanBlog5M4` | `SalinanBlog3M4` (0.962) | Hero replaced 11-02: light hero with a photo on the right, new copy |

**DetailArtikel3 versus DetailArtikel4.** Same byte size (118,764). `cmp` finds exactly 4 differing bytes, at offsets 236, 848, 862 and 936, each changing a `3` to a `4` or a `d` to an `e`-adjacent version digit. All four are inside the header comment: the comment-stripped files hash identically (`792cc275`). [s2][s2] [s3][s3]

**Other lineage facts.**
- A comment states the convention: since the whole Mobbin 3 page was copied to Mobbin 4, file names changed but inner `<title>` values did not, so "identity is in canvas.json". [s9][comments]
- Comments name `y=-1200` the **"baris beku" (frozen row)** and `y=0` the **"baris hidup" (live row)**. The frozen row holds 8 boards, including `BerandaM4` and `UlasanM4Salinan`, the canonical picks. Freezing is not absolute: `SalinanSkuPageM4` and `SalinanProdukPageM4` carry notes dated 11-02. [canvas.json][canvas] [s2][s2] [s13][s13]
- **"Desktop M3" and "Mobbin 3" labels are stale, not a different language.** The note `n-desktop-m4-title` reads "Desktop M3 · bahasa Mobbin 3 pada 1440" (the id says m4, the text says M3), and 4 mobile titles say "Mobbin 3". Every `.dc.html` file name says M4. [canvas.json][canvas]
- Two boards share the title "Salinan Blog 2", and `<title>` is identical across the blog family. [canvas.json][canvas] [s1][s1]
- **56 dead link references:** `Artboard-pp1u.dc.html` ×28 (the logo link on 25 boards, some twice) plus 28 references to `*M3` boards that are not on the canvas (`RecCreateM3` ×11, `ArtikelM3` ×6, `DesktopProdukM3` ×3, others). `SkuDetailM4` links to a dead `UlasanM3`, so the mobile reviews board has 0 inbound links. [s4][s4]
- Links also cross breakpoints: mobile home links `DesktopProdukIndexM4` ×4, and `DesktopBerandaM4` links `RecCreateM4` ×2. [s4][s4]

### Inferences
- Prune or archive the 18 non-canonical boards before any token extraction. Three of them (Detail Artikel 2, 3, 4) carry no design information at all.
- **Sensitivity test:** swapping `BerandaM4`→`SalinanBeranda2M4` and `SalinanBlogM4`→`SalinanBlog5M4` keeps the top 6 mobile font sizes and the top 4 colours in nearly the same order (14 stays first at 227→223, `#5f5f5f` stays first). Token extraction is therefore safe whichever is chosen. The layout decision is not. [s13][s13]

### Gaps
- **Owner decision needed:** the home page (`BerandaM4` versus Salinan Beranda 2 or 3) and the blog (`SalinanBlogM4` versus Salinan Blog 3, 4 or 5). The newest work is on the Salinan boards, but no board links to them and no file marks a winner.
- No version history was available beyond dated notes. Last-note dates only approximate last edit.

## 2. Color

### Takeaway
Core colours are the most consistent part of the canvas: **every core token has one identical value on every board that defines it, and tokens win about 4:1 for text and 3:1 for backgrounds**. The drift sits around the core: literal hexes that duplicate tokens, greens and reds with several overlapping values, and tokens that are defined everywhere but never used, including `--price`.

### Cited Findings

**Tokens exist.** 96 distinct custom properties are defined in `:root` across all boards (16 to 73 per board). All are re-declared per file, because there is no shared stylesheet. Only three have conflicting values: `--sisi`, `--seksi` and `--font-harga`. [s4][s4]

**Token versus literal, canon:** [s12][s12]

| Property | Token | Literal |
|---|---|---|
| `color` | 875 | 223 |
| `background` | 484 | 153 |
| `box-shadow` | 152 | 72 |
| `fill` | 33 | 4 |
| `border` | 39 | 5 |

**Core usage, canon, token plus literal duplicate.** All-board roles are in brackets. [s5][s5]

| Role | Token | Value | Token uses | Literal uses | Notes |
|---|---|---|---|---|---|
| Text secondary | `--ink-2` | `#5f5f5f` | 570 | 0 | **More common than primary text** (text 1,100, icon 262) |
| Text primary | `--ink` | `#0a0a0a` | 455 | 36 | Also footer surface (surface 76) |
| Surface | `--surface` | `#ffffff` | 190 | 163 | Literal white is mostly text or icons on dark |
| Brand action | `--brand` | `#D70100` | 228 | 0 | text 271, icon 206, surface 101, border 9 |
| Brand logo | `--brand-hero` | `#FF0000` | 57 | 0 | **Icon role only, 123 of 123** |
| Hairline and sunken | `--line` | `#ececec` | 191 | 8 | **One token, two jobs:** surface 245, ring 130, border 79 |
| Strong line | `--line-kuat` | `#d4d4d4` | 6 | 0 | |
| Disabled text | `--ink-4` | `#c9c9cb` | 32 | 9 | |

**Drifted or orphaned colour tokens.** [s7][s7] [s12][s12] [s5][s5]
- **Defined but 0 uses on any board:** `--price #15763b` (32 boards), `--price-bg #eaf7ee` (23), `--chat-ikon #2563eb` (28), `--nav-aktif #A84C46` (10).
- **Token ignored, literal used instead:** `#A84C46` appears as a literal 54 times (all boards) while `--nav-aktif` has 0 uses. `#fdecec` appears as a literal 16 times in canon versus `--brand-subtle` 3 times.
- **Prices are not green.** The price recipe renders in inherited ink, in `--font-harga`. So the green "price" token is a leftover. [s10][s10]
- **`--awas-bg`** is defined on one board (`DesktopUlasanM4`) but referenced without a fallback on 11 others, which invalidates that declaration on those boards. [s12][s12] [s13][s13]
- **`--surface-2`:** notes say `#f4f4f5` was deleted on 2026-10-17, yet it is defined as `#f6f6f6` on 6 boards and used once. [s4][s4] [s7][s7]
- **Synonyms:** `--bintang` = `--star` (`#ffb800`), and `--bintang-garis` = `--star-stroke` (`#9a6700`). `--awas-bg` = `--brand-subtle`. [s4][s4]

**Near-duplicate clusters** (CIE76 deltaE ≤ 6, single linkage; the white-to-grey chain is a linkage artefact and was split by hand into the ramp below). [s5][s5]
- Blacks: `#0a0a0a` / `#000000`; `#1b191a` / `#1e1e1e`.
- Reds: `rgb(255,30,0)` / `#fe0100`.
- Slates: `#37566e` / `#3f536b`.
- Golds: `#ffb800` / `#fbbc05` (the second is Google's logo yellow, so the match is coincidental).

**Hue families in actual use.** [s5][s5] [s12][s12]
- **Reds, 7 values:** `#D70100` action, `#FF0000` logo, `rgba(255,0,0,.8)` product names (12 canon, 20 all, text), `rgb(255,30,0)` article ribbon (25 of 28 uses as surface), `#fe0100` (2), `#A84C46` active chip text, `#fdecec` tint.
- **Greens, 6 values:** `#157f3c` WhatsApp button (7 canon, literal), `#25d366` `--whatsapp` (1), `#16a34a` `--online-ikon` (2), `#4ade80` online dot in JS (4), `#15763b` and `#eaf7ee` (unused).
- **Blues:** `#1d4ed8` sent chat bubble on `DesktopSkuM4`. A note says this moved to `#fdecec` on 2026-10-19, so this board did not follow. `--biru-*` and `--keping-*` are confined to 4 boards.
- **Purple:** `#7c3aed`, `#6d28d9`, `#faf5ff`, `#ecdcfe` for a single purple tile with an icon disc (2 canon, 7 all).
- **Shadow tint split:** `rgba(17,25,33,α)` dominates, with `rgba(0,0,0,α)` in `--el-2` and `--el-3`.

**Every distinct colour value**, grouped by family. "boards" means canon boards. Counts include SVG attributes. [s5][s5]

%%COLORTABLE%%

**WCAG contrast.** Computed with the WCAG 2.x formula; alpha values composited on the stated background. [s5][s5] [s12][s12] [s14][s14]

| Pair | Ratio | AA normal text (4.5) | Where |
|---|---|---|---|
| `--ink` on white | 19.80 | Pass | Primary text |
| `--ink-2` on white | 6.39 | Pass | Secondary text, section labels |
| `--ink-2` on `--line` | 5.41 | Pass | Sunken rows |
| `--brand` on white, white on `--brand` | 5.39 | Pass | Links, CTAs |
| `--price` on white | 5.70 | Pass | Unused token |
| `--brand` on `--brand-subtle` | 4.72 | Pass | Tint chips |
| `#A84C46` on `#fdecec` | 4.85 | Pass | Active chip |
| White on `#157f3c` | 5.08 | Pass | WhatsApp button |
| White at 68% on `--ink` | 9.19 | Pass | Footer eyebrow |
| **`--brand-hero` on white** | 4.00 | **Fail** (passes 3:1) | Logo only, so acceptable as graphics |
| **White on `rgb(255,30,0)`** | 3.86 | **Fail** except large | Article ribbon |
| **`rgba(255,0,0,.8)` on white** | 3.64 | **Fail** | **14px product names, 12 canon declarations** |
| **`--online-ikon` on white** | 3.30 | **Fail** except graphics | Status icon |
| **`--chat-mati`, white on it** | 2.54 | **Fail** | Disabled send, exempt only if truly disabled |
| **`--whatsapp` on white** | 1.98 | **Fail** | 1 canon `color` use |
| **`--star` on white** | 1.73 | **Fail** | Rescued by `#9a6700` stroke (4.87) |
| **`--ink-4` on white** | 1.65 | **Fail** | Disabled text, separators |
| **`#c9c9cb` on `#ececec`** | 1.40 | **Fail** | Disabled filter chip |
| `--line` on white | 1.18 | n/a | Hairline, far below 3:1 for UI boundaries |

### Inferences
Proposed colour tokens (values are as found, renames are suggestions):

```text
neutral.0      #ffffff   surface
neutral.100    #ececec   split into border.subtle AND surface.sunken (now one token, two jobs)
neutral.200    #d4d4d4   border.strong
neutral.300    #c9c9cb   text.disabled (absorb #dcdcde, #d6d6db, #e4e4e6)
neutral.700    #5f5f5f   text.secondary
neutral.950    #0a0a0a   text.primary, surface.inverse (absorb #000000, #1e1e1e, #1b191a)
brand.action   #D70100   CTA, links, active marks
brand.logo     #FF0000   logo ONLY; never UI
brand.tint     #fdecec   alerts, sent bubbles, active chips (drop --awas-bg)
brand.onTint   #A84C46   wire up --nav-aktif, replacing 54 literals
success.solid  #157f3c   WhatsApp CTA (passes with white)
whatsapp.brand #25d366   glyph on dark only
rating.fill    #ffb800, rating.stroke #9a6700, rating.empty #dcdcde
```
- There is **no mid-grey** between `#c9c9cb` and `#5f5f5f`, since `--ink-3` was merged on 2026-10-17. A real system needs an accessible placeholder step.
- **Remove or replace `rgba(255,0,0,.8)`.** It is an off-ramp red and fails AA on the page type that sells the product. `--brand` already passes.
- No colour ramps exist (no 50 to 900 scale). The palette is a set of named roles.

### Gaps
- Actual on-screen backgrounds for every text colour were not computed, since no boards were rendered. Contrast is tested on inferred pairings, not an exhaustive element walk.

## 3. Typography

### Takeaway
There is a real, token-driven type ladder (**token share about 84% for mobile and 85% for desktop font sizes**) with a clear heading recipe, but it is **two different ladders with different role names per breakpoint**, and neither line-height nor letter-spacing has any tokens. A **typeface conflict** is also unresolved: the canvas uses the SF system stack, Figma uses Inter, and production uses Lato.

### Cited Findings

**Families.** [s7][s7] [s6][s6] [s13][s13]
- **Body:** `-apple-system,"SF Pro Text",system-ui,"Helvetica Neue",sans-serif` on all boards. No web font for body, and 0 `@font-face` rules.
- **Price:** `--font-harga` = JetBrains Mono on 32 boards, Source Code Pro on `RecCreateM4Salinan1`. Applied by `[data-harga]` in helmet CSS. Google Fonts link (`wght@400;700;800`) on 14 boards plus the Source Code Pro link on 1.
- **Conflict documented in notes:** Figma's equivalents are Inter styles, and a note says weight 500 "is not valid in the production tier: Lato only has 400/700/900, and `scripts/contract-rules.ts` rejects `font-weight: var(--bobot-medium)` as a Tier 1 violation". 500 is the second most used weight here (205 canon declarations).

**Font sizes, canon, resolved px.** Counts include 8 `html{62.5%}` rules, omitted here. [s6][s6]

| px | Mobile | Token | Desktop | Token |
|---|---|---|---|---|
| 8 | 3 | literal, outlier | 2 | literal, outlier |
| 9.5 | 4 | `--teks-sup` ("Rp" superscript) | 1 | `--teks-sup` |
| 10 | 26 | `--teks-micro` (fraud ribbon) | 6 | `--teks-micro` |
| 11 | 73 | `--teks-tiny` | 52 | `--teks-tiny` |
| 12 | 54 | `--teks-chip` 14 + literal 40 | 22 | **literal only** |
| 13 | 89 | `--teks-meta` | 141 | `--teks-meta` |
| 14 | **227** | `--teks-body` | 111 | `--teks-body` |
| 15 | 1 | literal, outlier | | |
| 16 | 11 | literal | 10 | literal |
| 17 | 5 | `--teks-price` | 0 | `--teks-advantage` (0 canon uses) |
| 18 | | | 5 | `--teks-subhead` |
| 20 | 49 | `--teks-section` 39 + literal 10 | **127** | `--teks-lead` |
| 22 | | | 11 | `--teks-price-lg`, `--teks-subsection` |
| 23 | 4 | literal, outlier | | |
| 26 | | | 27 | `--teks-section-md` |
| 28 | 8 | `--teks-page` | | |
| 29 | | | 7 | `--teks-cta` |
| 30 | 2 | literal | 1 | `--teks-section-lg` |
| 32, 35, 56, 60 | | | 1, 3, 1, 1 | literal, outliers |
| 44 | | | 10 | `--teks-display` |

**Token versus literal:** mobile 477 / 88, desktop 467 / 80. The 16 boards use 16 distinct values on mobile and 20 on desktop. All boards: 22 and 21. [s6][s6]

**Heading recipes, canon.** [s14][s14]

| Level | Mobile (dominant) | Desktop (dominant) | Drift |
|---|---|---|---|
| h1 | 28 / 700 / lh 1.2 / -0.01em (5 of 7) | 44 / 700 / -0.01em (6 of 8) | m: 30/900; d: 35/700, 56/900 |
| h2 section label | **20 / 500 / UPPERCASE / `--ink-2` / +0.12em / lh 1.35 (23 of 27)** | **26 / 500 / UPPERCASE / +0.1em / lh 1.2 (21 of 26)** | d: 22 and 30 once each |
| h3 | 14 / 500 / UPPERCASE / +0.12em (4 of 9) | 22 / 500 / UPPERCASE / +0.1em (4 of 10) | Weak consensus |

**Other properties, canon, mobile / desktop.** [s6][s6] [s14][s14]
- **Weights:** 700 (206 / 185), 500 (84 / 121), 600 (56 / 57), 300 (25 / 36), 800 (28 / 17), 900 (14 / 14), 400 (9 / 5). Tokens 800, literal 57. Regular 400 is rare because body copy inherits it.
- **Line-height (no tokens, 644 literals):** 1.35 (181 / 70), 1.2 (79 / 89), 1.45 (39 / 31), 1.3 (26 / 29), 1.25 (11 / 19), 1.5 (2 / 20), 1.1 (1 / 7). Outliers: 0.9, 0.95, 1, 1.04, 1.06, 1.12, 1.13, 1.15, 1.4, 1.55, 1.6, 1.65, `2rem`.
- **Letter-spacing (no tokens, 172 literals):** mixed units. 0.12em (29 / 1), 0.1em (8 / 30), 0.06em (18 / 13), 0.01em (10 / 10), 0.12rem (7 / 8), 0.02em (6 / 7), -0.01em (4 / 5).
- **Text treatments:** `uppercase` 65 / 51, `tabular-nums` 34 / 25, `text-align:justify` 48 total, `hyphens` 61 total, line-clamp 38 total.

### Inferences
Actual scale, per breakpoint:

```text
Mobile  : 9.5 · 10 · 11 · 12 · 13 · 14 · 17 · 20 · 28       (outliers 8, 15, 16, 23, 30)
Desktop : 9.5 · 10 · 11 · 12 · 13 · 14 · 18 · 20 · 22 · 26 · 29 · 44   (outliers 8, 16, 30, 32, 35, 56, 60)
```
- A note records that mobile was "reduced from 15 to 7 sizes" on 2026-10-17 (28/20/17/14/13/11/9.5), with 12 and 10 reopened afterwards. The ladder is genuinely being curated, and the code matches it. [s1][s1] [s9][comments]
- **Desktop body is effectively 20px for prominent content** (`--teks-lead` ×127, SKU row names, prose) with 13 and 14 as metadata. A note states prose is "14 px mobile, 20 px desktop". This is a large jump to rationalise.
- **Rename by role, across breakpoints.** The same role has different token names today (mobile `--teks-section` 20 versus desktop `--teks-section-md` 26). Use a single role with responsive values.
- **The most distinctive typographic signature:** quiet uppercase grey section labels (`--ink-2`, medium, tracked) rather than bold black headings, and monospace tabular prices with a superscript "Rp".
- Weights 300, 500, 600, 800 cannot survive a Lato production tier as written. Decide the typeface first, because it dictates the weight ramp.

### Gaps
- Whether Lato is still the production direction cannot be determined from this canvas, since `tokens/`, `scripts/contract-rules.ts` and the Figma file 'New Design System' are mentioned in notes but not available here.
- Whether `hyphens:auto` works for Indonesian in target browsers was not tested, and needs a device check given 61 declarations.

## 4. Spacing and layout

### Takeaway
**There is no 4px or 8px grid.** Spacing is a small set of named role values (12, 15, 20, 30, 60, 120), a "50/50 half-gutter" margin convention, and many one-off literals (71% to 79% literal). **Pages are not responsive:** mobile and desktop are separate fixed-width boards with effectively no breakpoints.

### Cited Findings

**Grid fit** of non-zero numeric spacing, canon. Half-gutter values depress these numbers, so treat them as evidence against a strict grid, not a precise measure. [s6][s6]

| Base | Mobile | Desktop |
|---|---|---|
| 2px | 68.7% | 76.7% |
| 3px | 46.8% | 46.2% |
| 4px | 31.9% | 45.3% |
| 5px | 23.7% | 27.6% |
| 8px | 6.1% | 21.9% |

- 34 and 35 distinct non-zero values. Fractional px values: 149 and 136 (4.5, 2.5, 3.5, 7.5, from halving odd gutters). [s6][s6]
- **Token versus literal spacing:** mobile 804 / 1,932, desktop 604 / 2,218. [s6][s6]

**Spacing tokens.** [s4][s4] [s11][s11] [s7][s7]

| Token | Mobile | Desktop | Canon uses | Role (per notes) |
|---|---|---|---|---|
| `--rapat` | 12 | 12 | 875 | Inline and tight gaps |
| `--dalam` | 20 | 20 | 197 | Inside a section or card, heading to content (14 of 14 per a note) |
| `--sisi` | **15 or 16** | **120** | 114 | Page edge. 15 on Beranda, Kategori, Index, Produk, SKU; 16 on Blog and Artikel. **Drift** |
| `--talang` | 15 | none | 51 | Page edge (mobile duplicate of `--sisi`) |
| `--seksi` | clamp(60, 7.5svh, 80) | 60 | 141 | Between sections |
| `--jarak-y-antar` | clamp(60, 7.5svh, 80) | none | 48 | Mobile duplicate of `--seksi` |
| `--jarak-y-dalam` | 15 | none | 44 | Row spacing inside a section |
| `--jarak-x-dua` / `--jarak-x-tiga` | 30 / 15 | none | 9 / 3 | Gutters for 2-up and 3-up |
| `--footer-jarak` / `--footer-pad` / `--selokan-dalam` | none | 72 / 56 / 48 | 16 / 8 / 12 | Desktop footer. Desktop-only names |

**Half-gutter "50/50" rule.** Each row item carries half its gutter on each side, `gap` is set to 0, and `data-tepi`, `data-tepi-y`, `data-tepi-kisi` plus `!important` helmet rules cut the outer half (1,001 `data-tepi` attributes, all boards). `calc(var(--rapat) / 2)` alone appears 350 + 274 times in canon. **Effective gutters, from equal left and right margin pairs:** [s1][s1] [s10][s10]
- Mobile: 12 ×175, 8 ×58, 10 ×50, 6 ×48, 9 ×26, 5 ×17, 30 ×10, 20 ×10.
- Desktop: 12 ×132, 16 ×107, 10 ×80, 6 ×58, 24 ×49, 8 ×46, 7 ×35, 60 ×24, 20 ×22, 48 ×13.
- The raw "6px ×491" and "4px" peaks are artefacts of this convention, and a token extractor would misread them.

**Runtime "optical" section spacing.** `_jarakHitung` on 7 canon mobile boards (19 all, with 2 variants) measures rendered height and writes margins via JS: `gap = round(clamp((h_above / h_below)^0.35, 0.75, 1.40) × basis)`, where `basis` is `--jarak-y-antar`. A note records that five tuning attempts failed because this engine overwrites margins on direct children of `[data-jarak]`. Desktop canon boards do not use it. [s10][s10] [s11][s11] [s3][s3]

**Layout.** [s6][s6] [s11][s11]
- **Page root:** `width:36rem` or `width:144rem`, `max-width:100%`, `margin:0 auto`, `min-height:100vh`. Mobile would stay 360 wide on a tablet.
- **Mobile container formula (per note):** 360 − 2×15 = 330; 2 cards @150 + gutter 30; 3 cards @100 + gutter 15. **Desktop content width:** 1440 − 2×120 = 1200.
- **Breakpoints:** canon has only 2 `min-width` media queries, both on `RecCreateM4` for one `[data-nama]` max-width. 0 `vw`, 0 container queries. `svh` and `vh` appear only in section clamps and `min-height`. Other at-rules: `prefers-reduced-motion` and `@supports not (height: 1svh)`.
- **Mobile grid:** `repeat(2,…)` ×4, `repeat(3,…)` ×3, `repeat(4,…)`, `repeat(1,…)`; `flex` with horizontal scroll rails. 16 scroll-snap declarations.
- **Desktop grid (15 patterns):** `repeat(2,…)` ×15, footer `minmax(0,1.4fr) repeat(3,minmax(0,1fr))` ×8, `repeat(3,…)` ×6, `repeat(6,…)` ×4, `repeat(4,…)` ×3, `25% 1fr` ×2 (filter sidebar), `8fr 4fr` (article), `1fr 20% auto` (SKU row).
- **Display, canon:** flex 760, block 515, grid 293, inline-flex 185.
- **Fixed heights:** header 56 (mobile), 72 (desktop). Sticky chrome: 25 declarations on desktop, 9 on mobile. Fixed: 20 mobile, 3 desktop.
- **Mobile footer** has `padding-bottom:25rem` (250px) on canon boards, apparently to clear the floating bar.

### Inferences
Proposed spacing tokens, based on what is used rather than an imposed grid:

```text
space.tight   12   (--rapat)
space.inner   20   (--dalam)
space.edge    15 mobile → 120 desktop (settle 15 vs 16)
gutter.2up    30   gutter.3up 15 (mobile); 12 / 16 / 24 (desktop)
section       clamp(60, 7.5svh, 80) mobile; 60 desktop
micro         2, 4, 6, 8, 10
```
- The half-gutter pattern exists because the canvas tool's property panel favours inline values. **In production components, replace it with `gap`.** It is an authoring workaround, not design intent, and accounts for much of the markup weight.
- Decide explicitly whether to keep the height-ratio spacing engine. It is unusual, it requires layout measurement at runtime, and it can cause layout shift. A static `--section` token would be the simpler path.
- **Responsive behaviour between 360 and 1440 is undesigned.** Everything from 400 to 1,200px must be defined from scratch.

### Gaps
- Actual computed section gaps from `_jarakSeksi` were not observed because boards were not rendered.

## 5. Shape and elevation

### Takeaway
The radius ladder is well tokenised and quite consistent (86% token). Elevation is a three-way mix: liquid glass tokens, an untokenised card shadow, and rings drawn with `box-shadow` instead of borders.

### Cited Findings

**Radius, canon, resolved.** Tokens 450, literals 75. [s6][s6] [s14][s14]

| Token | px | Mobile | Desktop | Role |
|---|---|---|---|---|
| `--pill` | 999 | 133 | 73 | Chips, circular buttons |
| `--tile`, `--control` | 5, 5 | 28, 16 | 42, 13 | Thumbnails; toolbar controls. Deliberately separate roles per a note |
| `--action` | 9 | 19 | 33 | Buttons, search field |
| `--card` | 14 | 12 | 13 | Cards |
| `--sheet` | 16 | 29 | 18 | Help-centre rows, sheets |
| `--quote` | 18 | 4 | 4 | Quote cards |
| `--island` | 26 | 4 | 2 | Floating islands |
| `--panel` | 22 | 0 | 0 | **Unused on any board** |
| literal `50%` | | 41 | 23 | Circles |
| literal others | 2, 4, 8, 12, 20 | 5 | 3 | Drift; a note calls these intentional |

**Borders.** Canon `border` declarations are mostly resets: `border:0` ×153. Real ones: 0.1rem solid `#ececec` ×30, `#d4d4d4` ×2, `#dfe4f0` ×3, 0.15rem ×3, 0.2rem ×3. **Rings are drawn with `box-shadow`:** `inset 0 0 0 .1rem var(--line)` ×24, hairlines `0 -0.1rem 0 var(--line)` ×20, `inset 0 -0.1rem 0 var(--line)` ×12. [s6][s6]

**Elevation.** [s6][s6] [s4][s4]

| Name | Value (rem) | Canon uses | Status |
|---|---|---|---|
| Glass bar (`--cair-rim`, `--cair-bayang`) | 6-layer inset rim + `0 .6 1.4 rgba(17,25,33,.16), 0 .1 .2 rgba(17,25,33,.10)` | 77 | Token |
| Card (untokenised) | `0 .1 .2 rgba(17,25,33,.06), 0 1 2.4 -1.4 rgba(17,25,33,.20)` | 41 | **Literal; most common card shadow has no token** |
| `--el-2` | `0 .2 1 rgba(0,0,0,.08), 0 .1 .2 rgba(0,0,0,.06)` | 12 | Token |
| `--el-3` | `0 .8 2 rgba(0,0,0,.14), 0 .2 .6 rgba(0,0,0,.08)` | 2 | Token, on 7 boards |
| `--bayang-kartu` | | 2 | Token, on 4 boards. Competes with the literal above |
| `--kaca-bayang` | 3 layers | 2 | Token |

**Liquid glass ("kaca cair") is the signature material.** `--cair` and `--cair-tombol` are radial white gradients, `--cair-tombol-blur` / `--cair-blur` use `blur(1.8rem) saturate(160%)` and `blur(1.4rem) saturate(165%)`. Backdrop-filter: 92 mobile and 82 desktop declarations, and a specular sheen `radial-gradient(62% 100% at 50% 42%, …)` ×61. Comments say glass is reserved for the bottom bar and island, with panels moved to white. [s6][s6] [s3][s3] [s9][comments]

**Opacity and z-index.** Opacity is only 10 declarations (states only; no opacity tokens). **Z-index: two inconsistent ladders.** Mobile 0, 1, 2, 3, 5, 9999, 10000 to 10003. Desktop 1, 2, 3, 30, 35, 40, 60, 10002, 10003. [s6][s6]

### Inferences
```text
radius: xs 5 (tile, control) · sm 9 (action) · md 14 (card) · lg 16 (sheet) · xl 18 (quote) · 2xl 26 (island) · full
shadow: card (promote the 41-use literal) · el-2 · el-3 · glass (rim+cast)
z:      base 1-3 · sticky 30-40 · overlay 60 · modal 10000+ (normalise)
```
- Delete `--panel`, merge `--bayang-kartu` with the card literal.
- **Rings via `box-shadow` were a deliberate decision** (per the `--line` note: a hairline on a sunken base disappears). Keep the visual result, but real borders may be simpler in production, except on sunken surfaces.
- Glass needs a non-`backdrop-filter` fallback and a performance review on low-end Android, which matters for this market. This is an inference, not measured.

### Gaps
- No `prefers-reduced-transparency` handling was found, and glass legibility over photos was not measured.

## 6. Motion and state

### Takeaway
Entrance motion is coherent: one easing curve and a small keyframe set, with reduced-motion handling on half of canon. **Interactive state design is the largest gap: effectively 0 hover styles, 3 `:focus-visible` rules, and `outline:none` 28 times.**

### Cited Findings

**Motion, canon.** [s6][s6] [s11][s11] [s14][s14]
- **Easing:** `cubic-bezier(.16,1,.3,1)` dominates (expo-out), plus `ease`, `ease-out`, `linear`.
- **Durations:** transitions at 150, 160, 200, 220, 240, 260, 420, 440ms (31 declarations). Animations at 240, 260, 300, 320, 380, 420, 440, 460, 520ms. Marquees 46s and 48s linear.
- **Keyframes (15 in canon, 16 all):** `sheet-up`, `scrim-in`, `baris-in`, `bantu-in`, `bantu-pop`, `pulau-naik`, `chip-a`/`chip-b` (same definition; name pair forces restart), `hdr-thumb`, `masuk`, `lazy-spin`, `pita`/`geser` (same marquee, 2 names), `revFillA`/`revFillB` (progress bars). Typical: opacity 0 → 1, translateY 10 to 16px, scale .90 to .98.
- **Reduced motion:** `@media (prefers-reduced-motion: reduce)` on 8 of 16 canon boards (21 of 34), 18 rules. JS uses `matchMedia` too (4 canon).
- **Autoplay:** `setInterval` ×3 for carousels with pause on hover, focus and drag (state keys `revHover`, `revFocus`, `revDrag`).

**States, canon.** [s6][s6] [s7][s7] [s14][s14]

| State | Evidence | Assessment |
|---|---|---|
| `:hover` | 3 selectors: 2 pause a marquee, 1 is input autofill | **No hover style on any button, link or card** |
| `:focus-visible` | 3: range slider ×2, review viewport (offset only) | **Practically absent** |
| `outline:none` | 28 declarations, with no replacement | **Fails keyboard visibility** |
| `:focus-within` | 2 (marquee pause) | |
| `:active` | 9: `[data-grid]:active` scale(.92 to .96), tile scale(.97), slider grab | Mobile-style press feedback exists |
| `:checked` | 2: radio with thick ink border (0.4 to 0.5rem) | |
| Disabled | 23 `disabled` attrs; style `background:#ececec;color:#c9c9cb;cursor:default` in JS; `cursor:not-allowed` ×5 | Inconsistent cursors, very low contrast |
| Selected | `aria-current` ×27, `aria-pressed` ×23, `aria-expanded` ×34; active chip `#A84C46` on `--brand-subtle` bold, or glass drop on desktop | **Two different active-chip recipes by breakpoint** |

**Interactivity is JS-state driven:** events `onClick` 603, `onChange` 79, `onFocus` 12, pointer events 7 each (all boards). `setState` 252 in canon. [s6][s6] [s11][s11]

### Inferences
```text
motion.ease.out    cubic-bezier(.16,1,.3,1)
motion.fast 150-160 · base 220 · slow 420-440 · enter 520
press.scale        .96
```
- Hover and focus have to be **designed from zero** for desktop. The 10 desktop boards are, in state terms, touch designs at 1440.
- The `chip-a`/`chip-b` and `pita`/`geser` duplicates can merge.

### Gaps
- Script-driven hover via `onPointerEnter` (7 uses, all boards) appears tied to carousels. Other JS-computed hover styling cannot be ruled out without running the boards.

## 7. Iconography and imagery

### Takeaway
A custom, hand-authored inline SVG set that looks Lucide-like (24 grid, round caps, stroke) but is **not Lucide**, has no consistent stroke or size, and contains near-duplicate glyphs. Imagery is disciplined: all `/_blob/`, 4:3 for products, `object-fit: cover`, full alt attribute presence.

### Cited Findings

**Icons.** [s7][s7]
- **Volume:** 1,241 inline `<svg>` with 103 distinct geometries (all boards); 474 and 87 in canon. No sprite, no `<use>`, no icon font.
- **Style:** stroke 372, fill 102 (canon). viewBox `0 0 24 24` on 405 of 474, plus 16, 20, 23, 14, 31 grids.
- **Stroke widths, canon (17 distinct):** 2 ×106, 1.8 ×77, 1.9 ×55, 2.2 ×43, 2.4 ×19, 2.6 ×19, 1.2 ×16, 1.7 ×16, 1.5 ×9, 1.725 ×8, 1.75 ×6, 2.1 ×6, others.
- **Rendered sizes, canon (over 20 distinct):** 18 ×105, 15 ×63, 16 ×53, 21 ×38, 17 ×32, 24 ×29, 19 ×25, 20 ×23, 26 ×16, 22 ×16, 14 ×12, 25 ×11. Some sizes are computed (`{{ sk.ikon }}`).
- **Library match:** 0 hits for 8 Lucide path signatures (`m9 18 6-6-6-6`, `M18 6 6 18`, `m21 21-4.3-4.3`, others), 1 Feather, 2 Heroicons, 2 Material or Tabler signatures. No `lucide` class. Signatures were written from memory of those libraries' path grammar, so this is strong rather than exhaustive evidence.
- **Duplicates:** chevron right `M9 5l7 7-7 7` (55) and `M9 18l6-6-6-6` (8). Chevron down `M6 9.5l6 6 6-6` (13) and `M6 9l6 6 6-6` (6). Close `M6 6l12 12M18 6L6 18` (27) and `M6.4 6.4l11.2 11.2…` (16). Arrow `M5 12h13M12.5 6…` (11) and `M5 12h13M12.6 5.6…` (2). Search `circle r7` (13) and `ellipse rx 8.789` (8). Two phone, three chat, two star glyphs. Two logo geometries (150×44 and 102×30).
- **Third-party glyphs:** WhatsApp, Google 4-colour, Facebook `#1877f2`, inline.
- **Top icons, canon:** chevron, close, star, back arrow, phone, pin, search, warning triangle, arrow, WhatsApp, chat, menu, clock, document, headset, share, home, send, shield.

**Images.** [s7][s7] [s6][s6] [s9][comments]
- **Volume:** 248 `<img>` (all), 101 (canon). 0 external image hosts. All use `/_blob/{hash}`. A note says the format allows only uploaded blobs and forbids `<iframe>`, `<object>`, `<embed>`.
- **Alt:** 0 missing attributes in canon: 45 literal, 32 dynamic, 24 empty (decorative, with an `aria-label` on the parent link).
- **Loading:** `loading="lazy"` on 60 of 101. No `width`/`height` attributes anywhere, so aspect ratio is CSS-only.
- **Aspect ratios, canon:** 4/3 ×18 (product and thumbnail standard), 360/150 ×18 (help-centre banner), 16/9 ×6, 1/1 ×4, plus one-offs derived from file dimensions (1200/400, 2000/971, 560/365, 1447/1087, 1170/675, 1448/1086, 1713/1105, 3/2).
- **Fit:** cover 72, contain 10.
- **Placeholder:** the product index shows a generic icon on `--line` when no photo exists (`p.takFoto`).

### Inferences
- **Adopt a real icon library rather than preserve these.** Lucide would be a close visual match with minimal redesign: 24 grid, round caps, stroke near 2. The 87 geometries would reduce to about 35 to 45 distinct concepts (an estimate from the top list).
- Normalise to 3 sizes (16, 20, 24) and 1 to 2 strokes.
- Keep **4:3** as the product image token, 16:9 for video and article, 1:1 for avatars and tiles.

### Gaps
- Not measured: whether any path matches another library not tested (Iconoir, Phosphor at 24, Untitled). The menu `M20.75 7a.75.75…` is a different grammar, suggesting at least one external source.

## 8. Component inventory

### Takeaway
About 35 real components recur, with strong semantic consistency but **zero reuse mechanism**: `<dc-import>` appears 0 times, and everything is copy-pasted, with 67.6% of canon bytes living in lines shared by two or more boards. The most complex and most valuable components are the price list, filter and sort, help centre, and glass floating navigation.

### Cited Findings

**Duplication.** [s10][s10] [s11][s11]

| Block | Instances (canon) | Distinct (canon) | Instances (all) | Distinct (all) | Average size |
|---|---|---|---|---|---|
| `<header>` | 17 | 9 | 40 | 17 | 7.5 KB |
| Fraud ribbon | 12 | 2 | 28 | 4 | 1.9 KB |
| `:root` block | 16 | 11 | 34 | 19 | 2.5 KB |
| Spacing engine `_jarak*` | 7 | 1 | 19 | 2 | 4.5 KB |
| Help centre | 4 | **4** | 11 | 6 | **48 KB** |

Canon templates: `<sc-for>` 201, `<sc-if>` 421, `{{ }}` 2,275.

**Inventory.** "m" and "d" mean mobile and desktop canon boards. [s10][s10] [s8][s8] [s12][s12]

| # | Component | Used on (canon) | Variants | States and behaviour |
|---|---|---|---|---|
| 1 | **Fraud warning ribbon** | All except m/d Ulasan and `DesktopSkuM4` (30 of 34 all) | 2 | Dismiss (`awas`), 10px, `#fdecec`, red bold label, link |
| 2 | **Site header** | All except `UlasanM4Salinan`; 2 per blog | m: logo + menu (56); d: logo + Kategori + search + menu (72) | Sticky on d, z40 |
| 3 | **Compact scroll header** | `RecCreateM4`, `SkuDetailM4` | Thumb animates in | `hdr-thumb`, `gulir` state |
| 4 | **Footer** | All except `UlasanM4Salinan`, not `<footer>` | m: stack, 250 bottom pad; d: `1.4fr + 3×1fr` | m has `foot` state key, inverse `--ink` |
| 5 | **Breadcrumb** | Produk index and Kategori m/d, `DesktopSkuM4`, `DesktopArtikelM4` | 1 | "Remah roti" nav. **Absent on `RecCreateM4`, `DesktopProdukM4`** |
| 6 | **Search field** | All d, `RecCreateM4`, `SkuDetailM4`, `SalinanBlogM4` | Header 46 tall, ring, action radius | Clear, in-header |
| 7 | **Search dialog** | `RecCreateM4`, `SkuDetailM4` | Sheet, recents, results | Includes a **fake on-screen keyboard** (`kbNum`, `kbShift`), prototype artefact |
| 8 | **Price-list row (SKU row)** | `RecCreateM4`, `DesktopProdukM4` | Table, card (`tampilan`), zebra | Name, mono price, "per batang", chevron link. d row 56+ grid `1fr 20% auto` |
| 9 | **Price block** | Home, Produk, SKU, Ulasan d | sm 17, lg 22, page 28, with `[data-harga]` | Superscript Rp, tabular, unit caption |
| 10 | **View toggle** | Produk m/d | Table, cards | `aria-pressed`; `data-seg-thumb` segmented on m |
| 11 | **Filter panel** | Produk m/d | m: dialog with tabs (`ocSeg`); d: `aside` sidebar | Size and thickness chips, `ukuranBuka`, `tebalBuka`, reset; props `panelFilter`, `filterAwal` |
| 12 | **Sort** | Produk m/d | Dialog radiogroup; d also inline | `urut`, `urutOpen` |
| 13 | **Pagination, lazy list** | d: `DesktopProdukM4`, `DesktopUlasanM4`; m: `RecCreateM4` | Numbered vs lazy spinner | `hal`; `limit`, `data-lazy-sentinel`, `lazy-spin` |
| 14 | **Empty state** | Produk m/d | 1 | "Tidak ada SKU untuk kombinasi ini" |
| 15 | **FAQ accordion** | Produk, SKU m/d | Show-more toggle | `faqBuka`, `aria-expanded` |
| 16 | **Star rating** | Home, Produk, SKU, Ulasan, some blog | 16 grid, `#ffb800` + `#9a6700` | `role="img"` label |
| 17 | **Review card** | Home, SKU, Ulasan | m: slide; d: grid; quote radius 18 | Bold highlights, Google glyph |
| 18 | **Review carousel** | `BerandaM4`, `SkuDetailM4` (d: paged `ul`) | Dots with progress fill | Autoplay, drag, `revRM` |
| 19 | **Review marquee** | Ulasan m/d | 46s, 48s | Pause on hover and focus (d has `jeda` button) |
| 20 | **Star filter** | `DesktopUlasanM4` | 1 | `saring`, `role=group` |
| 21 | **Hero banner carousel** | Home m/d | 1 | Dots, scroll spy `_bnrSpy` |
| 22 | **Photo gallery** | `RecCreateM4`, `SkuDetailM4`, d equivalents | Dots, thumbs | `foto`, `hero` |
| 23 | **Product card** | Home, related products, SKU "Ukuran Lainnya" | 4:3, `--tile`, name, "Mulai Rp", variants | Rail or grid |
| 24 | **Category tile** | Home, Kategori, Index | 2 to 6 up | Icon fallback |
| 25 | **Horizontal rail** | Home, Blog, SKU | 48% wide, 30 gutter | Snap, arrows on d |
| 26 | **Before-after comparator** | Home m/d | 1 | Invisible `range` plus `clip-path`, focus-visible style |
| 27 | **Calculator and promo CTA** | Home, Produk | Image + text | Links to `/tools/kalkulator-*` |
| 28 | **Consultation banner** | Produk, SKU, Blog, Article | Glass or brand button | "Konsultasi Sekarang" ×10 |
| 29 | **Bottom glass bar** | `RecCreateM4`, `SkuDetailM4`, `SalinanBlogM4`, `SalinanArtikel2M4` | 52 circular buttons | Hide on open, `barGaya`, grid-to-X icon morph |
| 30 | **Section sheet and nav** | Same 4 m boards | Grid `data-set`, `data-scrim` | `sheet-up`, scroll spy `_spy` |
| 31 | **Desktop island** | `DesktopProdukM4`, `DesktopSkuM4` | 72 glass, `--island` | `sekPulau`, `pulau-naik` |
| 32 | **Section rail** | `DesktopProdukM4`, `DesktopSkuM4` | Sticky at 124 | Glass active chip |
| 33 | **Help centre** | `RecCreateM4`, `SalinanBlogM4`, `DesktopProdukM4`, `DesktopSkuM4` | Tabs: menu, WhatsApp, live chat | Office-hours status `_jamKerja`, chat log `role=log`, CSAT, form (name, WA, email), emoji |
| 34 | **Blog row and card** | Blog m/d, article | 64 thumb 4:3, title, date | Category chip filter (`kat`) |
| 35 | **Category chip rail** | `SalinanBlogM4`, `DesktopBlogM4`, `DesktopArtikelM4` | Icon chips | `aria-current`, `#A84C46` |
| 36 | **Article body** | Article m/d | Prose, h2, h3, quote, table, figure | TOC (`nav` "Daftar isi"), overflow-x table, justify |
| 37 | **Red article ribbon** | `SalinanArtikel2M4` | Full-bleed `rgb(255,30,0)` | Mobile only |
| 38 | **Share, copy** | Produk, SKU m/d | Icon button | `disalin` on `DesktopSkuM4` only |
| 39 | **Partner logos, tags** | Produk m/d | "Dipercaya Mitra", "Pencarian terkait" | |

**Buttons have no scale.** [s10][s10]
- Primary CTA: `--brand`, white, `--action` 9, min-height **30**, padding 4/12, 13px bold ("Konsultasi Sekarang").
- Desktop banner CTA: same shell at font size **29px** ×6.
- Form buttons: `--control` 5, height **44 or 48**, 14px, in `--brand` or `#157f3c`.
- Pill: 50 tall, 14px bold, ×1.
- Chips: 28, 32, 36, 40 pill or control.
- Glass: 52 (mobile) and 72 (desktop) circles, plus 40-tall chips.
- Row-as-button: `--surface`, min-height 76, `--sheet` radius, ×39.

**Props expose only a few states:** `panelFilter` (closed, open) on `RecCreateM4`, and `tampilan` (table, card), `filterAwal` (empty, selected) on `DesktopProdukM4`. All other boards expose only `$preview`. [s1][s1]

### Inferences
Suggested build order for a design system, by reuse and business importance:
1. Foundations and tokens.
2. Button, IconButton, Chip, Input, Radio, Accordion, Rating, Price, Tag.
3. Header, Footer, Breadcrumb, FraudRibbon.
4. ProductCard, SKURow, PriceTable, FilterPanel, SortMenu, Pagination, EmptyState.
5. Carousel, Rail, Sheet, Dialog, GlassBar, Island.
6. HelpCentre, ReviewCard, ArticleBody.

- The fake keyboard is a prototype artefact, and should not become a component.
- The 4 divergent help-centre copies (48 KB each) are the largest merge risk.

### Gaps
- Heuristic detection: the matrix used text and attribute regexes, then spot checks. Some counts include CSS or script references, so the variant counts above are approximate.

## 9. Domain and content

### Takeaway
SMS Perkasa (PT. Sumber Makmur Surya Perkasa) is an Indonesian steel and building-materials distributor selling a very large SKU catalogue through **consultative sales on WhatsApp, not a cart**. The system's primary pattern is a long, filterable spec-and-price list, not a typical e-commerce grid.

### Cited Findings
- **Language:** `lang="id"` on 34 of 34 boards. [s14][s14]
- **Catalogue:** 41 product families and 1,634 SKU count on `DesktopProdukIndexM4`, for example Besi Hollow Hitam 297, Plat Lubang 129, Pipa Hitam 124, Hollow Stainless 304 114. `RecCreateM4` embeds all 297 rows as `[w, h, thickness, kg, price]`, for example `[15,15,0.8,2.26,29500]`. [s14][s14] [s11][s11]
- **Top categories:** 3 (Besi, Plastik, Stainless Steel) on Kategori. [s8][s8] [s11][s11]
- **Price format:** `Rp 711.000`, with dots as thousands separators. Unit captions such as "per batang", `/meter`, `/ btg`. Superscript "Rp" at 9.5px on list rows. [s10][s10]
- **Spec strings:** "40 × 40 × 2 mm × 6 M". Filters are by size and thickness. Uses the true `×`. [s8][s8]
- **WhatsApp as conversion:** `wa.me/628112689889` ×32, phone `+62 811-2689-889`, plus live chat with office hours. No cart, checkout, account or order elements are in any canon outline. [s10][s10] [s8][s8]
- **Trust and fraud:** a fraud warning ribbon on 30 of 34 boards ("Transaksi sah HANYA ke rekening a/n PT. Sumber Makmur Surya Perkasa"), plus reviews, partner logos, and a with-or-without comparison. [s10][s10]
- **Content marketing:** blog with 5 categories (Berita Baja, Industri Baja, Produk Besi, Team, Trivia), long articles, calculators at `/tools/kalkulator-*`. [s8][s8] [s11][s11]
- **Long strings:** 174 visible strings of 50+ characters in canon, many long technical sentences mixing Indonesian with English (zinc coating, closed section). [s10][s10]

### Inferences
Patterns the system must support:
- `<Price>` with Rupiah dot grouping, superscript prefix, unit, tabular mono, and a "Mulai" (from) variant.
- `<SpecTable>` or `<SKURow>` for 300+ rows with lazy load, sort and multi-facet filter, in table and card views.
- A WhatsApp CTA as a first-class button variant, with a brand-accessible green and pre-filled message.
- Long Indonesian copy: compound product names on narrow columns, which is why `[data-nama]` max-width and hyphenation rules exist.
- A fraud notice is a persistent business requirement, not a promo.
- Indonesian mobile context means network and device constraints, so 297-row inline data and glass effects deserve a performance review. This is an inference.

### Gaps
- Actual traffic split, device mix, and conversion data are not in the canvas.

## 10. Accessibility and code quality

### Takeaway
The canvas is **better than typical prototype div soup**: real buttons and links, labelled controls, complete `alt` attributes. But it has focus-visibility, contrast, landmark, and touch-target failures, and all styling is inline, so **markup should be rebuilt rather than ported**. Treat the structure and values as the spec, not the code.

### Cited Findings

**Semantics, canon.** [s7][s7]
- `div` 757, `span` 951 versus about 1,050 semantic elements (`a` 302, `button` 249, `p` 250, `h1` to `h3` 87, `input` 33, `label` 28, `section` 19, `nav` 18, `header` 17, `main` 10).
- **0** `<footer>`, `<form>`, `<dialog>`, `<select>`, `<textarea>`, `<details>`. Dialogs are `role="dialog"` ×9.
- `onClick` on 203 `button` and 14 `a`; **0 on `div` or `span`.**
- **Missing `<main>`** on 6 of 16 canon boards: `RecCreateM4`, `SkuDetailM4`, `UlasanM4Salinan`, `DesktopProdukM4`, `DesktopSkuM4`, `DesktopUlasanM4`.
- **Missing `<h1>`:** `SkuDetailM4` (and fork `SalinanSkuPageM4`). `SalinanBlogM4` has an `<h1>` whose tag-stripped text is empty, which needs a manual check. Heading order starts at h3 on `SkuDetailM4` (`323222`). [s14][s14]
- **The price list is not a `<table>`:** only 2 tables in canon, both in articles. 297 price rows are links in grids.

**ARIA, canon.** [s7][s7]
- `aria-hidden` 656, `aria-label` 339, `aria-expanded` 34, `aria-current` 27, `aria-pressed` 23, `aria-live` 14, `aria-roledescription` 6, `aria-selected` 1.
- Roles: `group` 26, `img` 11, `dialog` 9, `region` 4, `log` 4, `radiogroup` 3, `status` 1, `tablist` 1, `tab` 1.
- **Absent:** `aria-modal`, `aria-controls`, `aria-describedby`, `aria-invalid`, `aria-required`, `aria-labelledby`.

**Touch targets,** from explicit size on `button` and `a`, canon. [s7][s7]

| | ≥44 | 24 to 43.9 | <24 | No explicit size |
|---|---|---|---|---|
| Mobile | 126 | 62 | 4 | 78 |
| Desktop | 160 | 60 | 2 | 59 |

Common sub-44 mobile sizes: 40 ×23, 32 ×11, 36 ×8, 30 ×7. The primary CTA `min-height:3rem` (30px) is below 44. Some small visuals sit inside larger hit wrappers, so this overstates failures somewhat.

**Inputs, canon.** 33 total: text 20, tel 4, email 4, radio 3, range 2. 28 `<label>` tags but only 16 with `for`; 5 `aria-label`. Screen-reader labels use an inline clip pattern, repeated rather than a class. [s7][s7]

**Contrast:** see question 2. Main failures: product names `rgba(255,0,0,.8)` 3.64:1, disabled and separator `#c9c9cb` 1.65:1.

**Text alignment:** `text-align: justify` ×48 with `hyphens` ×61 on narrow columns, which can harm readability. [s14][s14]

**Other code quality.** [s4][s4] [s7][s7] [s12][s12]
- 8,286 inline `style` attributes (all boards), with 0 to 1 `class` attributes per board.
- `html{font-size:62.5%}` overrides user default scaling behaviour in a known-problematic way only if px text is used; here rem makes it scale. Worth keeping or dropping as an explicit decision.
- 6 colour tokens have 0 uses, `--teks-chip` is undefined on `SkuDetailM4`, `--awas-bg` undefined on 11 boards.

### Inferences
- **Rework estimate: rebuild the markup entirely**, keep the values and interaction specs. Nothing about inline-style, half-gutter, per-file `:root` markup should port.
- Priority fixes: a global focus ring, hover states, AA for product names, 44px minimum for primary CTAs on mobile, `<main>` and `<h1>` on all templates, a real `<table>` for the price list.

### Gaps
- No automated audit (axe, screen reader) was run, because boards were not rendered.

## 11. What a real design system needs that the canvas does not show

### Takeaway
The canvas is rich in layouts and strong on mobile interactions, but it **documents almost none of the failure, loading, or validation states**, and it has no theming or responsive model.

### Cited Findings
Absences below are 0-match results from the scripts unless noted. [s6][s6] [s7][s7] [s11][s11] [s10][s10]

| Area | Evidence | Status |
|---|---|---|
| Dark mode | 0 `prefers-color-scheme`, 0 `color-scheme` | **Absent** |
| Tablet and intermediate layouts | 2 `min-width` queries in canon | **Absent** |
| Hover | 0 on controls | **Absent** |
| Focus ring | 3 rules, 28 `outline:none` | **Almost absent** |
| Form validation | 0 `aria-invalid`, `aria-describedby`, `<form>`. Submit is enabled or disabled only | **Absent** |
| Error states | No error UI found for network, chat, or 404 | **Absent** |
| Loading | 1 spinner (`lazy-spin`), no skeletons | **Minimal** |
| Empty states | 1 pattern (filter no-results), `Belum ada` not found | **Minimal** |
| Toast and notification | `aria-live` ×14, `role=status` ×1; copied label only | **Minimal** |
| Native selects, textareas, date | 0 | **Absent** |
| Checkbox, switch | 0 `checkbox`; radios 3 | **Absent** |
| Tooltip, popover | No named pattern | **Not found** |
| Accessible modal | No `aria-modal`, no `<dialog>`; focus trap not evident | **Partial** |
| Cart, checkout, account | Not in any outline | **Absent, possibly intentional** |
| Print, quote, or PDF price list | Not found | **Absent** |
| Governance | Tokens per file, no shared file, no `dc-import` | **Absent** |
| Data states | Long names, 0 prices, out of stock, "harga hubungi" not shown | **Not found** |

### Inferences
Minimum additions for the system: state matrix per component (default, hover, focus-visible, active, disabled, loading, error), form field pattern, toast, skeleton, modal and focus management, responsive grid (at least 360, 768, 1024, 1440), semantic token layer that allows dark mode later, and out-of-stock or "ask for price" states for a distributor catalogue.

### Gaps
- Whether smsperkasa.com production already solves these states is out of scope here, since this audit used canvas files only.
- Notes refer to `tokens/mobbin3.ts`, `tokens/space.ts`, `scripts/contract-rules.ts`, a repo design system, and the Figma file 'New Design System'. They claim one-to-one token parity (for example, `--radius-m3-action` = `radius/action`, `font-size-m3-*` = `teks/*`). None of these are in this folder, so **parity is unverified**, and the replacement plan should reconcile against them if they still exist.

[canvas]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/artifact-files/af1844c4-47c4-4b6f-b513-7a862c499d80/project/canvas.json
[comments]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/comments.txt
[s1]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s1.txt
[s2]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s2.txt
[s3]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s3.txt
[s4]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s4.txt
[s5]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s5.txt
[s6]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s6.txt
[s7]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s7.txt
[s8]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s8.txt
[s10]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s10.txt
[s11]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s11.txt
[s12]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s12.txt
[s13]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s13.txt
[s14]: file:///private/tmp/claude-501/-Users-andrewirawan-Documents-smsp-new-design-system-v2/13a84191-ca90-4820-ab6a-4175bc11dd5b/scratchpad/audit-out/s14.txt

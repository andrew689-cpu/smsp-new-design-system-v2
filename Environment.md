# Environment

## URLs

| What | Link |
|---|---|
| **The live canvas: work here** | https://claude.ai/artifact/Nd3ZoK9rHyAgWfak2xJnn3 |
| Parent canvas "SMS Perkasa v5": read only, holds the older "Template Design System" page | https://claude.ai/artifact/Cx6beToCZPtSCVnET3bv33 |
| Production site | https://www.smsperkasa.com/ |

Canvas pages are `Prototype Mobbin 4` (id `salinan4`, the 37 screens) and `Components` (id `components`). The canvas is private to the owner.

## Credentials

**None stored here, and none needed today.** Canvas access comes from the owner's claude.ai login in Claude Code. If a real credential is added later, record only its name and where it lives (for example, "`FOO_TOKEN`, in the owner's password manager"), never its value.

## Folders

```
Agents.md, InstructionRules.md, Skills.md, Tools.md, Environment.md   this harness
CLAUDE.md                     loads Agents.md automatically in Claude Code
design-source/
  workspace/                  THE WORKING COPY. Has its own git history
    project/                  every board: screens, components, tokens.css, canvas.json
    tokens.base.css           source for tokens.css
    _token-requests/          source for tokens.css
    _manifests/               which boards exist; ATOMS_PROPS.md maps old copies to atoms
    publish-files.json        written by final_layout.py
  baseline/                   THE APPROVED VERSION. The gate compares with this. Only approve_baseline.sh changes it
  mobbin4-originals-2026-11-03/  the first 34 boards with all design notes. Read only; the reason behind odd values
  fixtures/                   repaired original of DesktopProdukM4Salinan
  images/                     canvas images in use, named by id
  store-ids.txt               image ids on the canvas; update it after uploading an image
  runtime/                    copy of the canvas runtime and format guide
  qa/                         every check; see Tools.md. qa/runs/ is disposable
  canvas-v13/, v16/, v19/, v21/, v23/, v24/, v25/, v27/, v28/, v29/  snapshots of published versions
  postponed/                  hover, focus and pressed work
reports/, research_notes/     the original research
```

The project root isn't a git repository. History is in `design-source/workspace`; its `states-wip` branch holds the postponed states.

`design-source/runtime/` is a copy: if the canvas type updates, refresh it from `artifact-type/dc-runtime.js` and `artifact-type/reference/format.md` on the canvas.

## How the system is built

- **Format:** `.dc.html` boards. React 18 at runtime with `this.props`, `this.state` and lifecycle. Flat folder, imports by name.
- **Tokens:** `tokens.css`, linked from each board's helmet. Names are Indonesian (`--ink`, `--brand`, `--teks-body`). `html` is `62.5%`, so `1rem` = 10px.
- **Breakpoint:** `--sisi` and `--seksi` switch at 1024px. Components take `tata="ponsel"` or `"desktop"`.
- **Board sizes:** mobile 360×800, desktop 1440×900. Screens starting with `Desktop` are desktop.
- **Canvas limits:** a frame is 40 to 8000 px per side, 512 files, 16 MB per publish call.
- **Images:** `/_blob/<id>`. Ids belong to one canvas, so an image copied in gets a new id.
- **Component counts:** 43 screens; the Components page has 150 boards (components, sheets, foundations).

### Canonical screens

File names mislead: "Salinan" doesn't always mean copy, and `canvas.json` titles are the identity.

| Page | Mobile | Desktop |
|---|---|---|
| Home | `BerandaM4` | `DesktopBerandaM4` |
| Price list | `RecCreateM4` | `DesktopProdukM4` |
| SKU detail | `SkuDetailM4` | `DesktopSkuM4` |
| Reviews | `UlasanM4Salinan` | `DesktopUlasanM4` |
| All products | `ProdukIndexM4` | `DesktopProdukIndexM4` |
| Category | `KategoriM4` | `DesktopKategoriM4` |
| Blog | `SalinanBlogM4` | `DesktopBlogM4` |
| Article | `SalinanArtikel2M4` | `DesktopArtikelM4` |
| Home with product rail (6 versions) | `SalinanBeranda4M4` to `SalinanBeranda9M4` | none |
| Article that opens the picked blog item | `DetailArtikel3M4` | none |
| News-style blog | `SalinanBlog4M4` | none |
| Learning (3 versions) | `LearningM4`, `SalinanLearning1M4`, `SalinanLearning2M4` | none |

The other 16 are variants and old copies. They follow the same rules.

## Current state

As of 2026-11-05, live canvas version 29, baseline equals version 29. The Publish skill updates this section.

- All 43 screens use only components, and the strict rule is at 0 violations.
- Version 29 brought the rest of the parent's Beranda boards: new `SalinanBeranda5M4`, `SalinanBeranda6M4` and `SalinanBeranda7M4`, and updated `SalinanBerandaM4`, `SalinanBeranda2M4` and `SalinanBeranda3M4`. All 10 mobile Beranda boards match the parent. `BerandaM4` and `DesktopBerandaM4` needed no change.
- Version 28 brought a second round from the parent canvas: new `SalinanBeranda9M4`, and updated `SalinanBeranda8M4`, `SalinanLearning1M4` and `RecCreateM4`. `DataMateri` now holds 11 more courses, the 41 product cards and the 4 material cards for Salinan Learning 1 only (`koleksi="foto-lengkap"`); `LearningM4` and `SalinanLearning2M4` still get their own lists.
- Versions 26 and 27 brought the owner's revisions from the parent canvas: new `SalinanBeranda4M4` and `SalinanBeranda8M4` (new component `SketchRail`; `Rail` owns the product list and `koleksi="sketsa"`), and updated `RecCreateM4` and `SalinanLearning1M4`. Checked against the parent's boards. The id map for images copied in is `design-source/blob-id-map-2026-11-05.txt`. The rest of the Produk Page look (glass view switch, white Live Chat and WhatsApp buttons, no row chevrons) stays on `RecCreateM4` only: `DesktopProdukM4` and the old copies keep theirs.
- `SalinanBlog4M4`, `DetailArtikel3M4` and the three Learning screens were rebuilt from the parent canvas on 2026-11-04 and match it (31 states, worst 0.557%, nearly all under 0.14%). The other 32 screens match the first originals; worst difference 0.029%, apart from the known differences below.
- Sections the owner switched off on those five boards were not rebuilt: partner logos and reviews on Salinan Learning 1, the sales ribbon and value points on Learning, filter and sort on Blog 4.
- Besi Hollow Hitam prices have one source, `DataHarga`.
- The article list (title, link, category, date, photo, summary) has one source, `DataDaftarArtikel`, read by `BlogPage` and `LearningPage`. Full article bodies stay in `DataArtikel`, which holds 43: the 12 Bacaan articles were copied from smsperkasa.com on 2026-11-05 with their captions, and Besi Siku has a `video` block.
- `LearningM4` has a "Bacaan" section with the 12 Produk Besi and Trivia articles (added 2026-11-05 at the owner's request). Each row opens the article inside `DetailArtikel3M4`. Learning's search also finds these articles, by title, category and summary, listed below any matching courses, and its search box says "Cari materi atau artikel". Salinan Learning 1 and 2 have neither the section nor article search, and keep "Cari materi".

### Known differences from the originals (accepted)

| Difference | Where |
|---|---|
| Fake on-screen keyboard removed. "Recent searches" no longer updates | Search on `RecCreateM4`, `RecCreateM4Salinan1`, `SalinanProdukPageM4`, `SkuDetailM4`, `SalinanSkuPageM4` |
| Fixed spacing replaced the height-measuring script: 1 to 7 px drift in a few states | `RecCreateM4` (filter applied, `panelFilter=terbuka`), `ProdukIndexM4` (footer open) |
| Rail shifts 21 px in one test against the originals, cause not found | `SkuDetailM4` `m_rail` |
| Working board built, because the original never ran | `DesktopProdukM4Salinan` |

### Not yet verified

The review runs locally with the real runtime. Live editor behaviour is confirmed by the owner only for a hand color edit on a component.

### Still more than one place

- The phone number is in `SiteHeader`, `HelpCentre` and the `Footer` address text.
- An article title is in `DataDaftarArtikel` (lists and search) and `DataArtikel` (the opened article).
- Home "Paling banyak dicari" prices aren't linked to `DataHarga`.
- The 41 product names are in `Rail` (price index and sketch rail) and `DataMateri` (Learning product cards).

### Spacing measured live (only these)

`BlogPage` versi `berita`, `LearningPage` and `ArticleBody` with `celahOtomatis` measure section heights in the browser, using the canvas spacing formula. A fixed value could not match every state. Everywhere else spacing stays fixed.

### Waiting on the owner

| Decision | Current default |
|---|---|
| Which size is the SKU page about? Title 40 × 40 × 2 mm (Rp188.600), description 15 × 15 mm, 1,5 mm (Rp50.300) | Left as in the original |
| Link home prices to `DataHarga`? 4x4 shows Rp83.000 vs Rp81.800 in the list; 4x6 shows Rp106.700 vs Rp132.100 | Not linked; recommended yes |
| Hover, focus and pressed states | Postponed by the owner |
| Course text is marked in the source as needing technical review before going live | Carried over unchanged |
| Consent line "Dengan menekan tombol diatas...": on both layouts? | Hidden on mobile, shown on desktop |
| Privacy link color from the 2 Nov note: mobile only? | Applied to mobile |
| "Hapus semua filter" clears the applied filter too | Yes; a known change from the original |
| Desktop help rows can't be clicked with a mouse (also in the original) | Left as is |

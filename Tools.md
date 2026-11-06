# Tools

Run commands from the project root. Each script's header explains its arguments.

## Requirements

| Tool | Used for | Check |
|---|---|---|
| Node 24 | Rendering and format checks | `node -v` |
| Python 3 with Pillow | Comparing images, gates | `python3 -c "import PIL"` |
| Playwright with Chromium | Rendering boards in a real browser | `ls "$(npm root -g)/@playwright"` shows `cli`; browsers live in `~/Library/Caches/ms-playwright` |
| Artifact tool (Claude Code) | Reading and publishing the canvas | `action: "list", scope: "files"` on the canvas URL |

The scripts find Playwright through the global `@playwright/cli` package. If it's missing, run `npm i -g @playwright/cli` and install its browsers.

## Review commands

| Command | What it proves | Pass looks like |
|---|---|---|
| `bash design-source/qa/gate.sh [Screen ...]` | The whole gate: everything in the next four rows, on all 37 screens by default. About 3 minutes | `GATE PASS`, or a list of differences from the baseline |
| `python3 design-source/qa/lint_strict.py [Name]` | One component, configured by props: no local copies, every prop declared, no repeated data, nothing unused | `TOTAL violations: 0` |
| `python3 design-source/qa/lint_components.py design-source/workspace/project [File.dc.html]` | Files are valid: tags closed, tokens exist, JS parses, images exist | `errors=0` |
| `python3 design-source/qa/lint_board.py <Screen ...>` | A screen holds only imports and layout | `PASS` |
| `python3 design-source/qa/compare.py <Screen> --no-orig-cache` | Same as the approved baseline: pixels, height, words, links, images, type styles | `PASS` |
| `python3 design-source/qa/run_steps.py <Screen>` | The interaction tests that apply to that screen | No `FAIL`. `CANT-RUN` is fine |
| `python3 design-source/qa/edit_test.py` | An edit reaches every page: plants edits on a temporary copy and counts what changes. Its "still on" lines are informational | `REACH PASS` |
| `python3 design-source/qa/price_test.py` | A price changed only in `DataHarga` shows everywhere | `FAILURES: 0` |
| `python3 design-source/qa/audit.py <dir> <dir> <canvas.json>` | Full reach audit: who owns each element, what's repeated | Read the report |

## Comparing screens

`compare.py` needs real images:

```bash
export REAL_IMAGES="$PWD/design-source/images" SETTLE_MS=3000
python3 design-source/qa/compare.py RecCreateM4 --no-orig-cache
```

- **Interactions:** add `--steps design-source/qa/steps/harga/m_filter.json --label filter`. Steps are JSON: `[{"click":"text=Filter"},{"wait":600},{"fill":["input","abc"]},{"scrollTo":1200},{"key":"Escape"}]`.
- **Limits:** at most 0.6% of pixels may differ, with page height within 2 px. A file compared with itself gives 0.000%, so any difference is real. The text check catches a one-word change that the pixel limit would miss.
- **Output:** `design-source/qa/runs/<Screen>-<label>/` has `orig.png`, `new.png`, `diff.png`, `side.png` and `report.json`. This folder is disposable and grows fast, so delete it when done.
- **What it compares with:** `design-source/baseline/` by default. For the first originals, add `--orig-dir design-source/mobbin4-originals-2026-11-03`; for `DesktopProdukM4Salinan` use `--orig-dir design-source/fixtures/DesktopProdukM4Salinan-repaired`, because its real original never ran.
- **Always use `--no-orig-cache`** unless you've just captured the same reference, because a cached capture can be stale.

## Rendering boards

| Command | Use |
|---|---|
| `node design-source/qa/capture.cjs <dir> <Board> <w> <h> <outPrefix> [steps.json]` | Screenshot plus a fingerprint of one board. Needs `DC_RUNTIME="$PWD/design-source/runtime/dc-runtime.js"` |
| `node design-source/qa/measure.cjs <dir> <list.json> <out.json>` | Real heights and runtime errors for many boards |

The render fixes the clock, seeds randomness and stops autoplay, so runs match. It uses the real canvas runtime, but it isn't the live editor.

## Build commands

| Command | Use |
|---|---|
| `python3 design-source/qa/merge_tokens.py design-source/workspace` | Rebuilds `tokens.css` from `tokens.base.css` and `_token-requests/`. `gate.sh` runs it too |
| `python3 design-source/qa/final_layout.py <live canvas.json>` | Rewrites sheet parts by real height, fits frames, writes `canvas.json` and `publish-files.json`. About 5 minutes |
| `bash design-source/qa/approve_baseline.sh` | Makes the workspace the new approved baseline. Only after a reviewed publish |
| `python3 design-source/qa/sync_paths.py` | Prints the paths to read for Sync |

## Canvas calls (Artifact tool)

| Task | Call |
|---|---|
| List files | `action: "list", scope: "files", url` |
| Read files | `action: "read", url, paths: [...], out_dir: <scratch>` (small files also print inline, so request only what you need) |
| Read one uploaded image | `action: "read", url, path: "<32-hex id>"`. `paths` doesn't accept image ids |
| Copy images between canvases | `action: "publish", url, asset: true, from_url, asset_ids` (10 per call). Copies get new ids |
| Publish | `action: "publish", url, root, file_path, files: {"project/X.dc.html": "project/X.dc.html"}` |

## Shell traps on this Mac

- zsh doesn't split a variable into words: `$G status` fails when `G` holds a whole command. Use a function, or `bash` for scripts.
- zsh stops on an unmatched wildcard, and macOS `xargs -I` fails on long commands. Use `xargs -n1` with a script.

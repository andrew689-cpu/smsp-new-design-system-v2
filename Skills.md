# Skills

The procedures for design work. Each one ends on a check you can see pass. Commands are in [Tools.md](Tools.md), paths in [Environment.md](Environment.md).

| Skill | Use when |
|---|---|
| [Sync](#sync) | Starting any task |
| [Review](#review) | Before anything reaches the owner, always |
| [Change a component](#change-a-component) | A component needs a new look, prop or variant |
| [Slice a new component](#slice-a-new-component) | UI exists that no component covers |
| [Change a token](#change-a-token) | A color, size or spacing value changes everywhere |
| [Change shared content](#change-shared-content) | Footer links, nav, labels, or a price change |
| [Change a screen](#change-a-screen) | One page needs something different |
| [Publish](#publish) | The review passed and the canvas should change |
| [Run parallel agents](#run-parallel-agents) | Work spans many components |

## Sync

The owner hand-edits the live canvas, so the workspace can be behind.

1. List the live files, in case boards were added. Get the paths with `python3 design-source/qa/sync_paths.py` and read them with `out_dir` set to a new temporary folder outside the project.
2. Run `diff -rq <temp>/project design-source/workspace/project`.
3. The workspace is committed at each publish, so a difference normally means the owner edited live. Confirm with `git -C design-source/workspace status`. Copy the live file over, commit, and tell the owner what you picked up. `canvas.json` differing only in layout keys such as `noteOrder` is normal: use the live version as your base.

Done when `diff -rq` shows no difference except `canvas.json` layout keys.

## Review

Be relentless: your job here is to catch your own work failing. Run all of it on the final code, because a pass from before your last edit proves nothing.

1. **Gate.** Run `bash design-source/qa/gate.sh`. Strict rule, component format and components-only must always pass. The comparison shows every difference from the approved baseline: see *Requested changes* below.
2. **Reach.** Run `python3 design-source/qa/edit_test.py`, which must print `REACH PASS`, and `python3 design-source/qa/price_test.py` if prices were touched, which must print `FAILURES: 0`.
3. **Behaviour.** Run `python3 design-source/qa/run_steps.py <Screen>` for each screen whose behaviour you could have affected. `CANT-RUN` means that step's control isn't on the screen, which is fine. A `FAIL` is a real difference. It's slow (about 16 minutes for 19 steps), so choose screens deliberately and list which you ran. A control with no step gets a new one in `qa/steps/`.
4. **Look.** For each changed screen, crop `qa/runs/<Screen>-gate/orig.png` and `new.png` around the change and read both. `side.png` is too wide to read whole. The gate's type check skips text that's new, and the pixel limit can hide a small change, so your eyes are the only check on a new label's look.
5. **Test the test.** For each pass you plan to report, ask what would have made it fail. If nothing could, the check is empty. Example from this project: search showed "39.000", but so did the price list on the same page, so the real check had to read the search result line.
6. **Review the harness too.** If you changed a skill, rule or tool, follow it literally once on a small case and confirm every path and command works.

Done when every step passed, or every difference is either requested by the owner or reported to the owner with its number and cause. An unrequested difference blocks publishing until the owner accepts it.

### Requested changes

The gate compares with the approved baseline, so a change the owner asked for makes it fail on those screens. That's correct: read the failures as a list of what changed.

- Each listed difference must be something requested, on a screen you expected. For example, `missing: Kontak, extra: Hubungi, Kami` on the 10 desktop screens. Anything else is a bug.
- Report the exact screens that changed.
- After publishing, `approve_baseline.sh` moves the baseline forward and the gate goes back to `GATE PASS`.

## Change a component

1. Find it in `design-source/workspace/project/` and read its `data-props` and `renderVals`.
2. Make the change additive: a new prop or variant whose default keeps today's output. To change every page on purpose, change the default.
3. Declare every prop in `data-props` with an editor, a default and a `section`, so it works in the canvas Tweaks panel.

Done when `lint_strict.py <Name>` prints `TOTAL violations: 0` and the Review passes.

## Slice a new component

1. Find the real markup in the screens' originals (`design-source/mobbin4-originals-2026-11-03/`). Comments there explain why values are odd, so read them.
2. Check the folder first: extend an existing component with a prop if it's close.
3. Build from small pieces: import `Price`, `Heading`, `Icon`, `Button`. Copy exact values through tokens.
4. Follow the format in `design-source/runtime/format.md` and the craft notes below.
5. Add it to a manifest in `workspace/_manifests/` so it gets a board on the Components page.

Done when it's used by a screen, and `lint_strict.py` reports nothing, including `component_unused_by_any_screen`.

### Craft notes for `.dc.html`

These fail silently, so check them each time.

- Files sit flat in the folder. `<dc-import name="X">` takes a fixed name, never a `{{ hole }}`.
- `style="{{ a }}"` with a single hole is fine, but a style that starts and ends with a hole is read as one lookup and dropped. End it with `;`.
- An import's wrapper is `display: contents`, so `style` on `dc-import` keeps only position and size. Put margins on a wrapping `<span>`.
- `componentDidUpdate` receives only `prevProps`. `renderVals` must run without a DOM; touch `document` and `window` only in lifecycle methods.
- `{{ }}` is a dotted lookup only. Compute everything in `renderVals`.
- Inside a `<table>`, the HTML parser misplaces `<sc-for>`. Use a grid of `div`s.
- `dc-props="{{ obj }}"` spreads an object. Other attributes can sit beside it.
- A component can hand data to its importer through a callback in `componentDidMount`, which is how `DataHarga` works.
- Shared rules a component can't hold inline (`@keyframes`, `::-webkit-scrollbar`, `[data-*]`) go in a `_token-requests/*.css` file, never in `<helmet>`.

## Change a token

1. Find where it's defined: `workspace/tokens.base.css` or a file in `workspace/_token-requests/`.
2. Edit it there and run `qa/merge_tokens.py`. `tokens.css` is generated, and the merge overwrites direct edits.

Done when `merge_tokens.py` reports no clashes and `Colors` or `FontSizes` shows the new value.

## Change shared content

- **Footer, nav, ribbon link, labels:** edit the default prop in the component (`Footer`, `CategoryNav`, `FraudRibbon`).
- **A price:** edit the row in `DataHarga` (`[A, B, tebal, berat kg, harga]`).
- **Find every use first:** run `grep -rl "<old text>" design-source/workspace/project`. One word can be different things: "Kontak" is a link on desktop, and a heading on mobile. "Lihat Selengkapnya" is a separate default in several components. If the request doesn't say which, ask.
- **Sheets are documentation:** `Sheet*` boards hold their own sample data, and the strict rule skips them. Update a sheet that shows the old text.

Done when each remaining match of the old text is a use you've decided to leave and named in your report, and for a price, `price_test.py` passes.

## Change a screen

1. Set a prop on the existing component, and add the prop if needed.
2. When two screens need the same thing, it belongs in a component's default. Keep screens holding only what differs.

Done when `lint_board.py <Screen>` prints `PASS` and the comparison shows only the requested difference.

## Publish

1. Run Sync again right before publishing, so you work from the newest version.
2. If boards were added, removed or resized, run `qa/final_layout.py` with the live `canvas.json` as its base. It repacks sheets, fits frames and writes `canvas.json`.
3. Publish only the changed files, with `url`, `root` = `design-source/workspace` and `file_path` on one of them. Set a removed board's path to `null`.
4. If the publish is refused, someone saved meanwhile: read the file it names, merge, try again. After a third refusal, tell the owner and stop.
5. If the result warns the previous version was saved from the page, check the files it replaced against what you synced, and tell the owner if anything was lost.
6. Read one changed file back from the live canvas and confirm it matches.
7. Run `bash design-source/qa/approve_baseline.sh`, commit in `design-source/workspace`, and copy the project to `design-source/canvas-v<N>/`, where `N` is the "Version N" in the publish result.
8. Update *Current state* in Environment.md.

Done when the read-back matches, `gate.sh` prints `GATE PASS`, and the owner has the link.

## Run parallel agents

Use this when work spans many components and the owner has asked for that scale.

- **Give each agent exclusive file ownership.** Concurrent edits to shared files overwrote each other in an earlier round. An agent that needs someone else's file reports what it needs.
- **Order the work:** small pieces first with a written prop contract, then bigger components, then screens.
- **Re-run the whole Review yourself afterwards.** Agents' reports are claims until your own run confirms them.

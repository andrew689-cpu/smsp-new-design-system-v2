# Component architecture, tooling, docs and quality automation for a code-first design system (state as of November 2026)

All sources accessed 2026-11-03. npm versions and weekly downloads come from the npm registry and `api.npmjs.org` (`last-week`) on that date. GitHub figures come from the GitHub API on that date. "Own measurement" means I ran it in this session; the method is given so it can be reproduced. Evidence labels: **[primary]** official docs, repo or registry; **[vendor]** a party with a commercial stake; **[independent]** neither; **[weak]** blogs or aggregators of unclear provenance.

## Objective: what concrete stack should the team adopt?

### Takeaway
Default recommendation for React/Next.js: **native HTML first, Base UI 1.9 for what native cannot do, Tailwind v4 + `cva`, a pnpm + Turborepo monorepo with a workspace `packages/ui`, Storybook 10 as workbench and test harness, a Fumadocs site as the designer-facing reference, and Vitest browser mode + axe + a hosted visual-review tool as gates.** Publish a versioned package only when a second consumer repo appears, and use a private shadcn registry for copy-owned blocks rather than for core components.

### Cited Findings
Recommended stack summary (rationale and evidence are in the sections below; versions verified on npm):

| Layer | Pick | Version | Main alternative |
|---|---|---|---|
| Primitives | Native HTML, then [`@base-ui/react`](https://www.npmjs.com/package/@base-ui/react) | 1.9.0 | `radix-ui` 1.8.1 if JS weight dominates; `react-aria-components` 1.22.1 for hard date or i18n widgets |
| Scaffolding | [`shadcn`](https://www.npmjs.com/package/shadcn) CLI as a one-time generator | 4.23.0 | Hand-rolled |
| Styling | [`tailwindcss`](https://www.npmjs.com/package/tailwindcss) + [`class-variance-authority`](https://www.npmjs.com/package/class-variance-authority) | 4.3.4 + 0.7.1 | CSS Modules if framework portability dominates |
| Repo | [`pnpm`](https://www.npmjs.com/package/pnpm) + [`turbo`](https://www.npmjs.com/package/turbo) | 12.16.1 + 2.11.10 | pnpm alone at first |
| Build (when published) | [`tsdown`](https://www.npmjs.com/package/tsdown) unbundle | 0.23.4 | `tsc` (as Medusa does) |
| Release (when published) | [`@changesets/cli`](https://www.npmjs.com/package/@changesets/cli) | 3.0.3 | n/a |
| Workbench | [`storybook`](https://www.npmjs.com/package/storybook) | 10.6.5 (11 stable targeted 1 Dec 2026) | n/a |
| Docs for designers | [`fumadocs-ui`](https://www.npmjs.com/package/fumadocs-ui) | 16.17.10 | Starlight 0.42.8 if the app is Astro or not React |
| Tests | [`vitest`](https://www.npmjs.com/package/vitest) browser mode + [`@storybook/addon-vitest`](https://www.npmjs.com/package/@storybook/addon-vitest) | 5.1.0 + 10.6.5 | Playwright 1.64.1 for page-level tests |
| Visual review | Chromatic Free, then Argos or Chromatic paid | see quality section | Self-hosted `toMatchScreenshot` in Docker |
| A11y | [`axe-core`](https://www.npmjs.com/package/axe-core) via `@storybook/addon-a11y`, with WCAG 2.2 tag enabled | 4.14.0 | n/a |
| Budgets | [`size-limit`](https://www.npmjs.com/package/size-limit) + [`@lhci/cli`](https://www.npmjs.com/package/@lhci/cli) | 14.3.0 + 0.16.0 | n/a |

How the recommendation changes by framework:

| App framework | Primitives | Registry/port | Docs | Storybook notes |
|---|---|---|---|---|
| Next.js or React | `@base-ui/react` | `shadcn` has `next-app` and `next-monorepo` [templates](https://github.com/shadcn-ui/ui/tree/main/templates) | Fumadocs | `@storybook/nextjs-vite`, needs [Next 14.1+](https://storybook.js.org/docs/writing-tests/integrations/vitest-addon); MCP docs tools [available](https://storybook.js.org/docs/ai/mcp/overview) |
| Astro (content-heavy) | Native HTML + Tailwind; React islands with Base UI only where needed | `astro-app`, `astro-monorepo` [templates](https://github.com/shadcn-ui/ui/tree/main/templates) | Starlight ([supports React, Vue, Svelte components in MDX](https://starlight.astro.build/components/using-components/)) | Component stories cover the React islands; `.astro` component support not verified |
| Vue/Nuxt | [`reka-ui`](https://www.npmjs.com/package/reka-ui) 2.11.0 (2.85M/wk); [`@ark-ui/vue`](https://www.npmjs.com/package/@ark-ui/vue) 5.40.0 is much smaller (36.5k/wk) | [`shadcn-vue`](https://www.npmjs.com/package/shadcn-vue) 2.9.0 | Starlight | `vue3-vite` works with the Vitest addon; manifest [also needs `experimentalDocgenServer`](https://storybook.js.org/docs/ai/mcp/overview) |
| Svelte/SvelteKit | [`bits-ui`](https://www.npmjs.com/package/bits-ui) 2.20.3 (1.6M/wk, [active](https://github.com/huntabyte/bits-ui)) | [`shadcn-svelte`](https://www.npmjs.com/package/shadcn-svelte) 1.7.2 | Starlight | `sveltekit` works with the Vitest addon; no manifest in 10.x docs; [Storybook 11 alpha adds Svelte docgen](https://github.com/storybookjs/storybook/releases) |
| Framework-agnostic web components | [`lit`](https://www.npmjs.com/package/lit) 3.3.3, or adopt [`@awesome.me/webawesome`](https://www.npmjs.com/package/@awesome.me/webawesome) 3.14.0 | Registry [is framework-agnostic in principle](https://ui.shadcn.com/docs/registry) | Starlight | Agentic support for Web Components [is a Storybook 11 target](https://github.com/storybookjs/storybook/discussions/36230) |

### Inferences
- The framework is the largest unresolved variable. Three layers survive a framework change: CSS and token conventions, docs content, and test scenarios. Component code does not. Keep business-free styling in plain Tailwind classes and data-attribute variants so a port is mainly re-binding behaviour.
- If the team cannot decide soon, start on the CSS layer and the native-HTML components (SKU radios, spec table, `<details>`, `<dialog>`). They are framework-independent and also cover the highest-traffic e-commerce pages.
- Avoid web components as the storefront default. Reasons: the ARIA-across-shadow-root limit noted below (`referencetarget` is limited availability), smaller tooling coverage, and Polaris's main advantage (CDN control of a platform you own) does not apply.

### Gaps
- The app framework is unknown, so the Next.js default is conditional.
- I found no first-person, long-term account from a small team on this exact combination. The stack is assembled from component-level evidence.

## Headless primitives: who is maintained, how is Radix, which is most accessible, and what can native do now?

### Takeaway
Base UI is the safest default on momentum: stable since December 2025, with monthly minors and the shadcn default since July 2026. Radix is **alive again but was dormant for 10 months and is concentrated on one maintainer**. React Aria has the deepest published a11y claims, but it is the heaviest and ships no Indonesian strings. No independent comparative a11y audit was found, so "best a11y" rests on vendor claims.

### Cited Findings
**Health table** (commits are for the last 90 days; my query capped at 100; "open" is GitHub's count, which includes PRs):

| Library | Latest | Weekly downloads | Commits | Open | Status |
|---|---|---|---|---|---|
| [`@base-ui/react`](https://github.com/mui/base-ui) | 1.9.0, 9 Oct 2026 | 26.5M | 100+ | 446 | Active |
| [`radix-ui`](https://github.com/radix-ui/primitives) | 1.8.1, 12 Oct 2026 | 25.4M (`@radix-ui/react-dialog` 88.3M) | 69 | 265 | Revived in June 2026 |
| [`react-aria-components`](https://github.com/adobe/react-spectrum) | 1.22.1, 9 Oct 2026 | 8.0M | 100+ | 676 (whole monorepo) | Active |
| [`@ark-ui/react`](https://github.com/chakra-ui/ark) | 5.40.0, 29 Oct 2026 | 1.38M | 100+ | 5 | Active |
| [`@zag-js/core`](https://github.com/chakra-ui/zag) | 1.47.0, 26 Oct 2026 | 2.2M | 100+ | 7 | Active |
| [`@headlessui/react`](https://github.com/tailwindlabs/headlessui) | 2.2.10, 7 Apr 2026 | 9.76M | **0** | 122 | Dormant-looking (last push 13 Apr 2026) |
| [`bits-ui`](https://github.com/huntabyte/bits-ui) | 2.20.3, 1 Nov 2026 | 1.6M | 100+ | 32 | Active |
| [`melt`](https://github.com/melt-ui/next-gen) | 0.44.0, 4 Jan 2026 | 14.5k | **0** | 33 | Low activity (last push 4 Mar 2026) |

**Base UI**
- 1.0.0 shipped 11 Dec 2025. Minors followed about monthly, through v1.9.0 on 9 Oct 2026: Drawer, OTPField, `createItems` for Combobox, mount performance work — [Base UI releases](https://base-ui.com/react/overview/releases) [primary].
- Use `@base-ui/react`. The old [`@base-ui-components/react`](https://www.npmjs.com/package/@base-ui-components/react) is stuck at 1.0.0-rc.0 yet still draws 745k/wk.
- Semver caution: v1.5.0 renamed `sanitizeValue` to `normalizeValue`, and post-1.0 entries do not list breaking changes. The page describes no formal policy — [Base UI releases](https://base-ui.com/react/overview/releases).
- A11y: ships ARIA roles, APG keyboard behaviour, focus management, and form association, and says it tests across browsers, devices and screen readers. **You** own visible focus, contrast and accessible names — [Base UI accessibility](https://base-ui.com/react/overview/accessibility) [primary, self-reported].

**Radix in 2026**
- npm history: 1.4.3 on 13 Aug 2025, then nothing until 1.5.0 on 6 Jun 2026 (about 10 months), then 12 releases from 1.5.0 through 1.8.1 on 12 Oct 2026 — [npm registry](https://registry.npmjs.org/radix-ui).
- Recent fixes include dialog ARIA references, Select form bubbling and React 19 render loops — [Radix releases](https://www.radix-ui.com/primitives/docs/overview/releases), [changelog](https://github.com/radix-ui/primitives/blob/main/packages/react/radix-ui/CHANGELOG.md).
- Concentration: Chance Strickland authored 76 of the 100 most recent commits ([GitHub API](https://github.com/radix-ui/primitives/commits/main)); his [profile](https://github.com/chaance) lists WorkOS.
- Since 1 May 2026: 148 merged PRs and 577 issues closed versus 71 opened, per GitHub search. The closed number likely includes bulk triage, so it should not be read as 577 fixes.
- The Radix releases page has no roadmap or maintenance statement. A PkgPulse claim of "ownership concerns" gives no detail, so treat it as unverified — [PkgPulse](https://www.pkgpulse.com/guides/shadcn-ui-vs-base-ui-vs-radix-components-2026) [weak].
- shadcn says Radix is not deprecated, every update still ships for it, and the team runs it in production — [shadcn: Base UI as default](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) [primary].

**React Aria**
- States it follows APG, tests with multiple screen readers and devices (not named), handles touch specifics such as hidden dismiss buttons and non-sticky hover, offers 30+ languages, and supports 13 calendar systems — [React Aria](https://react-aria.adobe.com/) [primary, self-reported].
- The repo has 34 locale files and **no `id-ID`** — own check of the [react-spectrum tree](https://github.com/adobe/react-spectrum) (34 distinct `intl/*.json` names).
- Is now a first-class shadcn base alongside Base UI and Radix — [shadcn React Aria entry](https://ui.shadcn.com/docs/changelog/2026-07-react-aria).

**Ark/Zag**
- The multi-framework state-machine approach is active, with very low open issue counts and releases for React, Vue and Svelte ([Ark](https://github.com/chakra-ui/ark), [Zag](https://github.com/chakra-ui/zag)). Adoption is an order of magnitude below Base UI and Radix.

**Independent a11y evidence is thin**
- No rigorous multi-AT comparison turned up. One axe-based survey has unclear provenance and says its screen reader checks were only smoke tests — [disabilityworld.org](https://www.disabilityworld.org/articles/accessible-component-libraries-survey/) [weak].
- Untitled UI, a vendor, favours React Aria for a11y depth and Base UI for API — [Untitled UI](https://www.untitledui.com/blog/base-ui-vs-react-aria) [vendor].

**Own measurement: JS cost.** esbuild 0.28.2, minified, ESM, `react`/`react-dom` external, production define, library code only, no CSS. React 19.3.1 + react-dom client alone was 68.9 KB gz. Sizes in KB:

| Export | Radix 1.8.1 | Base UI 1.9.0 | RAC 1.22.1 | Ark 5.40.0 | Headless UI 2.2.10 |
|---|---|---|---|---|---|
| Dialog (gz / br) | 14.2 / 12.8 | 23.9 / 21.5 | 28.6 / 25.5 | 21.2 / 19.1 | 16.8 / 15.0 |
| Select (gz / br) | 32.3 / 28.8 | 45.4 / 40.4 | 58.4 / 50.2 | 34.2 / 30.6 | not measured alone |
| Accordion (gz / br) | 9.3 / 8.3 | 9.6 / 8.6 | not measured | not measured | not measured |
| 7-part kit* (gz / br) | 43.3 / 37.8 | 74.3 / 64.0 | 67.5 / 57.6 | 58.1 / 48.5 | 48.4 / 42.4 |

*Dialog, Popover, Select, Tabs, Accordion, Tooltip, RadioGroup. Headless UI has no Tooltip, so its kit is six parts and is listed for reference only. Parts are not perfectly equivalent across libraries.

**Native platform status** — [web-features data](https://cdn.jsdelivr.net/npm/web-features@latest/data.json) v3.45.0, cross-checked with [webstatus.dev](https://webstatus.dev):

| Feature | Baseline | Support (first version) | Use now? |
|---|---|---|---|
| `<dialog>` | Widely (since Sep 2024) | Chrome 37, FF 98, Safari 15.4 | Yes |
| `<details name>` | Newly (Sep 2024) | Chrome 120, FF 130, Safari 17.2 | Yes |
| Popover API | Newly (Jan 2025) | Chrome 116, FF 125, Safari 17; iOS 18.3 | Yes, for simple cases |
| `:has()` | Widely (Jun 2026) | [webstatus](https://webstatus.dev) | Yes |
| Invoker commands | Newly (Dec 2025) | Chrome 135, FF 144, Safari 26.2 | With fallback |
| `@starting-style` | Newly (Aug 2024) | Chrome 117, FF 129, Safari 17.5 | Yes, as enhancement |
| `field-sizing` | Newly (Jun 2026) | Chrome 123, FF 152, Safari 26.2 | As enhancement |
| View transitions | Newly (Oct 2025) | Chrome 111, FF 144, Safari 18 | As enhancement |
| Scroll-driven animations | Newly (27 Oct 2026) | Chrome 115, FF 159, Safari 26 | As enhancement |
| Customizable `<select>` | **Not Baseline** | Chrome 135, Safari 27; no Firefox | Progressive enhancement only |
| Anchor positioning | **Not Baseline** (see below) | Sources disagree | Enhancement, keep JS positioning |
| `<dialog closedby>` | Not Baseline | Chrome 134, FF 141; no Safari | No, without fallback |
| `popover="hint"` | Not Baseline | Chrome 151, FF 153; no Safari | No |
| Interest invokers | Not Baseline | Chrome 149 only | No |

- **Source conflict on anchor positioning.** web-features lists only Safari 27 as meeting its bar. [caniuse](https://github.com/Fyrd/caniuse/blob/main/features-json/css-anchor-positioning.json) shows *partial* support from Chrome 125, Firefox 147, Safari 26 and Samsung 27, with notes on missing `position-anchor: normal`, `position-visibility` values and (Firefox) animation. It gives 0.78% full and 86.58% partial global usage. So core positioning works widely, but details vary.
- Customizable select falls back to a classic select in unsupported browsers. MDN warns that some JS frameworks block these features and that others cause **hydration failures under SSR** — [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Customizable_select) [primary].
- Indonesia mobile browser share, October 2026: Chrome 75.49%, Safari 18.04%, Samsung Internet 3.48%, UC 1.34%, Opera 1.11%, Firefox 0.22% — [StatCounter](https://gs.statcounter.com/browser-market-share/mobile/indonesia) [independent].
- Web components: [`referencetarget`](https://webstatus.dev/features/referencetarget) (ARIA references into shadow DOM) is limited availability, while [declarative shadow DOM](https://webstatus.dev/features/declarative-shadow-dom) is widely available.
- All major JS libraries still carry a JS positioning layer: Base UI depends on `@floating-ui/react-dom` and Radix Select and Popover on `@radix-ui/react-popper` (npm metadata).

### Inferences
- **Pick Base UI over Radix despite Radix's smaller JS.** The 10–30 KB difference is real, but the native-first rule removes most of it from product pages, and interactive overlays can be lazy-loaded. Maintenance risk is harder to mitigate later. If the team later finds JS weight dominating and Radix's activity continues for a further 6–12 months, Radix is a credible second choice. Note that this reverses if the team expects to use nearly all overlay components on first load.
- **React Aria is a poor default for this market**: the heaviest Select measured, and no bundled Indonesian strings for its built-in text. Use it surgically for what it does uniquely, such as complex date and number handling.
- Firefox at 0.22% makes Firefox-only gaps low-risk in Indonesia. **Safari gaps are not**, at 18%. Plan around iOS.
- Suggested mapping for this site:
  - SKU selector: `<fieldset>` + `<input type="radio">` styled with `:has(:checked)`.
  - Spec table: `<table>` with `scope`.
  - FAQ and long specs: `<details name>`.
  - Variant picker: `<select>`, with `base-select` only after testing hydration in the chosen framework.
  - Image lightbox and simple modals: `<dialog>`.
  - Filter drawer with swipe: Base UI Drawer, lazy-loaded.
  - Search combobox, toast, complex menus: Base UI.
- Treat download counts as weak signals: shadcn scaffolding and CI inflate them.

### Gaps
- No independent multi-screen-reader comparison, in particular none using TalkBack on Android, which matters most here. The team must run its own.
- Whether React Aria offers a supported way to add custom locale packs for built-in strings was not verified.
- Samsung Internet support for customizable select is not in web-features' core browser set, and Android version distribution for Indonesia was not found.
- I found no primary source explaining the Radix gap, nor any roadmap.

## Distribution: registry vs npm package vs workspace package, and what is shadcn/ui in 2026?

### Takeaway
shadcn/ui is now a **multi-base code distribution platform** rather than a Radix component set. For one site, a workspace package is simplest. For a system where code is the design source of truth, copy-paste drift is the critical weakness, so core components should stay centrally versioned, with registries reserved for blocks that consumers own.

### Cited Findings
**What shadcn/ui is in 2026**
- CLI 4.23.0 (27 Oct 2026), 16.9M weekly downloads, 127k stars — [npm](https://www.npmjs.com/package/shadcn), [GitHub](https://github.com/shadcn-ui/ui).
- **Three bases:** Base UI has been the default since July 2026 (citing v1.6.0 and 6M+ downloads at the time); Radix is fully supported, with `-b radix`; React Aria was added as a first-class base in July 2026 across all eight styles — [Base UI default](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default), [React Aria](https://ui.shadcn.com/docs/changelog/2026-07-react-aria).
- **Migration:** optional and per-component, driven by an agent skill. `asChild` becomes `render` mechanically, and behavioural differences are flagged instead of silently changed — [Base UI default](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default).
- **Tailwind:** v4 support since February 2025; `tailwind` config is left empty in monorepos with v4 — [changelog](https://ui.shadcn.com/docs/changelog), [monorepo](https://ui.shadcn.com/docs/monorepo).
- **Presets and themes:** `shadcn apply --preset <id>` switches a preset and **reinstalls existing components**. The page does not say what happens to local edits — [shadcn apply](https://ui.shadcn.com/docs/changelog/2026-04-shadcn-apply). Styles named in the changelog include Luma, Sera and Rhea — [changelog](https://ui.shadcn.com/docs/changelog).
- **MCP and agent context:** the changelog has MCP entries in April 2025 and with CLI 3.0 (August 2025), and `shadcn docs <component>` and shadcn/skills feed agents — [changelog](https://ui.shadcn.com/docs/changelog), [Component Composition](https://ui.shadcn.com/docs/changelog/2026-04-component-composition).
- **Support packages:** `cn` replaces `twMerge(clsx())` (September 2026) — [cn entry](https://ui.shadcn.com/docs/changelog/2026-09-cn). `shadcn eject` inlines `shadcn/tailwind.css` and removes the dependency — [eject](https://ui.shadcn.com/docs/changelog/2026-05-shadcn-eject).

**Private registries**
- Any public GitHub repo has been able to act as a registry since June 2026 — [changelog](https://ui.shadcn.com/docs/changelog). **Private GitHub repos since August 2026**, via `gh` credentials or `GH_TOKEN`, read through the Contents API and pinned to the resolved commit SHA — [Private GitHub Registries](https://ui.shadcn.com/docs/changelog/2026-08-private-github-registries).
- This supersedes a 2026 write-up calling private repos a limitation — [noqta](https://noqta.tn/en/news/shadcn-github-registries-code-sharing-2026) [weak, outdated].
- Self-hosted registries use namespaces with `${VAR}` headers or query parameters in `components.json` — [authentication](https://ui.shadcn.com/docs/registry/authentication).
- `registry:base` pins a primitive library; without one, items initialise as Base UI — [Base UI default](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default).

**Upgrade path**
- The CLI reference has **no general upgrade or diff-against-upstream command**. It offers only `add --diff [path]`, plus targeted `migrate` jobs (`cn`, `icons`, `base-color`, `rtl`, `radix`) — [CLI docs](https://ui.shadcn.com/docs/cli).
- Third-party guides name drift as the main cost — [UXMagic](https://uxmagic.ai/blog/shadcn-ui-explained) [vendor].

**Monorepo mode**
- `init --monorepo` produces `apps/web` + `packages/ui` with Turborepo. `add` puts primitives in `packages/ui`, and apps import `@workspace/ui/components/*`; blocks split across both — [shadcn monorepo](https://ui.shadcn.com/docs/monorepo). It is a hybrid: copied once, then shared as a workspace package.

**Options compared** (assessment is mine, built on the above):

| Model | Upgrade path | Consistency | Effort | Fit |
|---|---|---|---|---|
| Workspace package (JIT TS source) | Atomic, in one PR | Very high | Lowest | One repo, one or few apps |
| Versioned npm package | Semver + Changesets + codemods | High | Build, release, changelog | Two or more repos |
| Registry copy-paste | Manual; local forks diverge | Low over time | Low at first, rising | Blocks and templates meant to be modified |

- Medusa UI and Saleor macaw-ui, the closest open-source commerce systems, both publish versioned npm packages — [`@medusajs/ui`](https://www.npmjs.com/package/@medusajs/ui) 4.2.9, [`macaw-ui`](https://github.com/saleor/macaw-ui) 3.0.0.

### Inferences
- **Phase 1:** one pnpm workspace with `packages/ui` as a Just-in-Time package, using shadcn only to generate a Base UI starting point, then owning the code.
- **Phase 2:** when a second repo consumes it, publish to a private npm registry with tsdown + Changesets.
- **Blocks:** distribute composed e-commerce sections (PDP gallery, filter panel, review summary) via a private GitHub registry, because consumers legitimately adapt those.
- If code is the design reference, then a consumer's locally edited Button makes the reference false. That is why registry copying suits blocks and not core components. This argument is mine and has not been tested in the field.

### Gaps
- No detailed small-team post-mortem on registry drift was found. An [r/reactjs thread](https://redlib.hbubli.cc/r/reactjs/comments/1krvi8r/shadcn_registries_are_better_than_react_libraries) describes an npm-to-registry move, but its outcome was not visible.
- Behaviour of `shadcn apply` on locally edited files is undocumented on the page checked. Test it before relying on it.

## Styling and variants, and Core Web Vitals for Indonesian mobile

### Takeaway
Tailwind v4 + `cva` gives static CSS, near-zero variant runtime, the largest ecosystem, and now a stable owner. Performance budgets should use **Indonesia's P75 network (6.4 Mbps / 75 ms) and an Android mid-tier reference**, not the Ookla median. Speed-conversion evidence is directionally strong but almost all vendor-published.

### Cited Findings
**Tooling state**

| Option | Version | Usage (State of CSS 2025) | RSC/build notes |
|---|---|---|---|
| Tailwind v4 | [4.3.4](https://www.npmjs.com/package/tailwindcss), 2 Nov 2026 | 2,041 of 3,977 framework answerers | Static CSS. Min Chrome 111, Safari 16.4, FF 128 — [compat](https://tailwindcss.com/docs/compatibility) |
| CSS Modules | Built into bundlers | 1,037 of 3,718 CSS-in-JS answerers | Static. Tailwind [discourages combining them](https://tailwindcss.com/docs/compatibility) (each module reruns Tailwind) |
| vanilla-extract | [1.21.3](https://www.npmjs.com/package/@vanilla-extract/css) | 98 of 3,718 | Build-time; on [Next's supported list](https://nextjs.org/docs/app/guides/css-in-js). Used by [macaw-ui](https://github.com/saleor/macaw-ui) |
| Panda | [2.5.0](https://www.npmjs.com/package/@pandacss/dev) | 62 of 3,718 | v2 Rust rewrite, [24 Aug 2026](https://v2.panda-css.com/blog/panda-css-v2). **[No first-party Turbopack adapter](https://v2.panda-css.com/docs/styling/source-transforms)**; Next 16 defaults to Turbopack |

Usage counts are from the [State of CSS 2025 tools page](https://2025.stateofcss.com/en-US/other-tools/) [independent, self-selected]. Blogs cite 37% Tailwind usage ([example](https://www.digitalthriveai.com/en-us/resources/web-development/the-state-of-css-2025-survey-is-out/) [weak]), which differs from the 51.3% implied by the counts above; bases likely differ. shadcn/ui was reported by 766 of the 3,977.

- Runtime CSS-in-JS in Next's App Router works only in Client Components, using a style registry and `useServerInsertedHTML`; Emotion is still "working on support" — [Next.js docs](https://nextjs.org/docs/app/guides/css-in-js) (updated 24 Mar 2026) [primary].
- **Tailwind's stewardship changed.** Tailwind Labs laid off 3 of 4 engineers in January 2026, citing AI's impact on revenue — [DevClass](https://www.devclass.com/2026/01/08/tailwind-labs-lays-off-75-percent-of-its-engineers-thanks-to-brutal-impact-of-ai/) [independent]. It **joined Shopify on 9 Sep 2026**: MIT license unchanged, same team leading, "a stable long-term home", new commercial sign-ups closed — [Tailwind blog](https://tailwindcss.com/blog/tailwind-is-joining-shopify) [primary]. "Acquired" is secondary-source language.

**Variant libraries**
- `class-variance-authority` 0.7.1 was last published 26 Nov 2024 and still draws 77.2M/wk — [npm](https://www.npmjs.com/package/class-variance-authority). Its successor [`cva`](https://github.com/joe-bell/cva) is at 1.0.0-beta.12 (17 Sep 2026), still on a beta tag, with an active repo. Medusa pins `cva@1.0.0-beta.1` in production — [Medusa package.json](https://github.com/medusajs/medusa/blob/develop/packages/design-system/ui/package.json).
- [`tailwind-variants`](https://www.npmjs.com/package/tailwind-variants) 4.0.1 published 31 Oct 2026, 6.5M/wk.

Own measurement (same esbuild method; gz):

| Package | Min | Gz |
|---|---|---|
| `class-variance-authority` `cva` | 1.0 KB | **0.56 KB** |
| `cva` beta (`cva`, `cx`) | 3.4 KB | 1.65 KB |
| `tailwind-variants/lite` `tv` | 16.4 KB | 5.67 KB |
| `tailwind-variants` `tv` | 45.3 KB | 17.37 KB |
| `tailwind-merge` `twMerge` | 27.4 KB | 8.51 KB |
| `clsx` + `twMerge` helper | 27.8 KB | 8.65 KB |
| `cn` 0.5.2 | 26.6 KB | 10.84 KB |

- shadcn describes `cn` as "smaller, faster", without figures — [cn entry](https://ui.shadcn.com/docs/changelog/2026-09-cn). In my single measurement it is about 4% smaller minified and about 25% **larger** gzipped than the helper it replaces. Speed was not measured.

**Performance context**
- Mobile CWV (HTTP Archive, July 2025 primary dataset): LCP good 62%, INP good 77%, CLS good 81%, all three 48%. Secondary pages fare worse on INP than home pages (69% vs 80%). Median mobile lab TBT rose 58% to 1,916 ms — [Web Almanac 2025](https://almanac.httparchive.org/en/2025/performance) [independent].
- **Reference budget:** 9/3/100 network and Galaxy A24 4G class. For a 3-second load: JS-light 2.0 MiB total with 0.3 MiB JS; JS-heavy 1.2 MiB with 0.62 MiB JS. Emerging-market services should anchor on P90–P95 — [Alex Russell](https://infrequently.org/2025/11/performance-inequality-gap-2026/) [independent expert].
- **Indonesia P75 network:** 6.4 Mbps down, 2.1 up, 75 ms RTT — [same source](https://infrequently.org/2025/11/performance-inequality-gap-2026/).
- Ookla shows a much higher figure: 62.98 Mbps median mobile download (June 2026), seventh in Southeast Asia — [Databoks](https://databoks.katadata.co.id/en/technology-telecommunications/statistics/6a604db869d80/mobile-internet-download-speed-in-southeast-asia-june-2026-brunei-leads). Not contradictory: it measures speedtest-takers at the median, while Russell models slow-tail P75 throughput.
- Budget CPUs have not meaningfully improved since 2022; low-end is about 9x slower than current iPhones, mid-tier 3.5x+ — [Russell](https://infrequently.org/2025/11/performance-inequality-gap-2026/).

**Speed-to-conversion evidence** (all Google-published or Google-commissioned; none independently verified)
- **Tokopedia (Indonesia):** a Svelte-based lite homepage cut app JS 88% (320 KB to 37 KB), improved TTI by 4 s, and yielded +35% CTR and +8% conversion. Undated — [web.dev](https://web.dev/case-studies/tokopedia). A separate roundup cites LCP 3.78 s to 1.72 s and +23% session duration — [web.dev roundup](https://web.dev/case-studies/vitals-business-impact).
- **Deloitte/55:** 0.1 s mobile speed gain gave retail +8.4% conversions and +9.2% AOV. Commissioned by Google; EU/US data; sample size reported inconsistently by secondary sources — [web.dev](https://web.dev/case-studies/milliseconds-make-millions).
- **Rakuten 24:** +33.13% conversion and +53.37% revenue per visitor in an A/B test — [web.dev](https://web.dev/case-studies/rakuten).
- **redBus:** INP from about 870–900 ms to 350–370 ms with a 7% sales increase — [web.dev](https://web.dev/case-studies/redbus-inp).
- **QuintoAndar:** INP down 80% with +36% conversions — [web.dev](https://web.dev/case-studies/quintoandar-inp).

### Inferences
- **Choose Tailwind v4 + `class-variance-authority`.** `cva`'s entire footprint is under 1 KB. Reconsider `cva@1.0` when it leaves beta. Avoid full `tailwind-variants` on storefront routes unless its slots API earns 17 KB gz.
- **`tailwind-merge`/`cn` is the hidden cost: 8–11 KB gz.** Consider a closed component API without a free `className` merge on storefront atoms, using `clsx` only, and allow merging only in documented escape hatches.
- CSS Modules remains the right pick if multi-framework portability outranks ecosystem and shadcn compatibility. Panda and vanilla-extract have small communities (2.6% and 1.7%), and Panda has the Turbopack catch.
- **RSC:** static atoms (Badge, Card, Price, spec table) can stay Server Components because Tailwind and `cva` have no provider or runtime. Interactive primitives need client boundaries, so place them at leaves.
- **Proposed budgets to validate on real devices, not sourced targets:**
  - Critical-path JS on PDP and category routes ≤ about 200–250 KiB compressed. This is Russell's 0.3 MiB JS-light figure scaled for Indonesia's slower link.
  - Design-system share of first-load JS ≤ 40–50 KB brotli, excluding React. Base UI's full seven-part kit alone would be 64 KB br, so overlays must be lazy.
  - p75 field LCP ≤ 2.5 s, INP ≤ 200 ms.
  - Test on an A24-class phone, and run a low-end device check.
- Tokopedia is the most relevant precedent, but note that it was achieved by shipping far less JS, with Svelte on a lite route. It says nothing about React being unable to reach that, but it does show the size of the prize.

### Gaps
- No Indonesia-specific CrUX or CWV pass-rate dataset, and no independent (non-Google) conversion study was found.
- `cn` speed is unmeasured, and my size test is one bundler and one version.
- vanilla-extract's Turbopack status is unverified (its [docs page](https://vanilla-extract.style/documentation/getting-started/) does not mention Turbopack).
- Tailwind v4's real-world CSS size on a site like this is unmeasured. Russell's budget units are treated as critical-path wire bytes; verify before quoting exactly.
- Whether Tailwind's minimum browsers exclude meaningful Indonesian traffic is unknown without version-level data.

## Component API design: composition, slots, polymorphism, naming, docs anatomy

### Takeaway
The ecosystem has converged on **compound parts for multi-part widgets, simple config props for atoms, and a `render` prop replacing `asChild`** in new work. Docs structure is also becoming machine-relevant: composition trees help agents as well as people.

### Cited Findings
- **Base UI `render`.** A custom component must forward `ref` and spread received props onto its DOM node. Classes combine, render-element styles win, both click handlers run and all refs are kept. The function form receives `props` and `state` and is suggested for performance-sensitive apps — [Base UI composition](https://base-ui.com/react/handbook/composition) [primary].
- **`asChild` remains in use:** Medusa's Button still imports `Slot` from `radix-ui` — [button.tsx](https://github.com/medusajs/medusa/blob/develop/packages/design-system/ui/src/components/button/button.tsx). shadcn's migration converts `asChild` to `render` mechanically — [shadcn](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default).
- **"Render props" means something else in React Aria:** components expose state-based render props with built-in states and slots — [React Aria](https://react-aria.adobe.com/).
- **Radix is adding finer composition:** `unstable_` parts for Radio Group, Select, Slider and Switch — [Radix releases](https://www.radix-ui.com/primitives/docs/overview/releases).
- **shadcn publishes "Composition" sections** showing what wraps what, stating that LLMs and agents compose more reliably with them — [shadcn composition](https://ui.shadcn.com/docs/changelog/2026-04-component-composition).
- **State styling via data attributes:** the shared stylesheet provides variants like `data-open:` — [shadcn eject](https://ui.shadcn.com/docs/changelog/2026-05-shadcn-eject).

**Published API examples**

| System | Prop names | Polymorphism | Source |
|---|---|---|---|
| Medusa UI Button | `variant`: primary, secondary, transparent, danger. `size`: small, base, large, xlarge | `asChild` | [button.tsx](https://github.com/medusajs/medusa/blob/develop/packages/design-system/ui/src/components/button/button.tsx) |
| Geist Button | `size`, `variant`, `shape`, `prefix`, `suffix`, `loading`, `disabled` | Separate `ButtonLink` (Button props + `href`) | [Geist](https://vercel.com/geist/button) |

**Published docs structures**
- **Primer** splits Overview, Guidelines and Accessibility into separate pages. Guidelines has a labelled anatomy diagram (label, leading visual, trailing visual, trailing action), inactive-state behaviour, and Do/Don't pairs — [Primer Button](https://primer.style/product/components/button/guidelines/).
- **Geist** uses a runnable catalogue page: sizes, shapes, prefix/suffix, loading, disabled, best practices. It has no full prop reference, and its text says `type="secondary"` where examples use `variant` — [Geist](https://vercel.com/geist/button). That inconsistency illustrates the risk of hand-written prop docs.

**Behaviour is part of the contract**
- A Modal that changes focus return or Escape behaviour can be breaking even with unchanged props — [Path to Project](https://www.pathtoproject.com/blog/20260505-component-api-versioning-for-enterprise-design-systems) [weak].

### Inferences
Proposed conventions for this system:
- **Atoms use config props** with a closed set: `variant`, `size`, `disabled`, `loading`; `prefix`/`suffix` slots.
- **Multi-part widgets use compound parts:** `Select.Trigger`, `ProductCard.Media`.
- **Domain components use props with named slots**, not deep configuration objects. `SkuSelector` takes `options`, and `ProductCard` composes parts.
- **Links:** use `render` (function form on hot lists) only at interactive atoms. Do not introduce a free `as` prop. A dedicated `ButtonLink` is a simple alternative where type safety matters.
- **State expression:** expose states through `data-*` attributes, including `data-open`, `data-disabled`, `data-invalid`, to let designers read state from CSS and let VRT target states.
- **Standard doc page:** one-sentence purpose, Anatomy, Composition tree, Variants, a State matrix (default, hover, focus-visible, active, disabled, loading, invalid), 360/1440 responsive views, Keyboard + screen-reader notes, Generated props table, Do/Don't with Indonesian copy, and Changelog.

### Gaps
- No independent study compares `render` and `asChild` ergonomics or performance. The function-form performance advice comes from Base UI itself.
- The Primer fetch was truncated, so the full section list on its Guidelines page is not confirmed.

## Monorepo and release tooling

### Takeaway
**pnpm workspaces + Turborepo** is the proportionate default, and Nx is more than a small team needs. **tsdown** is the forward path for library builds but is pre-1.0. **Changesets** remains the standard, once there is something to publish.

### Cited Findings
- Turborepo sits **on top of** package-manager workspaces (a root `turbo.json`, a `package.json` per package), and documents Just-in-Time vs Compiled internal packages — [Turborepo docs](https://turborepo.dev/docs/crafting-your-repository/structuring-a-repository) [primary].
- [`turbo`](https://www.npmjs.com/package/turbo) 2.11.10 has 42.6M/wk. [`nx`](https://www.npmjs.com/package/nx) 24.0.3 has 14.5M/wk. Both are [very](https://github.com/vercel/turborepo) [active](https://github.com/nrwl/nx); Turborepo has 23 open issues and PRs, Nx 470.
- shadcn's monorepo mode uses Turborepo by default, which gives alignment — [shadcn monorepo](https://ui.shadcn.com/docs/monorepo).
- State of JS 2024 called pnpm the clear front-runner among monorepo tools — [State of JS 2024](https://2024.stateofjs.com/en-US/libraries/monorepo_tools). A comparable 2025 page could not be retrieved.
- Secondary guides: pnpm as baseline, Turborepo as usual starting orchestrator, Nx as a fuller platform — [PkgPulse](https://www.pkgpulse.com/guides/best-monorepo-tools-2026) [weak].

**Library builds**
- **[tsup](https://github.com/egoist/tsup):** the README warns it is "not actively maintained anymore" and points to tsdown. Yet [`tsup`](https://www.npmjs.com/package/tsup) 9.0.0 shipped 14 Oct 2026 and shows 13 commits in 90 days. Mixed signal; I would follow the README.
- **tsdown:** v0.23.4, Rolldown-based, auto `.d.ts`, has dedicated options pages for unbundle, CSS and package exports — [tsdown guide](https://tsdown.dev/guide/). `unbundle: true` maps source files one-to-one to output, which suits per-component imports and tree-shaking — [unbundle](https://tsdown.dev/options/unbundle) [primary]. 6.5M/wk, 65 commits in 90 days. Still pre-1.0.
- **tsc only:** Medusa builds with plain `tsc` + `tsc-alias` for CJS and ESM — [package.json](https://github.com/medusajs/medusa/blob/develop/packages/design-system/ui/package.json).

**Releases and policy**
- [`@changesets/cli`](https://www.npmjs.com/package/@changesets/cli) 3.0.3 (14 Sep 2026), 8.1M/wk, 74 commits in 90 days. Used by [macaw-ui](https://github.com/saleor/macaw-ui/tree/main/.changeset), and by [Radix](https://github.com/radix-ui/primitives/commits/main) per recent commit messages.
- **Clearest semver test:** if a team can bump, release, and users see no bugs without further code changes, it is not breaking. Layout-affecting design changes are breaking; markup is not public API — [Volvo Cars](https://designsystem.volvocars.com/web/developing/releases/) [primary for its own system].
- GOV.UK Frontend treats breaking changes as majors, avoids them for small reasons, and declares a public API — [GOV.UK](https://github.com/alphagov/govuk-frontend/blob/main/docs/contributing/versioning.md) [primary].
- **Codemods:** [`jscodeshift`](https://www.npmjs.com/package/jscodeshift) 17.4.0 (Jul 2026) and [`@ast-grep/cli`](https://www.npmjs.com/package/@ast-grep/cli) 0.51.1 (Nov 2026) are active. [`shadcn migrate`](https://ui.shadcn.com/docs/cli) and Storybook's [CSF upgrade codemods](https://storybook.js.org/blog/storybook-10/) are models. shadcn's [agent-skill migration](https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default) produces per-component reports and one commit per component, an emerging pattern worth copying.

### Inferences
- Initially there is no need for tsdown or Changesets; JIT packages avoid a build step. Add them together at Phase 2.
- Adopt a written definition of "breaking" that covers visual changes as well as behaviour, because without Figma the rendered output *is* the spec. Example: a colour token value change in `primary` is a design-major if it fails contrast or changes meaning, and is otherwise a minor with VRT sign-off.
- Pre-1.0 tsdown risk is low because config is small and swappable.
- Ship a codemod with any major that renames a prop. Hand-written ast-grep rules suit small changes; agent migration is worth trying for structural ones, with review.

### Gaps
- Vite library mode was not evaluated from primary sources in this pass; [Vite 98% satisfaction](https://2025.stateofjs.com/en-US/libraries/) is general, not about library mode.
- `use client` preservation in tsdown unbundle output was not confirmed. Test it, since it is critical for RSC.
- 2025 State of JS monorepo numbers were not retrieved.

## Docs as the design reference: what should designers browse?

### Takeaway
**Use two surfaces with one source of components.** Storybook 10 is the workbench and test harness. A Fumadocs site that imports the real components is the designer-facing reference. Very small teams can start with Storybook alone, and add the site when guidance outgrows MDX. Hosted tools (Zeroheight, Knapsack, Mintlify) are poor value here.

### Cited Findings
**Storybook**
- Current stable: 10.6.5 (27 Oct 2026), 34.6M/wk — [npm](https://www.npmjs.com/package/storybook). Storybook 10 launched 28 Oct 2025: ESM-only, install 29% smaller than 9, CSF Factories in preview, `sb.mock`, Vitest 4 support — [blog](https://storybook.js.org/blog/storybook-10/) [vendor/primary].
- **Storybook 11 is imminent:** alpha.9 published 2 Nov 2026; beta target 2 Nov, RC 24 Nov, stable **1 Dec 2026** (moved back on 29 Sep). As of 3 Nov the latest tag is still alpha.9, so the 2 Nov beta target has apparently not been met yet and the December date may move. The theme is "agent-ready", with MCP, skills, and support across React, Vue, Angular, Svelte and Web Components; deprecated APIs are removed — [release plan](https://github.com/storybookjs/storybook/discussions/36230), [releases](https://github.com/storybookjs/storybook/releases). CSF Factories were [expected to become the default in 11](https://storybook.js.org/blog/storybook-10/).
- **MCP:** `@storybook/addon-mcp` serves `/mcp` with development, docs, and testing toolsets (`docs-list`, `docs-show`, `stories-preview`, `test-run`, and more). It is **"in preview"**. The docs toolset needs the components manifest, which is off by default in 10.6 and available only for React frameworks, `angular-vite`, and `vue3-vite` — [MCP docs](https://storybook.js.org/docs/ai/mcp/overview). [11 alpha.2](https://github.com/storybookjs/storybook/releases) enables it by default for those frameworks. 3.5M/wk on [npm](https://www.npmjs.com/package/@storybook/addon-mcp).
- **Embedding:** iframes are supported but your Storybook "must be published and publicly accessible"; oEmbed works when published via Chromatic — [embed docs](https://storybook.js.org/docs/sharing/embed). Portable stories (`composeStories`) are documented for test environments; rendering them in a docs site is not addressed — [portable stories](https://storybook.js.org/docs/api/portable-stories/portable-stories-vitest).
- **Satisfaction:** Storybook is used by 56.1% of respondents, but satisfaction is 69% vs Vitest 97% and Playwright 94% — [State of JS 2025](https://2025.stateofjs.com/en-US/libraries/) [independent].
- **Custom sites:** Storybook says they need "a substantial investment", and that Canvas and Spark embed story iframes in their doc pages — [Storybook blog](https://storybook.js.org/blog/4-ways-to-document-your-design-system-with-storybook/) [vendor].

**Docs frameworks**

| Tool | Version | Weekly downloads | Activity | Fit |
|---|---|---|---|---|
| [Fumadocs](https://github.com/fuma-nama/fumadocs) | 16.17.10, 2 Nov 2026 | 3.2M (core) | 100+ commits, 6 open | React docs: [Next.js, Waku, React Router, TanStack Start](https://www.fumadocs.dev/docs) |
| [Starlight](https://github.com/withastro/starlight) | 0.42.8, 30 Oct 2026 | 2.15M | 100+ commits, 36 open | Framework-neutral; pre-1.0 versioning |
| [Docusaurus](https://github.com/facebook/docusaurus) | 3.10.2, Jul 2026 | 1.94M | 100+ commits, 435 open | Solid but generic |
| [Nextra](https://github.com/shuding/nextra) | 4.6.1, Dec 2025 | 314k | **0 commits** in 90 days | Avoid for now |
| [Ladle](https://github.com/tajo/ladle) | 5.1.1, Nov 2025 | 471k | **0 commits** in 90 days | Workbench only, slowing |
| [Histoire](https://github.com/histoire-dev/histoire) | 1.0.0-beta.1, Jan 2026 | 115k | 100+ commits, 205 open | Vue/Svelte workbench, still beta |

- **Fumadocs prop tables:** `AutoTypeTable` generates them from TS types via the compiler API. It is RSC-only and needs build-time file access and a cache on serverless platforms — [AutoTypeTable](https://www.fumadocs.dev/docs/ui/components/auto-type-table) [primary]. i18n and `llms.txt` are listed features — [Fumadocs](https://www.fumadocs.dev/docs). The site does not mention Twoslash or live previews on the overview page.
- **Real-world signal:** shadcn/ui's own site uses `fumadocs-core`, `fumadocs-ui`, `fumadocs-mdx`, and `fumadocs-docgen` on Next 16 and renders all three bases — [apps/v4/package.json](https://github.com/shadcn-ui/ui/blob/main/apps/v4/package.json). Base UI's docs use `@next/mdx` with MUI's internal docs infra — [docs/package.json](https://github.com/mui/base-ui/blob/master/docs/package.json).

**Hosted platforms** [vendor pricing pages]
- [Zeroheight](https://zeroheight.com/pricing/): Free for 1 editor and 1 styleguide; Starter $49 per editor/month (up to 5 editors, $59 monthly billing); Enterprise custom. Lists Storybook, Git, and live React components as features; per-tier availability is unclear.
- [Knapsack](https://www.knapsack.cloud/pricing): no public prices, annual billing, minimum 5 users, no free trial; renders React, Vue, Web Components, and others. Enterprise-oriented.
- [Mintlify](https://www.mintlify.com/pricing): Starter $0 (5 editors, custom domain); Pro $450/month annually. Positioned as a "knowledge platform built for agents"; "custom components" are listed, framework not specified.

### Inferences
- **Why not Storybook alone as the designer surface:** it is excellent for state matrices and viewports, but its navigation, developer controls and tone suit engineers. Anatomy, guidance and Indonesian usage examples read better on a proper site. This is judgment, based on what Primer and Geist publish rather than on measured designer preference.
- **Why not iframes:** public hosting is required, iframes on mid-tier phones are heavy, and the docs site can import the same real components directly, so previews use the production bundle and CSS.
- **Sequence:**
  1. Storybook-only, with one MDX per component, for the first 10–15 components.
  2. Add the Fumadocs app in the same monorepo, sharing example files between stories and docs (`examples/*.tsx`), so one file feeds both.
  3. Enable MCP and the manifest for agents, as it is preview-grade but cheap to try.
- **Timing:** start on 10.6 with CSF that upgrades cleanly, and plan the move to 11 after its RC or stable release. Avoid the alpha for production work.
- **Fumadocs needs a React host even if the product is Vue or Astro.** In that case, use Starlight.
- Designers without Figma need a **stable URL per component, per state, per viewport**. Make these a site requirement, as they become design handoff links.

### Gaps
- No credible engineering write-up was found comparing designer adoption between Storybook and a custom site, and no study of designers using code-based references after dropping Figma. Toolradar and tech-interview pages found were [weak].
- Sharing examples between Storybook and Fumadocs is a proposed approach, not a documented pattern from either project; prove it in a spike.
- Astro-component support in Storybook was not verified.

## Quality automation

### Takeaway
A credible small-team gate set is: Storybook-driven Vitest browser tests, axe with **WCAG 2.2 explicitly enabled**, a hosted visual-review tool, token lint rules, and size and Lighthouse budgets. Two pitfalls: **Lost Pixel is gone**, and **axe's WCAG 2.2 target-size rule is off by default**, which matters for a 360px mobile-first site.

### Cited Findings
**Interaction tests**
- Vitest Browser Mode has been stable since Vitest 4 (22 Oct 2025) — [Vitest 4](https://vitest.dev/blog/vitest-4). Latest [`vitest`](https://www.npmjs.com/package/vitest) is 5.1.0 (2 Nov 2026). Survey satisfaction is 97% — [State of JS 2025](https://2025.stateofjs.com/en-US/libraries/).
- `@storybook/addon-vitest` turns each story into a smoke test, and runs play functions, in real Chromium via Playwright. It offers coverage and CI via `vitest --project=storybook`. **It needs a Vite-based Storybook framework**, and Vitest 3.0+ — [Vitest addon docs](https://storybook.js.org/docs/writing-tests/integrations/vitest-addon) [primary].

**Accessibility**
- The Storybook a11y addon uses axe-core. `parameters.a11y.test` takes `off`, `todo` or `error`, and **only `error` fails CI**. By default it checks WCAG 2.0/2.1 A and AA plus best practices — [a11y docs](https://storybook.js.org/docs/writing-tests/accessibility-testing) [primary].
- axe's WCAG 2.2 category has one rule, `target-size` (tags `wcag22aa`, `wcag258`), which is **disabled by default** "until WCAG 2.2 is more widely adopted" — [axe rule descriptions](https://raw.githubusercontent.com/dequelabs/axe-core/develop/doc/rule-descriptions.md) [primary].
- SC 2.5.8 requires 24×24 CSS px with exceptions (spacing, equivalents, inline, user-agent controlled, essential) — [W3C](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) [primary].
- Coverage: Deque's figure is 57% **by issue volume** (2,000+ audits, nearly 300,000 issues, 2021). This is not 57% of WCAG criteria, and Storybook's wording ("up to 57% of WCAG issues") blurs that — [Deque](https://www.deque.com/blog/automated-testing-study-identifies-57-percent-of-digital-accessibility-issues/) [vendor].
- **`eslint-plugin-jsx-a11y`:** last release 6.10.2 (Oct 2024), and peer range stops at ESLint 9 ([npm](https://www.npmjs.com/package/eslint-plugin-jsx-a11y)), while current [ESLint is 10.14.0](https://www.npmjs.com/package/eslint). ESLint 10 support requests have been open since February 2026 ([#1075](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/issues/1075), [#1079](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/issues/1079), [#1081](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/issues/1081)). 65.4M/wk anyway. [`oxlint`](https://www.npmjs.com/package/oxlint) 1.90.0 has a [`jsx_a11y` rule directory](https://github.com/oxc-project/oxc/tree/main/crates/oxc_linter/src/rules/jsx_a11y) with 36 entries.

**Visual regression**

| Tool | Status | Free tier | Paid | Notes |
|---|---|---|---|---|
| [Chromatic](https://www.chromatic.com/pricing) | [`chromatic`](https://www.npmjs.com/package/chromatic) 18.13.9, 2 Nov 2026 | 5,000 snapshots/mo, about 25,000 TurboSnaps; Chrome only; unlimited users | Starter $179 (35k), Pro $399 (85k); Starter overage $0.008 | Adds Safari, Firefox, Edge from Starter; hosts Storybook; oEmbed |
| [Argos](https://argos-ci.com/pricing) | [`@argos-ci/playwright`](https://www.npmjs.com/package/@argos-ci/playwright) 7.8.0, Oct 2026 | 5,000 screenshots/mo; commercial OK; uploads pause at limit | Pro $100 (35k); $0.004 overage, $0.0015 for Storybook | Smaller project: [656 stars](https://github.com/argos-ci/argos) |
| Percy | [`@percy/cli`](https://www.npmjs.com/package/@percy/cli) 1.32.12, Oct 2026 | Not retrieved | Not retrieved | BrowserStack product |
| Lost Pixel | **[Archived](https://github.com/lost-pixel/lost-pixel)**; README says the team is joining Figma and "sunsetting the product" | n/a | n/a | **Do not adopt.** npm last published Nov 2024 |
| [Vitest `toMatchScreenshot`](https://vitest.dev/guide/browser/visual-regression-testing) | Part of Browser Mode | Free | CI compute | Baselines committed per browser/platform; Docker "strongly recommended" |
| [Playwright snapshots](https://playwright.dev/docs/test-snapshots) | 1.64.1 | Free | CI compute | Rendering varies by OS, hardware, power source, headless mode; run where baselines were made |

**Token enforcement**
- [`eslint-plugin-better-tailwindcss`](https://www.npmjs.com/package/eslint-plugin-better-tailwindcss) 4.10.0 (Oct 2026): `no-restricted-classes` accepts regexes, including an official example banning arbitrary values such as `text-[#fff]` — [rule doc](https://raw.githubusercontent.com/schoero/eslint-plugin-better-tailwindcss/main/docs/rules/no-restricted-classes.md). Also has [`no-unknown-classes`, `no-conflicting-classes`, `no-deprecated-classes`](https://github.com/schoero/eslint-plugin-better-tailwindcss/tree/main/docs/rules). The fix option can auto-suggest a token replacement, such as `text-green-500` to `text-success`.
- [`eslint-plugin-tailwindcss`](https://github.com/francoismassart/eslint-plugin-tailwindcss) 4.4.0 (Aug 2026): "Made for Tailwind CSS v4", has `no-arbitrary-value` and `no-custom-classname`.
- Stylelint [`color-no-hex`](https://stylelint.io/user-guide/rules/color-no-hex/) bans hex values; [`stylelint-declaration-strict-value`](https://www.npmjs.com/package/stylelint-declaration-strict-value) 1.12.1 (Aug 2026) exists for enforcing variables; [`stylelint`](https://www.npmjs.com/package/stylelint) is at 17.16.0.

**Budgets**
- [`size-limit`](https://github.com/ai/size-limit) 14.3.0 (Oct 2026), active. [`@lhci/cli`](https://github.com/GoogleChrome/lighthouse-ci) 0.16.0 published 2 Nov 2026, active.

### Inferences
**Suggested PR gates**
1. Typecheck + lint (token rules at error).
2. `vitest --project=storybook`: stories as smoke tests, plus play functions.
3. a11y at `error`, adding WCAG 2.2:
```ts
// .storybook/preview.ts (verify against your Storybook version)
parameters: { a11y: { test: 'error', options: { runOnly: [
  'wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice' ] } } }
```
4. Visual diff across 360 and 1440 widths, with designer sign-off in the review UI. Without Figma, **this review is the design approval step**.
5. `size-limit` per entry point and per component.
6. Lighthouse CI on a built docs or demo route with mobile throttling matching Indonesia P75, to catch regressions. Field RUM on real traffic remains the authority.

**Visual tool choice**
- Start with **Chromatic Free**, because it hosts the Storybook and gives non-developers a review UI.
- Estimate cost early. Example with assumed numbers: 60 components × 8 stories × 2 viewports = 960 snapshots per full build, which is about 5 full builds on 5,000/month. TurboSnap reduces this materially. Whether each viewport mode bills separately should be confirmed.
- Argos Pro at $100 has cheaper Storybook overage and is the natural cost-out; it has a lower-capacity, pause-at-limit free tier and a smaller vendor footprint.
- Self-hosted Vitest in Docker is the zero-subscription fallback, but needs baseline files in Git and gives designers no review UI.

**Other**
- Chromatic's Free plan is Chrome-only. Since Safari is 18% in Indonesia, include periodic iOS checks by hand or move to Starter.
- Use `oxlint` for JSX a11y if on ESLint 10, or pin ESLint 9. Confirm whether `better-tailwindcss` can run in the same setup.
- Arbitrary-value bans will also catch legitimate cases like `w-[var(--x)]`. Refine the regex, or allow a `/* token-exempt */` comment convention.
- Automated checks do not replace manual testing. Add a release checklist with TalkBack on an Android phone, VoiceOver on iOS, keyboard-only, and 200% zoom at 360px.
- A review tool fills part of Figma's role, so choose it with designers' involvement.

### Gaps
- Percy pricing could not be retrieved.
- The Lost Pixel announcement page timed out (HTTP 504); status comes from the repo README and archived flag. Date of sunset is unknown.
- Compatibility of `@storybook/addon-vitest` 10.6 with Vitest **5.x** was not confirmed (docs say "3.0 or later"). Check before pinning.
- Whether Storybook's Chromatic runner counts each viewport as a separate billed snapshot was not verified. I also did not verify in this session that Chromatic's company maintains Storybook (background knowledge), which is relevant to vendor bias.

## Reference systems: what can be learned from Polaris, Medusa UI, Geist, and Saleor?

### Takeaway
Commerce systems share a recognisable shape: **a small set of packages, colocated stories and tests, one primitive layer, and semver**. Polaris's web component move is instructive, but it is driven by platform-owner needs that do not apply to a single storefront.

### Cited Findings
**Shopify Polaris**
- `@shopify/polaris` (React) is **deprecated and no longer maintained**: "use Polaris web components" — [npm deprecation message](https://www.npmjs.com/package/@shopify/polaris). The repo is archived as [`polaris-react-archive`](https://github.com/Shopify/polaris-react-archive). Still 350k/wk.
- This corrects older sources: Shopify forum threads and earlier posts do not state deprecation, but the npm message now does.
- Web components were announced as an RC on 21 May 2025 and became stable on 1 Oct 2025. Delivered from Shopify's CDN so apps inherit updates; said to work with any framework. Stated benefit: removing React runtime overhead in UI extensions; "significantly smaller and faster", **with no figures published** — [announcement](https://shopify.dev/blog/polaris-unified-and-for-the-web), [stable post](https://shopify.dev/changelog/blog/polaris-goes-stable-the-future-of-shopify-app-development-is-here) [vendor].
- Each surface (Admin, Checkout, Customer accounts, POS) has its own component subset — [Polaris docs](https://shopify.dev/docs/api/polaris).
- Migration is per component, such as `Button` to `s-button` — [migration guide](https://shopify.dev/docs/apps/build/app-home/migrate-from-polaris-react/button.md). A community gotcha: `s-button-group` content disappeared without the required slot attributes — [forum](https://community.shopify.dev/t/s-button-group-not-showing-buttons/22806) [anecdote].
- Shopify now also hosts Tailwind — [Tailwind blog](https://tailwindcss.com/blog/tailwind-is-joining-shopify).

**Medusa UI** ([repo path](https://github.com/medusajs/medusa/tree/develop/packages/design-system))
- Packages: `ui`, `icons`, `ui-preset` (Tailwind preset), `toolbox`.
- `@medusajs/ui` 4.2.9 has 46 entries in `src/components`, and 339k/wk on [npm](https://www.npmjs.com/package/@medusajs/ui).
- Colocated per component: `button.tsx`, `button.stories.tsx`, `button.spec.tsx`, `index.ts` — [folder](https://github.com/medusajs/medusa/tree/develop/packages/design-system/ui/src/components/button).
- Stack: `cva` beta, Tailwind classes using semantic names like `bg-ui-button-neutral`, Radix **plus** `react-aria`/`react-stately`, `tailwind-merge`, `sonner`, TanStack Table, Storybook, Vitest, `tsc` builds. Peer dependency is React ^18.3.1 — [package.json](https://github.com/medusajs/medusa/blob/develop/packages/design-system/ui/package.json).
- My reading: it serves Medusa's admin UI more than a storefront; I did not find a source stating this explicitly.

**Saleor macaw-ui** ([repo](https://github.com/saleor/macaw-ui))
- v3.0.0 (14 Oct 2026). Stack: vanilla-extract recipes, individual Radix packages, `downshift`, Floating UI. Scripts include `chromatic`, `build-storybook`, `knip`, `bundle-visualizer`. Uses Changesets. Storybook has `.storybook/components` for `Colors`, `Spacings`, `Typography`, `Shadow`, and more — token documentation built inside Storybook. 120 stars, also dashboard-focused.

**Vercel Geist**
- Single page per component with runnable TSX. Imports from `@vercel/geistcn/components`. No license, repo or install steps shown on the page checked — [Geist Button](https://vercel.com/geist/button). The name suggests a shadcn-style lineage, but that is my speculation.

### Inferences
Take from these systems:
- **Medusa's layout:** the most directly reusable structure. Colocate component, stories, tests and index in one folder, with `icons` and a Tailwind preset as sibling packages.
- **Macaw's tooling set:** `knip` and a bundle visualizer are cheap additions, and token pages inside Storybook are a useful, low-cost idea.
- **Geist's docs:** copy the runnable-catalogue format, but generate prop tables to avoid its drift.
- **Mixing primitive libraries** as Medusa does (Radix + React Aria hooks) is a real, workable pattern for filling gaps, at a bundle-size cost.
- **Do not copy Polaris's CDN model.** CDN-managed auto-updates suit a platform owner governing thousands of third-party apps. A single storefront wants control, pinning, VRT sign-off, and no third-party critical script.
- **The real lesson from Polaris** is that even a very large React design system can be deprecated quickly: about 15 months separate the May 2025 RC from the August 2026 npm metadata update and September 2026 repo activity (the exact deprecation date is inferred from those timestamps). So keep app code insulated through your own component API, even when wrapping a third-party primitive library.
- None of these is a true **storefront** system. Patterns for PDP, SKU selection, and reviews must come from elsewhere, or be designed by the team.

### Gaps
- I found no open-source, actively maintained, storefront-focused design system with a comparable published structure. Saleor's storefront repo and Hydrogen were not examined.
- Geist's source and licensing status remain unverified, and whether `@vercel/geistcn` is publicly installable was not checked.
- Shopify has published no quantified before/after size or performance data for the Polaris migration.

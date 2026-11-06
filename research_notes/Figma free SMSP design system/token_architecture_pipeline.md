# Design Token Architecture and Pipeline for a Code-First, No-Figma Design System

All sources accessed 2026-11-03 unless noted. npm versions and dates come from the npm registry on that day.

Evidence labels:
- "First-hand test" means a smoke test I ran on 2026-11-03 with `style-dictionary@5.7.1` and `@terrazzo/cli@2.10.0` plus its plugins. The fixture was a small DTCG 2025.10 token set and a resolver file. It is not a conformance run.
- "Vendor claim" means marketing or self-description that was not independently verified.

## DTCG format: status, contents, and tool support

### Takeaway
DTCG 2025.10 (28 Oct 2025) is the first stable version and the only one as of Nov 2026, so it is safe to author in. It is a W3C Community Group report, not a W3C Standard. Tool support is uneven: in my test Terrazzo 2.10 handled everything in the fixture, while Style Dictionary 5.7.1 silently mis-handled `$ref`, `$extends`, gradients and resolvers.

### Cited Findings

**Status**
- The first stable version, 2025.10, was published on 28 Oct 2025 and has three modules: Format, Color and Resolver. The report says "This specification is considered stable" and "Further updates will be provided in superseding specifications." — [DTCG Technical Reports 2025.10](https://www.designtokens.org/tr/2025.10/); [DTCG blog](https://www.designtokens.org/blog/)
- The document is "not a W3C Standard nor is it on the W3C Standards Track." Its labels also conflict: the header says "Final Community Group Report" and the status text says "Candidate Recommendation." — [DTCG Technical Reports 2025.10](https://www.designtokens.org/tr/2025.10/)
- I found no 2026 stable revision. The repo's 2026 activity includes a conformance test suite for Format and Resolver (`@dtcg/test-suite`, added 2026-09-08) and an editorial fix to MAY/MUST wording on JSON Pointer support. — [community-group commits](https://github.com/design-tokens/community-group/commits/main); [test-suite README](https://github.com/design-tokens/community-group/tree/main/test-suite)
- The only 2026 blog post is "Thank you, Jina and Val" (17 Jun 2026). I could not read its body. — [DTCG blog](https://www.designtokens.org/blog/)

**What the Format module specifies**
- Basic types are Color, Dimension, Font family, Font weight, Duration, Cubic Bézier and Number. Composite types are Stroke style, Border, Transition, Shadow, Gradient and Typography. — [Format 2025.10](https://www.designtokens.org/tr/2025.10/format/)
- Dimension is an object with a numeric `value` and a `unit`, and the unit "may only be `px` or `rem`." — [Format 2025.10 §8.2](https://www.designtokens.org/tr/2025.10/format/)
- There are two alias syntaxes. Curly braces (`{group.token}`) "can ONLY target complete tokens." JSON Pointer `$ref` (`#/colors/blue/$value/components/0`) can reach property-level values. — [Format 2025.10 §7.1](https://www.designtokens.org/tr/2025.10/format/)
- Group features:
  - `$type` on a group is inherited from the closest parent group.
  - `$extends` deep-merges another group, and local definitions win.
  - `$root` gives a group a base value alongside its variants.
  - `$deprecated` accepts a boolean or an explanation string and cascades to children.
  - `$extensions` needs vendor-specific keys, and tools must preserve data they don't understand.
  - Source: [Format 2025.10](https://www.designtokens.org/tr/2025.10/format/)
- The file extension is `.tokens` or `.tokens.json`, and the MIME type is `application/design-tokens+json`. — [Format 2025.10](https://www.designtokens.org/tr/2025.10/format/)

**Color module**
- A color `$value` is an object with `colorSpace` and `components` (numbers or `none`), plus optional `alpha` and an optional 6-digit `hex` fallback. — [Color 2025.10](https://www.designtokens.org/tr/2025.10/color/)
- 14 color spaces are supported: `srgb`, `srgb-linear`, `display-p3`, `a98-rgb`, `prophoto-rgb`, `rec2020`, `hsl`, `hwb`, `lch`, `oklch`, `lab`, `oklab`, `xyz-d65` and `xyz-d50`. — [Color 2025.10](https://www.designtokens.org/tr/2025.10/color/)
- Gamut mapping is non-normative. The spec mandates no algorithm and tells authors to validate converted output. — [Color 2025.10](https://www.designtokens.org/tr/2025.10/color/)

**Resolver module**
- A `.resolver.json` file declares **sets** (collections of tokens) and **modifiers** (a `contexts` map such as light and dark, with an optional `default`). A required `resolutionOrder` applies them in sequence and the last occurrence wins. — [Resolver 2025.10](https://www.designtokens.org/tr/2025.10/resolver/)
- Input is a map such as `{ "theme": "dark" }`. Aliases are resolved only after flattening. A modifier may reference a set but not another modifier. — [Resolver 2025.10](https://www.designtokens.org/tr/2025.10/resolver/)

**Tool support**
- Terrazzo's docs say it is "the only tool that supports the full DTCG format." This is a vendor claim from the tool's own docs. The same page still describes resolver support as coming in 2.0, which is stale because 2.x has shipped. — [Terrazzo docs](https://terrazzo.app/docs/); [@terrazzo/cli on npm](https://www.npmjs.com/package/@terrazzo/cli)
- Style Dictionary's docs say "the latest format 2025.10 does not have full support yet," describing it as a work in progress in v5. — [Style Dictionary DTCG page](https://styledictionary.com/info/dtcg/)
- Tracking issue #1590 is still open (last activity 2026-10-12):
  - Color and Border/Shadow are done (5.3.0 and 5.3.1).
  - Dimension shipped in 5.4.0 and Duration in 5.7.0.
  - Gradient is not done.
  - Resolver is at the agreed-design stage only, with `resolver` as an alternative to `source`.
  - Sources: [SD #1590](https://github.com/style-dictionary/style-dictionary/issues/1590); [SD changelog](https://github.com/style-dictionary/style-dictionary/blob/main/CHANGELOG.md)
- First-hand test results on the same fixture:

| Fixture feature | Style Dictionary 5.7.1 (`css` transformGroup) | Terrazzo 2.10.0 (`plugin-css`) |
|---|---|---|
| `oklch` color object | Converted to hex; uses the `hex` field verbatim when present | `oklch()` plus a gamut-mapped sRGB value and `@media (color-gamut)` blocks |
| Dimension and duration objects | Correct (`16px`, `0.15s`) | Correct (`16px`, `150ms`) |
| `$root` | Correct (`--color-accent`) | Correct |
| Shadow | Correct | Correct |
| Typography | Shorthand output; `letterSpacing` dropped with a warning | Shorthand plus a variable per sub-value |
| Gradient | **Broken**: `[object Object],[object Object]` | Stop list emitted correctly |
| `$extends` | **Silently ignored**: inherited token missing | Correct (`--ext-button-bg`) |
| `$ref` to a whole value | **Broken**: `[object Object]` | Correct |
| `$ref` to a component | **Silently wrong**: `#000000` | Correct |
| Resolver file | **Silently ignored**: empty `:root {}` | Built light and dark permutations |
| `$deprecated` | Emitted with no warning | Emitted with no warning |
| Contrast linting | No equivalent found | `a11y/min-contrast` failed the build (3.69 vs 4.5) |

### Inferences
- Author only in DTCG 2025.10. The risk of format churn is low given the stable label and the "superseding specifications" policy.
- Style Dictionary's failures are silent, so they would ship wrong CSS rather than stop a build. This matters more than the feature gap itself.
- Use a portable subset: curly aliases only, no `$ref`, no `$extends`, no gradient tokens. Both tools handled that subset in my test, apart from Style Dictionary's `letterSpacing` warning, which keeps the choice of tool reversible.

### Gaps
- I found no published conformance results for any tool against `@dtcg/test-suite`, so "fully supports" remains unverified for every tool. My fixture is a smoke test, not a conformance run.
- I did not test Style Dictionary with custom preprocessors, which could fill some of its gaps.

## Token transformation tools: comparison and recommended default

### Takeaway
**Recommended default: Terrazzo 2.x (`@terrazzo/cli`, `plugin-css`), pinned to an exact version, with tokens kept in the portable DTCG subset.** Style Dictionary 5.x is the established, much larger alternative and the fallback for native platforms. It is not the default here because it lacks resolver support and fails silently on newer spec features. The main risk with Terrazzo is that it depends heavily on one maintainer. No SaaS platform is justified for a small team with no Figma.

### Cited Findings

| Tool | Current state (2026-11-03) | Monthly npm downloads (Oct 3 to Nov 1) | Fit: small team, no Figma, monorepo |
|---|---|---|---|
| **Terrazzo** | [`@terrazzo/cli` 2.10.0](https://www.npmjs.com/package/@terrazzo/cli), 21 Oct 2026; 2.0.0 on 17 Mar 2026; 484 stars | 482,289 | Strong. Resolver, lint and Tailwind plugin built in |
| **Style Dictionary** | [5.7.1](https://www.npmjs.com/package/style-dictionary), 24 Oct 2026; 5.0.0 on 16 May 2025; 4,875 stars | 7,755,664 | Good for the portable subset. No resolver yet |
| **Tokens Studio** | [`sd-transforms` 2.0.3](https://www.npmjs.com/package/@tokens-studio/sd-transforms), published 10 Dec 2025; Figma plugin repo active | 717,713 (`sd-transforms`) | Weak. The center of gravity is the Figma plugin |
| **Supernova** | Pricing: Starter free, Pro $399/month, Enterprise custom | n/a | Weak. Paid, with Figma-linked features on every tier |
| **Knapsack** | Enterprise "digital production platform"; pricing undisclosed | n/a | Weak. Enterprise and AI-conformance focus |
| **Specify** | Shut down 15 Nov 2024 | n/a | Dead |
| **Theo** | [8.1.5](https://www.npmjs.com/package/theo), last npm change Jun 2022 | 59,556 | Dead in practice |
| **Diez** | Last push Dec 2022 | not checked | Dead in practice |
| **Cobalt UI** | Predecessor of Terrazzo; [`@cobalt-ui/cli` 1.12.0](https://www.npmjs.com/package/@cobalt-ui/cli) | 1,367 | Do not start here |

Download counts are from the [npm downloads API](https://api.npmjs.org/downloads/point/last-month/style-dictionary). They include CI and transitive installs, so treat them as rough signals only.

**Terrazzo**
- Packages exist for CSS, CSS-in-JS, Sass, JS, Swift, Tailwind, Vanilla Extract and token listing. There is no Android or Compose package. — [Terrazzo packages](https://github.com/terrazzoapp/terrazzo/tree/main/packages)
- Lint rules include `a11y-min-contrast`, `a11y-min-font-size`, `colorspace`, `consistent-naming`, `descriptions`, `duplicate-values`, `max-gamut`, `required-children`, `required-modes` and validators for each type. — [Terrazzo lint rules](https://github.com/terrazzoapp/terrazzo/tree/main/packages/parser/src/lint/plugin-core/rules)
- CLI commands include `build`, `lint`, `check` (validates against the DTCG spec) and `bundle` (merges a resolver's files into one JSON file). — [Terrazzo docs](https://terrazzo.app/docs/)
- Adoption: `WordPress/gutenberg` (`packages/theme`), `guardian/csnx` (`libs/@guardian/pulse`) and `ITS-HCD/nysds` declare `@terrazzo/cli`. — [@wordpress/theme package.json](https://github.com/WordPress/gutenberg/blob/trunk/packages/theme/package.json); [GitHub code search](https://github.com/search?q=%22%40terrazzo%2Fcli%22+filename%3Apackage.json&type=code)
- WordPress is the closest public reference. It uses DTCG 2025.10 source files plus a `wpds.resolver.json`, with resolver overrides for corner radius and pixel density. — [Gutenberg tokens guide](https://github.com/WordPress/gutenberg/blob/trunk/packages/theme/tokens/README.md)
- Maintainer concentration: `drwpow` has 602 commits and the next human contributor has 21. — [Terrazzo contributors](https://github.com/terrazzoapp/terrazzo/graphs/contributors)
- The repo has 62 open issues and recent releases 2.8, 2.9 and 2.10 all landed in Oct 2026. — [Terrazzo changelog](https://github.com/terrazzoapp/terrazzo/blob/main/packages/cli/CHANGELOG.md)

**Style Dictionary**
- Large systems build on it: `@primer/primitives` declares `style-dictionary ^5.0.0` and `@carbon/themes` declares `^5.5.0`. — [Primer package.json](https://github.com/primer/primitives/blob/main/package.json); [Carbon themes package.json](https://github.com/carbon-design-system/carbon/blob/main/packages/themes/package.json)
- It ships predefined native formats: `ios-swift/*`, `android/resources`, `android/colors`, `compose/object`, `flutter/class.dart`. — [SD predefined formats](https://styledictionary.com/reference/hooks/formats/predefined/)
- It had several prototype-pollution advisories in 2026, all in `convertTokenData` "object" mode, and all patched (latest in 5.7.1). — [SD changelog](https://github.com/style-dictionary/style-dictionary/blob/main/CHANGELOG.md)
- Eight releases landed between 19 Aug and 24 Oct 2026, so maintenance is active. — [style-dictionary on npm](https://www.npmjs.com/package/style-dictionary)

**Vendors (all vendor claims unless noted)**
- Tokens Studio's site says it integrates with "PenPot, Figma, GitHub, VS Code, Framer," and claims "No proprietary formats." Its usage numbers refer to the Figma plugin ("300k users"). It does not confirm standalone operation or mention DTCG. — [Tokens Studio](https://tokens.studio/)
- Supernova's pricing page lists Figma variables import and Figma data sources on every tier, and does not describe a non-Figma token workflow or DTCG support. — [Supernova pricing](https://www.supernova.io/pricing)
- Knapsack positions itself for "enterprise teams," lists design tokens only as one context source, and gives no pricing. Its "95% fewer invented token names" claim has no stated methodology. — [Knapsack](https://www.knapsack.cloud/)
- Specify announced on 25 Oct 2024 that it would close on 15 Nov 2024, saying it "couldn't find our product-market fit." — [Specify blog](https://specifyapp.com/blog/the-end-of-specify)
- `salesforce/theo` returned 404 from the GitHub API, while the npm package remains. — [theo on npm](https://www.npmjs.com/package/theo)
- `diez/diez` was last pushed on 2022-12-10. — [diez repo](https://github.com/diez/diez)

### Inferences
- Recommended pipeline (design judgment, not a sourced standard):

```
packages/tokens/
  src/primitive/*.tokens.json     # OKLCH ramps, scale steps (internal)
  src/semantic/*.tokens.json      # public API, aliases only
  src/theme/{light,dark}.tokens.json
  ds.resolver.json                # sets + modifiers (theme; later brand, density)
  terrazzo.config.ts
  dist/tokens.css                 # :root and [data-theme] values
  dist/theme.css                  # @theme inline map for Tailwind
  dist/tokens.js + tokens.json    # JS consumers, docs, CI
```

- CI runs `tz check`, then `tz build` with lint, then a committed-output diff, then Changesets for versioning. `@changesets/cli` is at [3.0.3](https://www.npmjs.com/package/@changesets/cli).
- Pin Terrazzo exactly (no caret) and snapshot-test the generated CSS. Its pace of change and single-maintainer profile make unattended minor upgrades risky.
- Exit plan: if Terrazzo stalls, the portable subset can move to Style Dictionary with a small script to flatten themes. In my test that subset built correctly in both tools, except that Style Dictionary dropped `letterSpacing` from the typography shorthand (with a warning).
- Switch the recommendation to Style Dictionary if the team needs native output soon, or wants the most widely adopted tool and is happy to manage themes with separate builds. Avoid `sd-transforms` either way, since it exists for Tokens Studio's format.

### Gaps
- I found no independent head-to-head comparison of Terrazzo and Style Dictionary from 2026. The comparison rests on docs, changelogs and my smoke test.
- I found no published production post-mortems on Terrazzo 2.x.
- Knapsack and Tokens Studio Studio pricing were not visible on the pages I read.

## Tier architecture: what leading systems do, and when component tokens are overkill

### Takeaway
Leading systems disagree on the component tier, ranging from none at all (SLDS 2 global hooks, shadcn) to extensive (Spectrum, Carbon). Primitive plus semantic is the common core. **Recommendation: private primitives, public semantics, and component tokens only by exception.** Polaris is no longer a live reference, because its React repo is archived.

### Cited Findings

| System | Tiers in practice | Evidence |
|---|---|---|
| **WordPress DS** | Primitive (internal) → semantic (public API) | "Primitive tokens… are not part of the public API"; semantic tokens "are the public API." — [Gutenberg tokens guide](https://github.com/WordPress/gutenberg/blob/trunk/packages/theme/tokens/README.md) |
| **GitHub Primer** | `base` → `functional` → `component` | Directories in [src/tokens](https://github.com/primer/primitives/tree/main/src/tokens). `fgColor.default` aliases `{base.color.neutral.13}` — [fgColor.json5](https://github.com/primer/primitives/blob/main/src/tokens/functional/color/fgColor.json5). `button.default.fgColor.rest` aliases `{control.fgColor.rest}`, in a group labelled "component (internal)" — [button.json5](https://github.com/primer/primitives/blob/main/src/tokens/component/button.json5) |
| **Adobe Spectrum** | Palette → aliases → semantic → many component files | 441 keys in `color-palette`, 191 in `color-aliases`, 94 in `semantic-color-palette`, 345 in `layout`, 63 in `layout-component`, 91 source files overall. Source uses `value` and `uuid`, not `$value`. — [spectrum-design-data tokens](https://github.com/adobe/spectrum-design-data/tree/main/packages/tokens/src) |
| **IBM Carbon** | Core tokens + component tokens | Component tokens "should never be used for anything other than their own component." Names like `$text-primary`, `$layer-01`, `$button-primary-hover`. — [Carbon color tokens](https://carbondesignsystem.com/elements/color/tokens/) |
| **Salesforce SLDS 2** | Global hooks only, for now | "SLDS 2 doesn't support component-level styling hooks" (`--slds-c-*`), and Salesforce is working to enable them — [LWC guide](https://developer.salesforce.com/docs/platform/lwc/guide/create-components-css-custom-properties). Shared and component hooks are unsupported; replace with global hooks where possible — [SLDS best practices](https://lightningdesignsystem.com/dev-guidelines/best-practices) |
| **Atlassian** | Named `foundation.property.modifier` | Examples: `color.icon.success`, `color.text`, `opacity.disabled`. "A design token's name describes how it should be used." — [Atlassian design tokens](https://atlassian.design/foundations/tokens/design-tokens) |
| **Shopify Polaris** | Primitive `colors` → semantic aliases, with some component-named tokens in the semantic file | `bg-fill-brand-hover`, `input-bg-surface-hover`, `nav-bg-surface-active`, `avatar-bg-fill` — [color.ts](https://github.com/Shopify/polaris/blob/main/polaris-tokens/src/themes/base/color.ts). **Repo archived**; Polaris React is deprecated in favor of Polaris Web Components (1 Oct 2025) — [Polaris README](https://github.com/Shopify/polaris) |
| **Radix Colors** | A primitive scale with semantic meaning per step | 12 steps: 1–2 backgrounds, 3–5 component backgrounds, 6–8 borders, 9–10 solid fills, 11–12 text — [Radix scale docs](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale) |
| **shadcn/ui + Tailwind** | Semantic pairs only, mapped through `@theme inline` | `primary` / `primary-foreground`, plus `card`, `muted`, `border`, `ring`. `--radius` is one base value that scales the rest. — [shadcn theming](https://ui.shadcn.com/docs/theming) |

**Naming conventions seen**
- Foundation, property, modifier: Atlassian.
- Property then state, in camelCase: Primer (`bgColor`, `fgColor`, `.rest`, `.disabled`).
- Category, role, state, in kebab-case: Carbon, Polaris.
- Surface and foreground pairs: shadcn.

**Tailwind's naming constraint**
- Tailwind v4 derives utilities from a variable's namespace, such as `--color-*` for color utilities and `--text-*` for font sizes. — [Tailwind theme docs](https://tailwindcss.com/docs/theme)

### Inferences
- Component tokens are overkill when one brand, one platform and one monorepo own the components, which matches this project at the start. A component can reference semantic tokens directly and be changed in its own CSS.
- Add a component token only when one of these is true:
  - A value must differ by theme or brand in a way no semantic token captures.
  - A consumer outside the component package needs a supported override hook.
  - Several components must share a decision (Primer's `control.*` group is a good model).
- SLDS 2 is evidence that a large system can operate on global hooks, but Salesforce says it is still working to restore component hooks, so this may be a migration state rather than a design position.
- Spectrum's scale reflects multi-platform, multi-product needs and is not a template for a small team.
- Suggested naming for this project: use purpose-first names that do not repeat the Tailwind property. `--color-bg-page` produces the awkward class `bg-bg-page`, and `--color-text-default` produces `text-text-default`. Prefer names like `--color-surface`, `--color-surface-raised`, `--color-on-surface`, `--color-action`, `--color-on-action`, `--color-border-subtle`. Pair naming (`x` and `on-x`) also gives CI a mechanical list of contrast pairs.
- Keep primitives out of the public API by not mapping them in `@theme`, so `bg-blue-500` does not exist for product teams.

### Gaps
- The Atlassian page does not say whether primitives are exposed.
- SLDS documentation pages conflict slightly on namespaces and dates, and the design system site's hook page did not render for me. Current component-hook status should be rechecked before citing it as final.
- I did not find token counts for Polaris Web Components, or how tokens work after the move away from React.

## CSS output: Tailwind v4, modern CSS, and browser support for Indonesia

### Takeaway
Tailwind 4.3.4 (2 Nov 2026) is the current version. Map semantic variables with `@theme inline` and set values on `:root` and `[data-theme]`. Tailwind's floor (Chrome 111, Safari 16.4, Firefox 128) is acceptable, but **public data cannot show actual Chrome-for-Android versions in Indonesia**, and UC Browser is a real gap. Author in OKLCH, ship hex or `rgb()`, and avoid `light-dark()` and relative colors in token output.

### Cited Findings

**Tailwind v4**
- [`tailwindcss` 4.3.4](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.4) was released 2026-11-02; 4.3.0 on 2026-05-08, 4.0.0 on 2025-01-21. — [Tailwind changelog](https://github.com/tailwindlabs/tailwindcss/blob/main/CHANGELOG.md); [tailwindcss on npm](https://www.npmjs.com/package/tailwindcss)
- `@theme` variables create utilities and also compile to regular `:root` variables. They must be top-level, not nested under selectors or media queries. — [Tailwind theme docs](https://tailwindcss.com/docs/theme)
- Namespaces include `--color-*`, `--font-*`, `--text-*`, `--font-weight-*`, `--tracking-*`, `--leading-*`, `--breakpoint-*`, `--container-*`, `--spacing-*`, `--radius-*`, `--shadow-*`, `--ease-*` and `--animate-*`. — [Tailwind theme docs](https://tailwindcss.com/docs/theme)
- `@theme inline` uses the referenced value directly in the utility, which is what you need when a theme variable points to another variable. `@theme static` always emits all variables. `--*: initial` and `--color-*: initial` remove defaults. — [Tailwind theme docs](https://tailwindcss.com/docs/theme)
- Tailwind v4 "is designed for and tested on" Chrome 111 (Mar 2023), Safari 16.4 (Mar 2023) and Firefox 128 (Jul 2024). — [Tailwind compatibility](https://tailwindcss.com/docs/compatibility)
- v4.1 added fallbacks for oklab colors in older Safari, `@property`-dependent features in older Safari and Firefox, opacity modifiers (inlined) and gradient interpolation. Sites "will render and be usable" in older browsers, though not perfectly. — [Tailwind v4.1 blog](https://tailwindcss.com/blog/tailwindcss-v4-1)
- `@terrazzo/plugin-tailwind` generates an `@theme` block from a template using an `@tz` at-rule. Its docs warn that glob unpacking can produce names like `--color-blue-blue-0`. — [Terrazzo Tailwind docs](https://terrazzo.app/docs/integrations/tailwind/)
- First-hand test with a naive glob config (`color: ['color.**','bg.*','fg.*']`):
  - It produced doubled names (`--color-color-brand-500`).
  - It lost prefixes (`fg.default` became `--color-default`).
  - Aliases pointed to `--color-neutral-0`, which only exists if the `plugin-css` file is also loaded.
  - It emitted the raw P3 value `oklch(55% 0.2 250)` rather than the sRGB-safe value in `plugin-css` output.
  - A more explicit mapping may avoid these problems. I did not test one.

**Baseline status** (from [web-features data](https://unpkg.com/web-features/data.json))

| Feature | Baseline | Newly available | Widely available | Chrome / Safari / Firefox floor | Use in tokens? |
|---|---|---|---|---|---|
| Custom properties | Widely | 2017-04 | 2019-10 | 49 / 9.1 / 31 | Yes |
| `clamp()` | Widely | 2020-07 | 2023-01 | 79 / 13.1 / 75 | Yes |
| `@layer` | Widely | 2022-03 | 2024-09 | 99 / 15.4 / 97 | Yes |
| Container queries (size) | Widely | 2023-02 | 2025-08 | 105 / 16 / 110 | Yes |
| OKLCH | Widely | 2023-05 | 2025-11 | 111 / 15.4 / 113 | Author yes; ship with care |
| `color-mix()` | Widely | 2023-05 | 2025-11 | 111 / 16.2 / 113 | Runtime tints with a fallback |
| Native nesting | Widely | 2023-12 | 2026-06 | 120 / 17.2 / 117 | Source only if the build flattens it |
| `@property` | Newly | 2024-07 | ~2027-01 (projected) | 85 / 16.4 / 128 | Only for animating values |
| `light-dark()` | Newly | 2024-05 | ~2026-11-13 (projected) | 123 / 17.5 / 120 | No |
| Relative color | Newly | 2024-09 | ~2027-03 (projected) | 125 / 18 / 128 | No; compute at build time |
| Container style queries | Newly | 2026-05 | n/a | 111 / 18 / 151 | No |
| `contrast-color()` | Newly | 2026-04 | n/a | 147 / 26 / 146 | No |
| `@scope` | Newly | 2026-03 | n/a | 143 / 26.4 / 146 | No |
| `if()` | Not Baseline | n/a | n/a | Chrome 137 only | No |

Projected dates are my calculation from the Baseline rule of 30 months after "newly available."

- Sources disagree on relative color. web-features lists Chrome 125, while caniuse lists full support from Chrome 131 with partial support earlier and in Samsung Internet. — [caniuse data](https://github.com/Fyrd/caniuse); [web-features data](https://unpkg.com/web-features/data.json)
- `light-dark()` accepts two colors or two images, and needs `color-scheme: light dark` to be enabled. MDN still shows "Baseline 2024, Newly available." — [MDN light-dark()](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark)

**Indonesia usage (StatCounter, Oct 2026)**
- Platform: desktop 58.29%, mobile 41.22%, tablet 0.50%. September was 55.81 / 43.64 / 0.55. — [StatCounter platform, Indonesia](https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/indonesia)
- Mobile OS: Android 78.70%, iOS 21.22%. — [StatCounter mobile OS, Indonesia](https://gs.statcounter.com/os-market-share/mobile/indonesia)
- Mobile browsers: Chrome 75.53%, Safari 18.00%, Samsung Internet 3.48%, UC Browser 1.34%, Opera 1.11%, Firefox 0.22%. — [StatCounter mobile browser, Indonesia](https://gs.statcounter.com/browser-market-share/mobile/indonesia)
- Android versions: 16: 27.76%, 15: 17.72%, 14: 13.47%, 13: 11.40%, 12: 8.88%, 11: 9.54%, 10: 4.30%, 9: 2.67%, 8.x: 2.47%, 7.x: 0.55%, 6: 0.37%, 5.x: 0.26%. — [StatCounter Android version, Indonesia](https://gs.statcounter.com/android-version-market-share/mobile-tablet/indonesia)
- Chrome 139 requires Android 10, so Android 8 and 9 stop at Chrome 138. — [Android Central](https://www.androidcentral.com/phones/some-older-android-phones-will-no-longer-get-chrome-updates)
- Chrome 120 was reported in advance to require Android 8, leaving Android 7 at Chrome 119. This comes only from forward-looking 2023 reports, so it is partly verified. — [TuttoAndroid](https://www.tuttoandroid.net/news/2023/11/28/google-chrome-calendar-requisito-minimo-android-8-0-1022294/)
- The Chrome-for-Android version split is hidden. StatCounter groups it as one "Chrome for Android" row (72.07% of mobile), and caniuse's Indonesia data has a single unversioned row for it (34.58 points). — [StatCounter browser version, Indonesia](https://gs.statcounter.com/browser-version-market-share/mobile/indonesia); [caniuse region data for Indonesia](https://github.com/Fyrd/caniuse/blob/main/region-usage-json/ID.json)
- Share unsupported in Indonesia, calculated by joining caniuse's Sep 2026 Indonesia usage with web-features floors. This only covers browsers with version data, about 61.6 of 99.06 points, and excludes Android Chrome, UC, Samsung and Opera Mobile:

| Feature | Unsupported (points of ~61.6) |
|---|---|
| Custom properties | 0.11 |
| `clamp()` | 0.16 |
| `@layer` | 0.21 |
| Container queries | 0.47 |
| `@property` | 0.93 |
| OKLCH | 1.14 |
| `color-mix()` | 1.31 |
| Nesting | 2.71 |
| `light-dark()` | 3.48 |
| Relative color | 4.26 |

- caniuse shows no full support in UC Browser for Android 15.5 for LCH/Lab colors, container queries or nesting, while layers, custom properties and math functions are supported. — [caniuse data](https://github.com/Fyrd/caniuse)
- Desktop has its own long tail: Chrome 109 is 0.54 points, Chrome 120 is 0.35 and Chrome 119 is 0.27. — [caniuse region data for Indonesia](https://github.com/Fyrd/caniuse/blob/main/region-usage-json/ID.json)

**Terrazzo CSS output**
- `plugin-css` emits an sRGB-safe value by default, adds `@media (color-gamut: p3)` and `rec2020` overrides, and has a `legacyHex` option. — [Terrazzo CSS docs](https://terrazzo.app/docs/integrations/css/)
- Aliased values are redeclared in each mode block, so output is larger than expected. `include`, `exclude` and `only` can reduce it. — [Terrazzo CSS docs](https://terrazzo.app/docs/integrations/css/)
- First-hand test: an out-of-sRGB `oklch(0.55 0.2 250)` became `oklch(55.83% 0.1823 254.8)`, so hue shifted about 5° when mapped. The dark block repeated primitives as well as semantic tokens.

### Inferences
- **Recommended output shape** (shadcn's pattern; simpler and more predictable than generating theme values inside `@theme`):

```css
/* dist/tokens.css — generated */
:root { --surface: #ffffff; --on-surface: #13161a; --space-4: 1rem; }
[data-theme="dark"] { --surface: #13161a; --on-surface: #ffffff; }

/* dist/theme.css — generated or hand-kept, reviewed in PRs */
@theme inline {
  --*: initial;
  --color-surface: var(--surface);
  --color-on-surface: var(--on-surface);
  --spacing: 0.25rem;
  --radius-md: var(--radius-md-value);
  --text-body: var(--text-body-size);
  --text-body--line-height: var(--text-body-leading);
  --breakpoint-lg: 90rem;
}
```

- **Ship hex or `rgb()`, not `oklch()`, at the start.**
  - A custom property accepts `oklch()` even in a browser that can't parse it, so the failure appears where it is used: `color: var(--x)` becomes invalid at computed-value time, and an earlier fallback declaration does not apply. This is my understanding of standard CSS behavior and was not separately sourced here.
  - There is little to lose: this design targets sRGB, and P3 adds little on mid-tier phones.
  - Revisit if your own analytics show the UC and old-browser share is negligible.
  - Author tokens in OKLCH inside the sRGB gamut, and let Terrazzo's `max-gamut` rule block out-of-gamut values. That also removes the extra gamut media blocks and the hue shift.
- Do not use `light-dark()` for token output. It handles only colors and images, needs `color-scheme`, and locks the theme to two states, while a `[data-theme]` selector supports forced modes and later brands.
- Derive tints and hover states at build time as explicit tokens, instead of relative color at runtime. Use `color-mix()` only with a solid-color fallback declared first.
- OS-level limits suggest a small hard floor. About 93.6% of Android mobile is on Android 10 or later and can run current Chrome. About 5.1% (Android 8–9) can reach Chrome 138, which covers everything in the table except `contrast-color()` and `@scope`. About 1.2% (Android 5–7) is stuck below nesting and `light-dark()`. These are capability limits, not actual versions.
- Assignment context says "mobile-heavy," but StatCounter shows 41–44% mobile for Indonesia. Its figures are affected by which sites carry its tracker, so the project's own analytics should decide, particularly for mobile e-commerce traffic.
- Measure before finalizing: add a small analytics beacon using `CSS.supports()` for `oklch`, `color-mix`, nesting and container queries. That one step closes the largest unknown here.

### Gaps
- **No public source gives Chrome-for-Android version distribution in Indonesia.** Update lag on mid-tier phones is unknown.
- In-app browsers and WebViews (Shopee, TikTok, Instagram and similar) are not separated in StatCounter. No reliable Indonesian data was found.
- caniuse's UC Browser data rests on a single version entry (15.5), while StatCounter shows 15.0 to 15.3 and 12.10 in the field.
- The floor for Android 5–6 Chrome was not verified.
- I did not test `legacyHex`, `@layer` ordering with generated token files, or whether a given bundler flattens native nesting.
- I did not find a direct source for how much CSS size matters for token blocks on these devices.

## Color: OKLCH vs HSL, gamut, contrast algorithms, and CI

### Takeaway
Use OKLCH for authoring ramps, **WCAG 2.2 contrast as the only pass/fail gate** and APCA at most as advisory. WCAG 3's draft says its contrast algorithm is "yet to be determined," and APCA is not in it. Automate at two levels: token pairs in the token build, and rendered pages with axe in a real browser.

### Cited Findings

**OKLCH vs HSL**
- HSL lightness is inconsistent across hues, while OKLCH's perceptual lightness makes changes more predictable. HSL cannot encode P3, and OKLCH can. — [Evil Martians, 2025-09-17](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)
- Gotchas: not every L/C/H combination can be displayed, and the authors said Chrome and Safari still clipped out-of-gamut colors at the time. They recommend defining an sRGB color and overriding it inside `@media (color-gamut: p3)`. — [Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)
- This article is advocacy for OKLCH, so weigh it accordingly. It also recommends APCA for contrast checks, which conflicts with the conservative position below.
- shadcn/ui's defaults are written in OKLCH. — [shadcn theming](https://ui.shadcn.com/docs/theming)
- DTCG supports `oklch` directly and allows a `hex` fallback. — [Color 2025.10](https://www.designtokens.org/tr/2025.10/color/)

**Contrast standards**
- WCAG 2.2 SC 1.4.3 needs 4.5:1 for text and 3:1 for large-scale text (at least 18pt, or 14pt bold, which is about 24px and 18.5px). Values are not rounded, so 4.499:1 fails. — [W3C Understanding 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- WCAG 3 Working Draft of 10 Sep 2026: "The contrast algorithm used in WCAG 3 is yet to be determined." Text contrast is a "Developing" requirement with the measure left as "to be determined," and the draft says it "still has several years of work." — [WCAG 3.0 WD](https://www.w3.org/TR/wcag-3.0/)
- APCA was removed from the July 2023 WCAG 3 draft. Adrian Roselli estimates WCAG 3 won't finish before 2030. He advises that teams using APCA should also meet WCAG 2, or document the decision. — [Roselli, Apr 2026](https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html)
- APCA's author, commenting on that post, calls APCA "draft guidance we are actively testing and evaluating," says it should not be called "WCAG 3," and says nobody should drop WCAG 2 conformance based on a draft. — [Roselli, comments](https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html)
- Some 2026 blogs still present APCA as WCAG 3's method. Those claims conflict with the W3C draft, which takes precedence. — [WCAG 3.0 WD](https://www.w3.org/TR/wcag-3.0/)
- [`apca-w3`](https://www.npmjs.com/package/apca-w3) is at 0.1.9, with its last npm change in July 2022, although [its repo](https://github.com/Myndex/apca-w3) was pushed in May 2026.

**Ramp tools**
- **Radix Colors**: steps 11 and 12 are guaranteed at Lc 60 and Lc 90 APCA on a step 2 background from the same scale. This is an APCA guarantee, and the page gives no WCAG ratios. Most step 9 colors pair with white text; Sky, Mint, Lime, Yellow and Amber pair with dark text. — [Radix scale docs](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale)
- [`@radix-ui/colors`](https://www.npmjs.com/package/@radix-ui/colors) 3.0.0 was published in Oct 2023, so it is stable but slow-moving.
- **Adobe Leonardo**: generates swatches from target contrast ratios and can export CSS custom properties and W3C-format design tokens (vendor description). — [Leonardo](https://leonardocolor.io/)
- [`@adobe/leonardo-contrast-colors`](https://www.npmjs.com/package/@adobe/leonardo-contrast-colors) is at 1.1.0 (Feb 2026), after a long gap since 1.0.0 (Mar 2024).
- Math libraries: [`colorjs.io`](https://www.npmjs.com/package/colorjs.io) 0.7.1 and [`culori`](https://www.npmjs.com/package/culori) 4.0.2.

**CI**
- Terrazzo's `a11y/min-contrast` takes explicit foreground and background pairs with `largeText` and AA or AAA options, and computes with `contrastWCAG21` from Color.js. — [rule source](https://github.com/terrazzoapp/terrazzo/blob/main/packages/parser/src/lint/plugin-core/rules/a11y-min-contrast.ts)
- First-hand test: the rule failed the build with "expected 4.5, got 3.69 (AA)".
- Tools: [`axe-core`](https://www.npmjs.com/package/axe-core) 4.14.0, [`@axe-core/playwright`](https://www.npmjs.com/package/@axe-core/playwright) 4.14.0, [`@storybook/addon-a11y`](https://www.npmjs.com/package/@storybook/addon-a11y) 10.6.5.
- axe's contrast rule has had trouble with modern color syntax. The 4.11.1 release notes fix contrast failures with oklch/oklab values using `none`. A third-party changelog reports that axe 4.13 still reported "incomplete" on `oklch(100% 0 none)`, so the check never measured. — [axe-core 4.11.1 notes](https://docs.deque.com/axe-release-impact/4.11.1/en/release-notes); [chassis-ui changelog](https://github.com/chassis-ui/css/releases/tag/v0.7.1)
- jsdom lacks the layout APIs axe's contrast check needs, and `jest-axe` disables the rule for that reason. — [DEV post (secondary)](https://dev.to/jangwook_kim_e31e7291ad98/why-color-contrast-disappears-when-you-put-axe-core-in-ci-2ak8)
- `stylelint-gamut` 2.0.1 can flag colors that need P3 wrapping. — [stylelint-gamut on npm](https://www.npmjs.com/package/stylelint-gamut); [Evil Martians](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)

### Inferences
- Ramp recipe, given the look already exists:
  1. Extract the prototype's brand and neutral colors.
  2. Convert them to OKLCH.
  3. Fix an L ladder shared across hues.
  4. Tune chroma per step to stay in sRGB.
  5. Keep the exact brand color as a named step.
  6. Commit the result as plain DTCG values.
  Generators such as Leonardo or Radix's custom tool are good seeds, but the committed token values should be the source of truth, not the generator config.
- Radix fits as a neutral or status palette if it matches the prototype. Do not treat its APCA guarantee as WCAG conformance. Verify with the pair checks below.
- Contrast CI in three layers:
  1. Token level: every `x` and `on-x` pair, for every theme permutation, at 4.5:1 for text and 3:1 for large text.
  2. Non-text UI such as borders and focus rings at 3:1 under WCAG 2.2 SC 1.4.11 ([W3C Understanding 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html), not re-read this session).
  3. Rendered level: axe through Playwright or the Storybook test runner in a real browser, across themes, treating "incomplete" as a failure so an unparsed color cannot pass silently.
- Shipping hex (see the CSS section) also avoids axe's OKLCH parsing edge cases.
- Report APCA as a non-blocking comment if designers want it. Dark-mode readability is where it may add the most value.
- A passing WCAG 2 ratio is a compliance floor, not proof of good legibility, so dark themes and white text on saturated fills still deserve visual review. This is my judgment and is not sourced here.

### Gaps
- I could not confirm whether Terrazzo's contrast rule evaluates every resolver permutation or only the default. I only tested a passing light default and one failing pair. Assume a custom per-permutation script may be needed until this is tested.
- I could not confirm how the rule handles alpha. Pairs with translucent colors should be composited over their real background first.
- The Leonardo page I read does not name the contrast formula it uses.
- The Radix custom palette tool was not read in this session.
- I did not research Indonesian accessibility law or procurement requirements.

## Typography and spacing: fluid vs fixed, scales, density, and migrating from the prototype

### Takeaway
For e-commerce and content, **use fixed rem steps for UI and body text, and fluid `clamp()` only for display and large headings**, keeping max at or below 2.5× min. Use a 4px-based spacing scale. Implement density later as a resolver modifier. Migrate through audit, cluster, snap, codemod, then lint. I found no authoritative source on snapping, so that method below is judgment.

### Cited Findings

**Fluid type**
- `clamp()` with viewport units can fail WCAG 1.4.4 because browsers don't scale `vw` when zooming. The rule: "The maximum value must be less than or equal to 2.5 times the minimum value," using `rem`, and testing at 500% zoom. — [Barvian, Smashing Magazine, 2023](https://www.smashingmagazine.com/2023/11/addressing-accessibility-concerns-fluid-type/)
- A non-fluid value such as `font-size: 2rem` avoids the resize issue entirely. — [Smashing Magazine](https://www.smashingmagazine.com/2023/11/addressing-accessibility-concerns-fluid-type/)
- Utopia's calculator defaults to a 360px to 1240px viewport, 18px to 20px base and ratios 1.2 to 1.25. It outputs `--step-*` custom properties using `clamp()` and can be viewport- or container-relative. — [Utopia calculator](https://utopia.fyi/type/calculator/)
- A German secondary source says Utopia now warns when a step breaks WCAG 1.4.4 at 200% zoom, but the calculator page I read does not mention WCAG. Treat this as unconfirmed. — [drweb.de](https://www.drweb.de/utopia-fluide-typografie-clamp/)
- DTCG dimensions allow only `px` or `rem` with a numeric value, so a `clamp()` expression is not a valid standard dimension. — [Format 2025.10 §8.2](https://www.designtokens.org/tr/2025.10/format/)
- Tailwind's `--text-*` namespace supports paired properties such as `--text-tiny--line-height`, and its `text-*` utilities consume only line-height, letter-spacing and font-weight sub-values. — [Terrazzo Tailwind docs](https://terrazzo.app/docs/integrations/tailwind/)

**Spacing and density**
- Tailwind can use a single multiplier (`--spacing`), and the docs' examples show `--spacing: 4px`. — [Tailwind theme docs](https://tailwindcss.com/docs/theme)
- Spectrum uses `sets` with `desktop` and `mobile` values on a token, for example `base-padding-horizontal-2x-large` has `desktop: 20px`. — [Spectrum layout.json](https://github.com/adobe/spectrum-design-data/blob/main/packages/tokens/src/layout.json)
- WordPress handles pixel density and corner radius as inline overrides in its resolver. — [Gutenberg tokens guide](https://github.com/WordPress/gutenberg/blob/trunk/packages/theme/tokens/README.md)
- Terrazzo advises orthogonal resolvers: no two modifiers should affect the same tokens, and it suggests one modifier per token `$type`. — [Terrazzo resolvers guide](https://terrazzo.app/docs/guides/resolvers/)

**Auditing and enforcement**
- Project Wallace's CSS Design Tokens Analyzer extracts potential tokens from a URL, files or pasted CSS, covering colors, font sizes, families, line heights, shadows, radii, durations and more. The output format was not stated. — [Project Wallace](https://www.projectwallace.com/design-tokens)
- [`@projectwallace/css-analyzer`](https://www.npmjs.com/package/@projectwallace/css-analyzer) 9.9.5 was published in Oct 2026.
- Terrazzo has `duplicate-values`, `consistent-naming`, `required-typography-properties` and `a11y-min-font-size` rules. — [Terrazzo lint rules](https://github.com/terrazzoapp/terrazzo/tree/main/packages/parser/src/lint/plugin-core/rules)
- Large systems ship lint tooling:
  - [`@atlaskit/eslint-plugin-design-system`](https://www.npmjs.com/package/@atlaskit/eslint-plugin-design-system) 16.15.0
  - [`@primer/stylelint-config`](https://www.npmjs.com/package/@primer/stylelint-config) 13.6.0
  - [`@shopify/stylelint-polaris`](https://www.npmjs.com/package/@shopify/stylelint-polaris) 16.0.7
  - [`stylelint-plugin-carbon-tokens`](https://www.npmjs.com/package/stylelint-plugin-carbon-tokens) 5.0.6
  - [`@salesforce-ux/slds-linter`](https://www.npmjs.com/package/@salesforce-ux/slds-linter) 1.2.1
- Generic options:
  - [`stylelint-declaration-strict-value`](https://www.npmjs.com/package/stylelint-declaration-strict-value) 1.12.1 for hand-written CSS.
  - [`eslint-plugin-better-tailwindcss`](https://github.com/schoero/eslint-plugin-better-tailwindcss) 4.10.0, with `no-unknown-classes`, `no-restricted-classes` and `enforce-canonical-classes` for Tailwind v3 and v4. Its page has no rule that specifically targets arbitrary values.
- Tailwind's canonicalization now converts some arbitrary values to named equivalents, such as `max-[64rem]:flex` to `max-lg:flex`. — [Tailwind changelog 4.3.4](https://github.com/tailwindlabs/tailwindcss/blob/main/CHANGELOG.md)

**Deprecation**
- DTCG `$deprecated` takes `true` or an explanation string. — [Format 2025.10](https://www.designtokens.org/tr/2025.10/format/)
- Primer keeps a `removed.json` file listing removed tokens with `null` values. — [Primer removed.json](https://github.com/primer/primitives/blob/main/src/tokens/removed.json)
- In my test, neither tool warned at build time when a deprecated token was referenced, so CI has to enforce this itself.

**Migration evidence is weak**
- A self-reported portfolio describes 1,247 hardcoded hex values reduced to 34 using jscodeshift. The numbers are unverified. — [Dusk case study](https://portfolio-f1q1epwju-ben-eunsoo-hos-projects.vercel.app/work/token-migration-dusk)
- A TokenLens article describes a useful coverage-audit method, but it is promotion by the tool's author. — [DEV post (vendor promo)](https://dev.to/zetareticoli/why-your-design-tokens-and-your-css-are-probably-out-of-sync-and-how-to-check-3od6)

### Inferences
- **Type recommendation:**
  - Fixed steps for product UI, because prices, labels and dense cards need predictable wrapping and density at 360px.
  - Fluid only for display and hero sizes on content pages, with min set at 360px and max at 1440px (change Utopia's default 1240).
  - At the 360-to-1440 range, the 2.5× limit is easy to meet.
- **Representing fluid values in DTCG:** store `min` and `max` as standard dimension tokens, plus a `$extensions` key with viewport bounds, and generate `clamp()` in a custom transform. Do not place `clamp()` strings in `$value`, as that would break the spec's dimension rule.
- **Spacing recommendation:** a 4px base with a limited named set (4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80), expressed in rem. Allow 2px only as a named exception for optical adjustments. Keep layout breakpoints and container sizes as separate tokens.
- **Density:** do not build it now. Reserve it by using semantic spacing names for control padding and height, so a `density` modifier can be added later without renaming. Keep it orthogonal to `theme`. Do not use a density mode to address 360 vs 1440, which is a responsive concern.
- **Migration method (judgment):**
  1. **Audit:** extract every value from the prototype with usage counts, by property.
  2. **Cluster:** group near-duplicates (for example within 1–2px for spacing, or ΔE OK under about 0.02 for color). These thresholds are starting points, not sourced standards.
  3. **Decide the scale from high-frequency values**, not from the extremes.
  4. **Snap:** produce a reviewed mapping table (`old value → token`, count, delta). Flag any snap over a threshold for a human decision, and require contrast rechecks on every color snap.
  5. **Codemod** using that table, reviewed screen by screen with visual diffs.
  6. **Lock:** turn on strict lint and remove Tailwind defaults with `--*: initial`. Use a ratchet (no new violations) until the count reaches zero.
  7. **Deprecate:** mark old names with `$deprecated`, keep aliases for one minor release, then list them in a `removed` file, with CI failing on use of removed names.
- Because the source is a prototype and no production code exists on these tokens yet, the deprecation stage can be light at the start. Most of the effort goes into auditing and snapping.

### Gaps
- I found no authoritative source on snapping algorithms or thresholds, and no strong, independently verified migration case study. The search returned mainly vendor posts, AI-skill listings and a portfolio.
- I did not find a direct comparison of Utopia-style fluid scales with fixed steps in e-commerce, or a comparison of sales or usability outcomes.
- I did not verify how to extract values from the prototype canvas, since its format was not part of this assignment.

## Non-web and multi-brand extensions

### Takeaway
Keep DTCG as the source. Add a `brand` modifier in the resolver if multi-brand arrives. For native, use Style Dictionary's predefined formats or Terrazzo's Swift plugin. For email, generate static resolved values, since CSS variables are unreliable there.

### Cited Findings
- The resolver's sets and modifiers apply to any dimension, not just theme. — [Resolver 2025.10](https://www.designtokens.org/tr/2025.10/resolver/)
- Terrazzo builds a permutation for each input you list and recommends orthogonal modifiers. — [Terrazzo resolvers guide](https://terrazzo.app/docs/guides/resolvers/)
- Terrazzo has `plugin-swift` but no Android or Compose package. — [Terrazzo packages](https://github.com/terrazzoapp/terrazzo/tree/main/packages)
- Style Dictionary has predefined formats for iOS Swift, Android resources, Compose and Flutter. React Native is not listed on that page. — [SD predefined formats](https://styledictionary.com/reference/hooks/formats/predefined/)
- Email: CSS variables have an estimated 45.24% support. Gmail supports `var()` but "not the variable declaration," and the data was last tested on 25 Feb 2020, so it may be outdated. — [Can I Email: CSS variables](https://www.caniemail.com/features/css-variables/)
- DTCG color's optional `hex` field gives email and legacy targets a simple value. — [Color 2025.10](https://www.designtokens.org/tr/2025.10/color/)

### Inferences
- Path for native: use `tz bundle` or a small script to resolve each permutation to flat DTCG JSON, then feed that to Style Dictionary for Android and Compose. This was not tested. The portable subset is what makes it practical.
- Email: a separate build target that emits literal hex and px values into a small JSON or template partial, using a reduced semantic set.
- Do not build these now. Staying with DTCG plus the portable subset is what preserves the option at low cost.
- Number of permutations grows multiplicatively (theme × brand × density), so ship only the combinations actually used.

### Gaps
- I did not test a Terrazzo to Style Dictionary handoff or real native output.
- caniemail's data on this feature is more than five years old. Test real clients, including those common in Indonesia, before relying on it.

## Designers without Figma: viewing, editing, and approving tokens

### Takeaway
The workable model is tokens as code plus generated visual review: PRs edit DTCG JSON, CI posts a semantic token diff and a preview deployment, and designers approve in a Storybook-based token gallery. Visual editors are helpers for exploration rather than sources of truth. No mature, DTCG-native, Git-backed visual editor turned up in this research.

### Cited Findings

**Diff and docs**
- Adobe publishes [`@adobe/token-diff-generator`](https://www.npmjs.com/package/@adobe/token-diff-generator) 2.5.8 (Oct 2026), and its monorepo contains a `diff-generator` tool and token visualizers. It is built for Spectrum's format, so it will not necessarily work directly on DTCG. — [spectrum-design-data](https://github.com/adobe/spectrum-design-data)
- WordPress generates a Design Tokens Reference (`docs/tokens.md`) for consumers. — [@wordpress/theme README](https://github.com/WordPress/gutenberg/blob/trunk/packages/theme/README.md)
- `plugin-token-listing` produces a listing that maps source tokens to their build output, for tool makers. — [plugin-token-listing README](https://github.com/terrazzoapp/terrazzo/tree/main/packages/plugin-token-listing)

**Storybook**
- [`storybook`](https://www.npmjs.com/package/storybook) is at 10.6.5.
- [`storybook-design-token`](https://www.npmjs.com/package/storybook-design-token) is at 5.0.0, last published Dec 2025, with a peer dependency on Storybook `^10.0.0` and 414,478 monthly downloads.
- Terrazzo's `@terrazzo/storybook` is a private package in its repo, not a published addon. — [package.json](https://github.com/terrazzoapp/terrazzo/blob/main/packages/storybook/package.json)

**Visual editors**
- tweakcn: a visual theme editor for Tailwind and shadcn/ui. Apache-2.0, 10,504 stars, 56 open issues, last pushed 2026-09-03. — [tweakcn repo](https://github.com/jnsahaj/tweakcn)
- Terrazzo Token Lab ("Create, edit, and save tokens.json in DTCG format") is **private, version 0.0.0**, in the repo. The npm name holds only a 2024 placeholder, so it is not a tool you can adopt today. — [token-lab package.json](https://github.com/terrazzoapp/terrazzo/blob/main/packages/token-lab/package.json)
- Leonardo offers visual ramp generation and token export (vendor description). — [Leonardo](https://leonardocolor.io/)

**Penpot**
- Penpot says it follows the W3C DTCG approach. A user report from 4 May 2026 says its export is in Tokens Studio multi-set format instead: `$themes` and `$metadata` wrappers, hex strings rather than color objects, and unit strings rather than dimension objects. The reply did not commit to a change. — [Penpot design tokens](https://penpot.app/collaboration/design-tokens); [Penpot community thread](https://community.penpot.app/t/token-export-is-tokens-studio-format-not-dtcg-2025-10/10544)
- A third-party plugin imports DTCG files into Penpot as native token sets, last updated 24 Jul 2026. — [Penpot plugin listing](https://penpot.app/penpothub/plugins/dtcg-toke-import)

### Inferences
- Recommended flow:
  1. A designer or engineer opens a PR changing `*.tokens.json`. GitHub's web editor is enough for small value changes.
  2. CI runs validation, lint and contrast checks.
  3. CI comments a semantic diff by resolved value: token, old value, new value, swatch, changed contrast pairs, and affected tokens downstream of an alias. A plain text diff misses downstream changes when a primitive moves.
  4. CI deploys a preview with a token gallery plus real screens at 360px and 1440px, in each theme.
  5. CODEOWNERS requires design approval.
  6. Changesets versions the release.
- A custom diff script is likely the right size. Compare the `dist/tokens.json` output between base and head for each permutation. This takes modest effort and avoids depending on Spectrum's format.
- A generated gallery from the same token output, rather than an addon parsing CSS comments, keeps docs and tokens from drifting. `storybook-design-token` is a reasonable shortcut for a first version.
- Use tweakcn for quick exploration only if the semantic names stay shadcn-compatible. Copy values back into DTCG by hand or with a script, and do not let it become a second source of truth.
- Don't adopt Penpot just for tokens. Its value here would be as a design canvas. If it is adopted, treat it as an importer from DTCG, and do not treat its export as DTCG.
- Designer access is a workflow risk: if designers are not comfortable with PRs, a small local or preview-hosted form that writes JSON and opens a PR would be a low-cost addition. This is a suggestion and I did not find an established product doing this well.

### Gaps
- I found no actively maintained, published, DTCG 2025.10-native, Git-backed visual token editor. My search was not exhaustive.
- I could not read tweakcn's feature list. Its site returned only a title, so I cannot confirm contrast checks or import and export formats.
- I did not verify current Penpot docs beyond the May 2026 thread and could not confirm whether its export has changed since.
- I found no published evidence on how well PR-based token approval works for designers on teams without Figma.

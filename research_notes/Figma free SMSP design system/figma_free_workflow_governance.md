# Working Without Figma: Workflow, AI-Native Tooling, Governance and Migration Risks of a Code-First Design System (as of 3 November 2026)

All sources accessed 2026-11-03. Evidence labels used throughout:

- **[P]** primary documentation or filing
- **[T]** first-hand team or practitioner account
- **[S]** survey (the survey publisher is usually a vendor)
- **[V]** vendor or competitor marketing
- **[2]** secondary or aggregator summary
- **[U]** not independently verified

Method notes for the report writer:

- The two Claude artifact type definitions (Design, Design System) and their reference files were read verbatim through the Artifact tool.
- Most other pages came through a fetch tool that returns model summaries. Recheck short quotes against the original before publishing them.
- Several search-only items are marked [2] or [U] because the page itself was not opened.
- Token formats and component library choice are out of scope. They appear only where they constrain the pipeline.

**Overall evidence quality:**

- There are a handful of real team accounts, nearly all under 12 months old and nearly all without outcome metrics.
- I found no longitudinal study and no controlled study of a Figma-free design system.
- I also found no first-hand account of a team that left Figma, regretted it and went back. That absence probably reflects publication bias and the short time elapsed. It is not evidence of success.

## Case studies: which teams have publicly moved off Figma or gone design-in-code/AI-first, and what happened?

### Takeaway
Public accounts describe Figma's role narrowing far more often than Figma being removed. The strongest cases share preconditions the SMSP team should test itself against: a code-based design system, design-engineer capacity, and a B2B or internal product with light visual-exploration needs. Reported wins are speed, working-software review and fewer source-of-truth arguments. Reported pain is preview environments, stale context, token limits, and designers who cannot debug.

### Cited Findings

**Closest to a full move**

- **Cisco DevNet, PubHub internal tool (2 Nov 2026) [T].** A coding agent built a working UI from user stories and APIs first. Designers then refined a single HTML prototype with AI coding tools and shipped it with an embedded design system, a persona switcher and a changelog per iteration. Engineers gave a coding agent the changelog and HTML to apply changes across the project.
  - Reported: new HTML iterations daily, versus "a single page took days" under Figma-first.
  - The Figma round trip lost interactions, flows and animations, and left it unclear which artifact was current.
  - When the designer hit token limits they moved from Cursor to Claude to Codex, and the HTML file preserved state.
  - Limits they state: the AI did not know the design language or which interactions felt right.
  - No formal governance is described. No quantified outcome beyond the iteration speed. Internal tool. — [Cisco](https://blogs.cisco.com/cisco-devnet/design-to-code-ai-handoff-workflow)
- **Changying Zheng, 40-person org of UX, design engineers and engineering (15 Feb 2026) [T, paywalled; free portion only].** A four-month transition: vibe-coding training to reduce fear, production dev-environment onboarding, internal tools, then papercut fixes.
  - The design system now lives only in code: "Code is the source of truth because it's the originator." Designers clone the DS repo, vibe-code with DS components and push merge requests; engineering reviews, refines and ships.
  - Resistance: the original proposal was "too drastic for many", and managers argued designers still need Figma skills.
  - Most prototypes do not go to production; engineers refactor them.
  - Stated failure conditions: heavy visual exploration, no code-based DS, no AI infrastructure, or a resistant culture.
  - Figma is still used, but no longer as source of truth or handoff vehicle. No metrics in the visible portion. — [Ops Forward](https://changying.substack.com/p/case-study-from-figma-first-to-code)
- **Hikari, solo contract product designer on a SaaS (29 Oct 2026) [T].** Already had shadcn, Storybook, a token repo and Claude Code in the app repo.
  - Each issue gets a `design/<issue>-<screen>` branch that is **never merged**. Engineers run it locally as the spec.
  - Worked: dynamic mocks removed the need to build states in Figma; reviewers evaluate interactive mocks more easily.
  - Friction: specs outside the repo don't fit; non-engineering reviewers need a preview environment that engineers must set up, which becomes a bottleneck; small tweaks are faster by hand than by prompt.
  - Figma use fell but remains for banners and early ideas. — [note.com](https://note.com/hgffdgn654/n/n92467b83a1c1?hl=en)
- **Two Medium accounts seen only in search snippets (pages returned 403) [U].**
  - A design innovation lead on a 20-person AI-native team "barely opens Figma", and the DS lives in a single markdown file — [Bootcamp](https://medium.com/design-bootcamp/i-do-design-innovation-i-barely-open-figma-anymore-0a46003fbe8b).
  - A designer publishing prototypes to a GitHub repo for review — [Bootcamp](https://medium.com/design-bootcamp/the-designer-who-made-the-developer-redundant-the-developer-who-made-the-designer-redundant-4fe86b185259).
  - Another September 2026 post asks whether anyone has done this, and is itself unanswered — [Medium](https://medium.com/@veigasvishal2000/has-anyone-ditched-figma-and-moved-to-an-ai-generated-code-first-design-system-7c1715c747f3).

**AI-first but keeping Figma**

- **BILL, Trinity design system (17 Aug 2026) [T].** See the AI-native section for numbers. Storybook stays the single source of truth; the agent CLI, MCP server and skills are generated from it. — [BILL Engineering](https://www.bill.com/engineering/how-we-made-our-design-system-bilingual)
- **Indeed [2].** 4,300 AI prototypes in 4 months using real React DS components across a 77-component pipeline, reported by a design-systems training site. — [Into Design Systems](https://www.intodesignsystems.com/design-systems-mcp)
- **Intercom [2/U].** Podcast listing says engineers, designers, PMs and TPMs all ship code through Claude Code, with R&D throughput doubled in nine months — [How I AI listing](https://metacast.app/podcast/how-i-ai/amGU0EZw/how-intercom-2x-d-their-engineering-velocity-in-9-months-with-claude-code-brian-scanlan/tKF8XiSo). A secondary talk summary says their designers prototype in code using Figma Code Connect, so Figma is still in the loop — [summary](https://thehuman2ai.pages.dev/design/videos/sneak-peek-intercom-figma-mcp-claude). I did not find an Intercom-authored post.
- **Jenny Wen, head of design at Claude and ex-Figma (Mar 2026) [T, with an obvious interest].** Mocking and prototyping went from "60 to 70%" of the work to "30 to 40%", per a transcript-quoting summary — [Antoine Buteau](https://www.antoinebuteau.com/lessons-from-jenny-wen/). A third-party summary says Figma is now for exploring and communicating intent, not the final spec — [RAR Design](https://rar.design/posts/design-process-is-dead-jenny-wen.md). The episode has a chapter titled "Why Figma still matters" — [Lenny's](https://www.lennysnewsletter.com/p/the-design-process-is-dead).

**Counter-evidence and critics**

- **ServiceNow Innovation Office, 3 people (Oct 2025) [T; dated].** Went straight to code with Windsurf and got a polished result, but "Every step required careful curation by someone experienced with writing code", and "graphic designers will not—there's still too much coding involved." LLMs lost working code during small edits. — [ServiceNow](https://www.servicenow.com/community/innovation-office-blog/idea-to-code-in-an-ai-world-do-we-need-figma/ba-p/3394865)
- **Roger Wong (9 Mar 2026) [T/opinion].** "Leaving" is the wrong word: designers are adding tools and Figma's role is narrowing. He argues designers become directors orchestrating agents against a design system rather than coders. The same post's source (Chawla) concedes Figma "is still the best tool for a majority of creatives". — [Roger Wong](https://rogerwong.me/2026/03/figma-role-narrows-not-dies)
- **Market data [P].** Figma's Q2 2026 revenue was $370.1M, up 48% YoY, with net dollar retention of 136%. Q3 guidance implies about 36% growth. This is not what mass exit looks like, though it does not speak to small teams. Q3 actuals were not found. — [SEC 8-K](https://www.sec.gov/Archives/edgar/data/0001579878/000162828026053331/q226pressrelease.htm)
- **zeroheight State of AI in Design Systems 2026 [S, n=123, skews in-house leads at mid-to-large tech firms].** Design generation has the worst satisfaction, net −53. 67% say AI is somewhat or very overhyped. 63% are most satisfied with AI for documentation. 56% use Figma Make, so these teams are not leaving. — [zeroheight](https://zeroheight.com/resources/state-of-ai-in-design-systems/)
- **Hands-on Claude Design criticism, early and possibly stale (Apr–May 2026).**
  - Builder.io (a competitor) estimates DS fidelity at "maybe 50%-75%", and reports no real components, no Figma export, and no persistence with a changing app — [Builder.io](https://www.builder.io/blog/claude-design) [V].
  - A Substack summary of Reddit reports a post titled "practically unusable", aggressive usage limits, and drift by revision 4–5 — [Boringbot](https://boringbot.substack.com/p/claude-design-what-it-is-how-it-works) [2].
  - The positive launch quotes from Brilliant and Datadog are vendor-selected — [Anthropic](https://www.anthropic.com/news/claude-design-anthropic-labs) [V].

### Inferences
- The best-evidenced pattern is not "no Figma" but "no parallel design library". What these teams removed is the duplicate source of truth. SMSP is going further than most public cases, so it should expect to find out some costs first-hand.
- All strong cases had code before the switch (Hikari: Storybook plus tokens; Zheng: a DS repo; BILL: Storybook). SMSP's stated position is canvas-first with code to follow, which has less precedent. Cisco is the nearest match, and it is one internal tool with no described governance.
- Most Claude Design criticism dates from April–May 2026, before the September merge into conversations. Treat it as a checklist to retest, not as current fact.

### Gaps
- No public 12-month-plus outcome data, no team that returned to Figma, and no small Southeast Asian or Indonesian team case found.
- Designer attrition and satisfaction after these moves are unreported.
- Zheng's paywalled section may contain metrics.

## Replacement tools by function: what's current, and which are code-native vs canvas?

### Takeaway
The market has split into three groups: HTML-rendering canvases (Claude Design, Paper), agents and visual editors on a real repo (Claude Code, Cursor Design Mode, Onlook, Subframe, Builder.io), and app generators (v0, Lovable, Bolt, Stitch, Tempo). Most comparison content is written by competitors, so status details below should be rechecked before purchase. Nothing here fully replaces Figma's combination of free-form manipulation, reliable multiplayer and comment history.

### Cited Findings

| Tool | Nature | Exploration / layout | Handoff | Comments / collaboration | State and evidence quality |
|---|---|---|---|---|---|
| **Claude Design** | HTML canvas: `.dc.html` artboards rendered live, plus chat | Direct drag, resize, align; properties panel; inline comments; prompts | Handoff to local agent or Claude Code Web; `/design` imports to codebase, exports code as a live prototype, or builds the project | View, comment or edit roles. **"Multi-person simultaneous editing is basic and may be unreliable"** (fetch summary wording; recheck) | Launched as research preview 17 Apr 2026; in any conversation since 16 Sep; standalone closes 14 Dec. — [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design), [Release notes](https://support.claude.com/en/articles/12138966-release-notes) [P] |
| **Claude Code + artifacts** | Code-native agent; publishes pages | `/design` drafts canvases (requires v2.1.265+); side-by-side layout options | Native to the repo | Org-only comments; Claude can read and answer them (v2.1.221+) | Templates labelled beta. — [Docs](https://code.claude.com/docs/en/artifacts) [P] |
| **Cursor Design Mode** | Code-native; no canvas; needs the running app | Annotate or select UI elements in the browser for the agent | Same repo | None documented | In Cursor 3.0, 2 Apr 2026 — [Changelog](https://cursor.com/changelog/3-0) [P]. Predecessor Visual Editor shipped in 2.2, Dec 2025; bugs reported during the transition — [secondary](https://pasqualepillitteri.it/en/news/3794/cursor-design-mode-what-it-is-how-it-works-cursor-3) [2] |
| **v0** | Generator on shadcn/Tailwind | Design Mode controls | GitHub branches and PRs (sources disagree on one-way vs two-way sync) | Not verified | — [Comparison](https://www.nxcode.io/resources/news/vibe-design-tools-compared-stitch-v0-lovable-2026), [another](https://emergent.sh/learn/v0-vs-lovable-vs-bolt) [2/V] |
| **Lovable** | App generator | Prompts, visual edits | GitHub sync; a competitor says you can't start from an existing repo and only the default branch syncs back | Not verified | — [Builder.io](https://site-qwik.vercel.app/blog/lovable-alternatives) [V] |
| **Bolt** | App generator | Design Mode for visual edits | GitHub sync per comparisons | Not verified | — [Comparison](https://www.nxcode.io/resources/news/vibe-design-tools-compared-stitch-v0-lovable-2026) [2] |
| **Google Stitch** | AI canvas plus generator | Screen generation; DESIGN.md | HTML/Tailwind or React export (sources conflict) | Not verified | Reviews say major update Mar 2026; about 350 standard and 50 experimental generations a month; paid plans speculated, not announced — [Review](https://muratesmer.pages.dev/blog/google-stitch-review-2026), [Pricing guide](https://www.nxcode.io/resources/news/google-stitch-pricing-plans-complete-guide-2026) [2/U]. Official docs page returned no body. |
| **Subframe** | Canvas plus agent, outputs React/Tailwind | Visual canvas | Reads and writes local files | Not verified | From $20/editor/month; best for React. — [Modeinspect](https://modeinspect.com/blog/figma-alternatives-for-product-teams), [Subframe](https://www.subframe.com/tips/subframe-vs-pencil) [V] |
| **Paper** | Canvas on real HTML/CSS; agent via MCP | Canvas, MCP | Agent writes code | Real-time multiplayer per its own page | One roundup calls it alpha; MCP was desktop-only in March. — [Paper](https://paper.design/compare/pencil) [V], [O'Connell](https://brendan-oconnell.com/paper-vs-pencil-agentic-design-tools-with-mcp-to-iterate-designs-figma-alternatives/) [T] |
| **Pencil (now pen.dev)** | `.pen` JSON in repo; agents via MCP | Canvas | Sync is manual: design and code align only when you ask the agent | Local and single-user according to Paper (a competitor); "less natural" for stakeholder review per UXMagic (also competing) | About $16/user. — [UXMagic](https://uxmagic.ai/blog/pencil-dev-review) [V] |
| **Penpot** | Traditional open-source canvas (MPL-2.0), self-hostable | Vector canvas | MCP server plus token access; 2.14 details are secondary | Multiplayer canvas | Official MCP moved into main repo in Feb 2026. — [Penpot](https://penpot.app/ai/mcp-server) [P], [dev.to](https://dev.to/creeta/penpots-mcp-server-runs-on-five-tools-figmas-uses-dozens-354e) [2] |
| **Onlook** | Visual editor on a running React app; Apache 2.0; Next.js and Tailwind focus | Direct manipulation | Writes to code | Not verified | 22k+ stars as of Mar 2026; current activity not verified. — [GitHub](https://github.com/onlook-dev/onlook), [comparison](https://aicoolies.com/comparisons/onlook-vs-lovable-vs-tempo-labs) [2] |
| **Tempo** | Moved from visual React editor to prompt-to-app | Not verified | Not verified | Not verified | Status as of Mar 2026 only. — [comparison](https://aicoolies.com/comparisons/onlook-vs-lovable-vs-tempo-labs) [2/U] |
| **Builder.io** | Visual and agent editing on existing repos | Claims "safely changing what already exists" | Repo-based | Not verified | Only its own blog seen; no Fusion primary docs read. — [Builder.io](https://www.builder.io/blog/claude-design) [V] |
| **Webflow / Framer** | Hosted site builders | AI code components, Wireframer, Workshop | Webflow HTML/CSS export; Framer no code export per a competitor | Not verified | Marketing-site tools, not product DS tools. — [Flow Ninja](https://www.flowninja.com/blog/framer-alternatives) [V] |
| **Figma itself (for comparison)** | Canvas adding code | Code layers announced 24 Jun 2026, rollout "starting in July" | Two-way frame and code layer updates claimed | Comments in the same file | Later beta status conflicts between sources. — [Figma](https://www.figma.com/blog/config-2026-recap/) [P/V], [Startup Fortune](https://startupfortune.com/figma-turns-its-design-canvas-into-a-coding-environment-at-config-2026/) [2] |

- O'Connell's hands-on test of Paper and Pencil calls them accelerators for early-stage work: "These tools are not meant to replace a designer." — [O'Connell](https://brendan-oconnell.com/paper-vs-pencil-agentic-design-tools-with-mcp-to-iterate-designs-figma-alternatives/) [T]
- Most surveyed teams use 2–4 AI tools; 74% use Claude. — [zeroheight](https://zeroheight.com/resources/state-of-ai-in-design-systems/) [S]

### Inferences
- For SMSP the core stack is already implied: Claude Design for exploration and review, Claude Code for production. Add a preview host and Storybook.
- Additional canvases add a second format to keep in sync. Consider Penpot only as a contingency for non-coders or exit insurance, and Cursor Design Mode or Onlook only if designers want direct manipulation on the running app.
- Portable HTML is the real hedge. Cisco's tool switching worked because the artifact was plain HTML. Note that `.dc.html` has a proprietary runtime layer (next sections), so test how portable it actually is.

### Gaps
- No independent, current comparison of these tools exists. Nearly all comparisons are written by competitors.
- Comment and multiplayer features for v0, Lovable, Bolt, Stitch and Subframe were not verified.
- Builder.io Fusion, Tempo and Onlook status as of November could not be confirmed from primary sources.

## Figma functions needing an explicit replacement, and who can edit what

### Takeaway
Each function has a workable substitute, but the substitutes are spread across several tools, and the seams are where the costs fall. The real losses are reliable multiplayer on one surface, a single browsable visual library that non-coders own, durable comment and version history on the canvas, and frictionless input from people outside the organization.

### Cited Findings

| Figma function | Replacement options | Evidence | What is genuinely lost |
|---|---|---|---|
| Component library browsing | Storybook (humans and agents); Design System artifact page with live previews | BILL keeps Storybook as "the single source of truth" and stories import real components so breaking changes fail the build — [BILL](https://www.bill.com/engineering/how-we-made-our-design-system-bilingual) [T]. The DS artifact offers README, tokens, previews, assets — [DS type](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd) [P] | Drag-and-drop instances from an asset panel. Mounting real components on a canvas needs a bundle and is agent-driven (`x-import`) — [Design type refs](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd) [P] |
| Multiplayer critique | Canvas co-presence plus scheduled live review | Anthropic warns simultaneous editing is basic and may be unreliable — [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) [P]. Cisco reviews often and sometimes live — [Cisco](https://blogs.cisco.com/cisco-devnet/design-to-code-ai-handoff-workflow) [T] | Reliable co-editing. This is the clearest functional loss |
| Comments | Canvas comments; artifact comments readable by Claude; Vercel comments; Netlify Drawer; PR threads | Inline comments can fail to appear (still in comments view), and Anthropic says paste feedback into chat if needed — [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) [P]. Vercel comments are on all plans, on by default, and need a Vercel account; external collaborators require Pro or Enterprise — [Vercel](https://vercel.com/docs/comments) [P]. Netlify's drawer offers annotated screenshots and recordings, syncing to the PR — [Netlify](https://www.netlify.com/platform/core/deploy-previews.md) [V/P] | Durability. **Comments do not move or export from standalone** and are deleted some time after closure — [Move guide](https://support.claude.com/en/articles/17440474-move-from-standalone-claude-design-to-claude) [P]. Decisions must be copied out |
| Version history | Git for code; artifact versions; ask Claude to save a copy | **Conflict:** "Claude Design doesn't have version history yet" — [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) vs "Each publish becomes a version", and you can choose which version viewers see — [Claude Code docs](https://code.claude.com/docs/en/artifacts) [both P] | Named, browsable, restorable design history until tested otherwise |
| Developer handoff | PR with live preview; changelog plus HTML; `/design` handoff | Cisco's changelog made updates incremental rather than page diffs — [Cisco](https://blogs.cisco.com/cisco-devnet/design-to-code-ai-handoff-workflow) [T]. Users reported handoff URLs returning 404 and a phantom connector (June 2026; may be fixed), with zip export as workaround — [Issue #60327](https://github.com/anthropics/claude-code/issues/60327) [T, closed not planned] | Pixel inspection, though real code largely removes the need |
| Prototyping | Interactive artboards (`is_interactive`), code prototypes | Hikari, Cisco and Zheng all report this as a net gain — [note](https://note.com/hgffdgn654/n/n92467b83a1c1?hl=en), [Cisco](https://blogs.cisco.com/cisco-devnet/design-to-code-ai-handoff-workflow), [Zheng](https://changying.substack.com/p/case-study-from-figma-first-to-code) [T] | Little; arguably a gain |
| Asset export | Per-artboard PNG/PDF; zip, PPTX, Google Slides, HTML; assets kept in the DS | [Claude Code docs](https://code.claude.com/docs/en/artifacts), [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design) [P]. Canva and PPTX quality criticised early — [third-party search result](https://pietromontaldo.substack.com/p/claude-design-full-tutorial) [2/U]. Video not exportable per a third-party guide [U] | Slice-level multi-scale export (my inference, no source) |
| Stakeholder review | Preview URLs per PR; shared artifact link | Non-engineers need previews that engineers must set up — [note](https://note.com/hgffdgn654/n/n92467b83a1c1?hl=en) [T]. Public-link viewers cannot see or add comments, and org sharing and editor roles need Team or Enterprise — [Claude Code docs](https://code.claude.com/docs/en/artifacts) [P]. Cloudflare previews are public by default, can be gated by Access, and I found no built-in comments — [Cloudflare](https://developers.cloudflare.com/pages/configuration/preview-deployments/index.md) [P] | Simple "anyone with the link can comment" for outside parties (clients, agencies) |
| Visual review of change | Chromatic; Playwright snapshots; Argos; screenshots in PRs | Chromatic lists visual tests, TurboSnap and UI Review; entry price reported as $179/month but aggregators conflict — [Chromatic](https://chromatic.com/pricing), [PricingSaaS](https://pricingsaas.com/companies/chromatic). Argos is a competitor — [Argos](https://argos-ci.com/blog/storybook-visual-testing-without-chromatic) [V]. `gh --attach` lets agents add before/after media to PRs (1 Sep 2026) — [GitHub](https://github.blog/changelog/2026-09-01-github-cli-media-in-issues-pull-requests-and-comments/) [P], which Frost called "a genuine game changer" for AI and DS work — [Frost](https://bradfrost.com/notes/post/2026-09-02-1308/) [T] | None; this improves on Figma for regressions |
| Non-coder contribution | Canvas edits and comments; DS page edits; agent-assisted PRs | Designers push MRs and engineers review — [Zheng](https://changying.substack.com/p/case-study-from-figma-first-to-code) [T]. Prompting "is still a programming language" — [ServiceNow](https://www.servicenow.com/community/innovation-office-blog/idea-to-code-in-an-ai-world-do-we-need-figma/ba-p/3394865) [T]. **A `/design-sync` system is read-only for everyone on its page; changes must be made in code** — [DS type refs](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd) [P] | Direct library ownership by designers who don't use Git |

**Leaving Figma**

- `.fig`, `.jam` and `.deck` are proprietary and open only in Figma. Figma suggests saving copies in case you return, and exporting to other formats to move content. The page doesn't mention comments or version history. — [Figma Help](https://help.figma.com/hc/en-us/articles/360039826814-Delete-your-Figma-account) [P]
- Community forum answers (not policy): nothing is deleted on cancellation, but over-limit teams on Starter can lock to view-only; copying or exporting from a locked team may be blocked for some users, so export first. — [Figma Forum](https://forum.figma.com/t/if-i-stop-paying-for-the-professional-plan-would-i-lose-all-my-files-or-they-are-just-going-to-be-locked/70961) [2/U]

### Inferences
Proposed permissions model, synthesized from the above:

| Role | Canvas | DS artifact | Repo | Approves |
|---|---|---|---|---|
| Non-coding stakeholder | View, comment | View | None | Sign-off on preview or canvas (record in PR or decision log) |
| Designer (no Git yet) | Edit | Propose via comment; can edit only if not `/design-sync` mode | Via an agent-opened PR, reviewed by an engineer | Visual and content quality |
| Designer-engineer / DS owner | Edit | Run `/design-sync` | Write; owns `tokens` and `components` paths | Component API, tokens |
| Engineer | View, comment | View | Write | Code, a11y gates |
| Agent | Draft only | Read README and tokens | PRs only; never self-merges | None |

- Pick one comment surface per stage to avoid fragmentation: canvas comments during exploration, preview or PR comments once code exists.
- A reasonable default on hosting is Vercel or Netlify if comments on previews matter, and Cloudflare if access control and cost matter more and comments stay in the PR. Vercel requires each commenter to have an account, which is a real hurdle for external reviewers.
- Keep Figma view-only for a defined period (budget one cycle) rather than deleting. This avoids burning the bridge and is cheap insurance.
- Contractors and agencies are a likely hidden cost if their deliverables assume Figma (my inference). A connected Figma MCP in this environment exposes an `html_to_figma` tool, which may serve as an escape hatch, but Cisco reports HTML-to-Figma loses interactions.

### Gaps
- Whether a user can browse and restore prior versions on a Design canvas needs a hands-on test because the docs conflict.
- Figma's terms on exporting comments or version history: not found.
- Chromatic's current official pricing could not be confirmed from the page. Argos and Playwright costs were not compared.

## AI-native design system practices: making the system legible to agents, and the evidence

### Takeaway
Evidence favours a small always-on context, structured machine-readable component data, a deterministic linter or checker, and your own evals. It does not favour big agent-instruction files. The benchmarks are small and many are self-reported, but they point the same way: agents do better grounded than ungrounded, and rules hold only when something can refuse them. Claude Design's Design System artifact fits this model but has real constraints, including copies per canvas and context costs.

### Cited Findings

**Evidence on instruction files**

- **Vercel (27 Jan 2026) [V, authors' own eval, Next.js 16 APIs outside training data].** Baseline 53%; skill default 53% (never invoked in 56% of cases); skill with explicit instructions 79%; compressed 8KB `AGENTS.md` docs index 100%. Authors expect the gap may narrow, and still recommend skills for action-specific workflows. — [Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)
- **ETH Zurich (Feb 2026, v3 Sep 2026) [P, academic].** Context files "generally do not improve task success" and raise inference cost by over 20%; repository overviews are not helpful; they are useful for non-standard practices. — [arXiv 2602.11988](https://arxiv.org/abs/2602.11988)
- These results are reconcilable. Vercel tested knowledge the model lacked; ETH tested general repo tasks.

**Evidence on grounding design system data**

- **BILL (Aug 2026) [T; four self-selected tasks, one run each, one model, own graders].**
  - Input tokens down 45% (19M to 10.4M). Grounded runs took a consistent 5 minutes versus 4–9. The grounded agent used correct DS components on the first pass.
  - Ungrounded failures: standard radio buttons instead of radio tiles, a form with no fields, hardcoded `#1c1b1b`.
  - Failures: a stale Data Table guide produced deprecated-API code, so docs generation was tied to the build graph with version headers. MCP outages stalled agents, so they added a pinned-CLI fallback and chose "a hard stop over silent degradation". Agents kept digging in `node_modules` until skills made grounding explicit. — [BILL](https://www.bill.com/engineering/how-we-made-our-design-system-bilingual)
- **Indeed benchmark (Diana Wolosin) [2; one DS, one model, one IDE].** 8 MCP data configurations. JSON was cheapest ($300 vs $1,500 a year against MDX) and most consistent, and used 80% fewer tokens than hybrid Markdown. Advice: JSON for APIs, Markdown with frontmatter for rules, always-on rules for foundations since "MCP only returns what was asked for". **Discrepancy:** the page states 22 prompts × 3 runs × 8 configs yet 1,056 total; that multiplication gives 528. — [Into Design Systems](https://www.intodesignsystems.com/design-systems-mcp)
- **GitHub Primer agent-eval [P, live benchmark, latest run 2 Nov 2026].** Overall checks 55.3% (+30% vs Control), with output tokens +21.7% and time +21%. Variance is extreme: on "appropriate components" two models scored 100% and three 0%; theme switching 16.7% overall. The page doesn't define the treatment. — [Primer](https://primer.github.io/agent-eval/benchmarks/design-system)
- **design-system-mcp PR [V, maintainer's own, 10 components].** Haiku 4.5: 6/10 clean to 10/10, errors 13 to 0, cost −11%. Opus 5: 8/10 to 10/10, cost +7%. — [GitHub PR](https://github.com/dgesteves/design-system-mcp/pull/10)
- **LogRocket [T, n=1 form].** Without MCP, 263 lines of bespoke inputs — [LogRocket](https://blog.logrocket.com/storybook-mcp-for-ai-aware-component-libraries). **Storybook/Reshaped experiment [T]:** agents often generate their own components rather than use the system — [Discussion](https://github.com/storybookjs/ds-mcp-experiment-reshaped/discussions/1).
- **TJ Pitre via Smart Interface Design Patterns [U, method not reported; Pitre teaches an AI and DS course].** 69/100 ungoverned vs 100/100 with a generated contract catalog. — [SIDP](https://smart-interface-design-patterns.com/articles/ai-drift-design-systems/)

**Enforcement**

- "A model can be talked around. But a schema can't." Recommended: AI drafts specs; deterministic non-AI checkers enforce on every commit. Opinion plus linked practitioner work, not a study. — [SIDP](https://smart-interface-design-patterns.com/articles/ai-drift-design-systems/)
- "Guidelines are not laws": the prompt usually wins (Laura Fehre, reported) — [Into Design Systems](https://www.intodesignsystems.com/design-systems-mcp). Anthropic confirms this ordering for artifacts: the design system outranks Claude's own choices, and your prompt outranks both — [Claude Code docs](https://code.claude.com/docs/en/artifacts) [P].
- Example lint: Atlassian's `ensure-design-token-usage` enforces tokens, is fixable, and has a preview variant to warn before erroring. — [Atlassian](https://atlassian.design/components/eslint-plugin-design-system/ensure-design-token-usage) [P]

**Tool state**

- **Storybook MCP.** In preview, "API may change". The docs toolset needs an opt-in `componentsManifest`, with support for React frameworks and `angular-vite`, plus Vue with an experimental flag, and none elsewhere. Includes `test-run` and `review-create`. No metrics claimed. — [Storybook 10.6](https://storybook.js.org/docs/ai/mcp/overview) [P]
- **shadcn MCP.** Browse, search and install from public, private and third-party registries that follow its spec; works with Claude Code, Cursor, VS Code and Codex. — [shadcn](https://ui.shadcn.com/docs/mcp) [P]
- **DESIGN.md.** Associated with Google Stitch; markdown of design rules said to be portable — [Review](https://muratesmer.pages.dev/blog/google-stitch-review-2026) [2]. Primary spec not readable. No efficacy evidence found.
- **llms.txt.** Used by shadcn and by Claude Code docs — [shadcn](https://ui.shadcn.com/docs/mcp), [Claude Code docs](https://code.claude.com/docs/en/artifacts). Tutorial coverage — [Codrops](https://tympanus.net/codrops/2025/12/09/supercharge-your-design-system-with-llms-and-storybook-mcp/). No efficacy evidence found.
- **Adoption [S].** 48% already run an MCP server, but only 17% rate docs "very AI-ready"; 59% report UI bypassing the DS; 50% say other teams' AI use causes real problems; recommended order is "documentation first, MCP second, quality over adoption". — [zeroheight](https://zeroheight.com/resources/state-of-ai-in-design-systems/)

**What Anthropic documents about Claude Design and Design Systems [P]**

- **Availability.**
  - Claude Design is available on all plans including Free, but **Design Systems are "in beta on Pro, Max, Ultra, Team, and Enterprise" and unavailable on Free** — [Academy](https://academy.claude.com/tutorials/create-a-design-system-with-claude).
  - Claude Design, Slides and Docs are in beta on Enterprise — [Release notes](https://support.claude.com/en/articles/12138966-release-notes). Templates are labelled beta — [Claude Code docs](https://code.claude.com/docs/en/artifacts).
- **Inputs.** GitHub repo, design files, uploads, local codebase, or `/design-sync`. "Design system import is only as good as its source." — [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)
- **Context cost.** Claude reads the full overview on every use, and every selected system with each request, so keep it short. Fonts need files. Existing designs keep their own copy of the system. — [Academy](https://academy.claude.com/tutorials/create-a-design-system-with-claude)
- **Limits from the type files** — [Design System type](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd), [Design type](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd):
  - A system: 1,008 files and 256 MiB. One file ≤15 MiB. One call 16 MiB.
  - A canvas: 512 files and 256 MB, at most four installed systems.
  - Component bundle: one classic IIFE script assigning `window.<Namespace>`, 6 MB maximum when built from code.
  - Artboards supply **React 18**, and a bundle carrying its own React cannot share the page's.
  - `tokens.json` must use the type's list shape. A DTCG-style map "is valid JSON the page CANNOT read". `calc()`, `color-mix()` and JS expressions are skipped on sync. (Format detail belongs to the other researcher, but the pipeline needs a translation step.)
  - Agents should read `project/README.md`, never the page.
- **Admin controls.** Retention, audit log events (`claude_artifact_*`), and Compliance API endpoints for listing and retrieving code artifact versions — [Claude Code docs](https://code.claude.com/docs/en/artifacts).
- **Live query from Claude Code.** A May 2026 request for a live query path was closed "not planned", though commenters found a Design MCP endpoint with broken auth as of June. Status now is unknown. — [Issue #60327](https://github.com/anthropics/claude-code/issues/60327) [T]
- **Quality.** Third-party testers report that even a detailed system doesn't always stop Claude's defaults — [Flowstep](https://flowstep.ai/blog/claude-design-review/) [V]. A plugin developer reports it "actually nails it" with exact tokens — [Boringbot](https://boringbot.substack.com/p/claude-design-what-it-is-how-it-works) [2].

### Inferences
Evidence-weighted priority for SMSP:

1. A short root `CLAUDE.md`/`AGENTS.md` containing only what is non-standard (where the DS lives, the "never hardcode" rule, how to escalate when no component fits). ETH and Vercel together argue for short, specific, and non-obvious.
2. The DS `README.md` written as imperative usage rules that name tokens.
3. Generated component metadata from code (types, manifest, version header), never hand-maintained, per BILL's stale-docs lesson.
4. Lint: no raw colours or spacing, no bare `<button>` where a DS component exists. Warn first, then error.
5. A small eval of 5–10 prompts run on each DS release, scoring component use, hardcoded values and a11y checks. Run each several times and across the models you actually use, because Primer shows large variance by model.
6. MCP last. It adds an uptime dependency (BILL), and for one small repo, files in the repo may already give the agent everything.

Skills are best for explicit workflows like "create component" or "extract from canvas". Don't rely on them for always-needed rules, since they may not trigger.

Check the React 18 constraint early. If production is on a different major version, the canvas bundle needs its own build target and may behave differently from production.

### Gaps
- No independent benchmark of Claude Design's DS adherence over time, and no controlled comparison of `llms.txt` or `DESIGN.md`.
- No current status for the Design MCP endpoint, and the official `/design-sync` reference page was not found. Third parties say React-only and run from the DS package repo — [wmedia](https://wmedia.es/en/tips/claude-code-design-sync-your-components) [2/U].
- The Primer page doesn't explain its control or treatment.

## Canvas-to-code pipeline: drift, direction of truth, extraction, role of the canvas

### Takeaway
After extraction, make truth flow one way: code wins, and the canvas consumes it. Anthropic's own `/design-sync` implements this literally, by making synced systems read-only on the page. The canvas stays valuable as the place to explore and propose changes, and proposals return to code as reviewed PRs. I found no evidence of working automatic two-way sync on a real product.

### Cited Findings

**Evidence for code-canonical**

- Anthropic's implementation: "`/design-sync` builds such a system from a codebase and publishes all of its files... each run replaces them. A page that opens it is read-only for everyone". Requests for change: "have the person edit the code and run `/design-sync` again". — [DS type: from-code.md](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd) [P]
- Third-party posts describe `/design-sync` as "two-way" — [Pillitteri](https://pasqualepillitteri.it/en/news/5308/claude-code-claude-design-two-way-sync-design-sync) [2]. **This conflicts with the read-only behaviour above for design systems.** Pushing code to a canvas as a design is a different thing from two-way system sync. Treat "two-way" claims as unverified.
- GitHub re-sync is non-destructive but one-directional: the repository is read-only; it updates changed values, keeps usage notes and fonts, and lists removed tokens and asks before deleting. — [DS type](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd), [Academy](https://academy.claude.com/tutorials/create-a-design-system-with-claude) [P]
- Dual Figma and code systems caused "constant drift" until the DS lived only in code — [Zheng](https://changying.substack.com/p/case-study-from-figma-first-to-code) [T]. Storybook is the shared source, because parallel AI docs would go stale — [BILL](https://www.bill.com/engineering/how-we-made-our-design-system-bilingual) [T]. Frost and Lovely discussed "code is the source of truth" (title only seen) — [Frost](https://v9.bradfrost.com/links/post/brad-frost-and-evan-lovely-code-is-the-source-of-truth/) [U].

**Evidence for prototype-canonical (narrower)**

- Cisco: "The HTML prototype became the single source of truth." This is a product-intent source for one internal app, with engineers applying changes via changelog. It is not a shared DS across products. — [Cisco](https://blogs.cisco.com/cisco-devnet/design-to-code-ai-handoff-workflow) [T]
- Hikari's never-merged design branches are a variant: the prototype is a spec, not a source. — [note](https://note.com/hgffdgn654/n/n92467b83a1c1?hl=en) [T]

**Built-in drift mechanisms to design around [P]**

- **Canvases hold copies.** "A design system on a canvas is a copy in the canvas's own files... a copy never changes by itself." The record stores `artifact`, `version` and `copiedAt`. — [Design type refs](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd). "Existing decks and designs keep their own copy." — [Academy](https://academy.claude.com/tutorials/create-a-design-system-with-claude)
- **Artboards are not production code.** They use `<x-dc>`, `support.js`, `{{holes}}`, `<sc-for>`, `<dc-import>` and classic-JS `DCLogic`, and inline `style` is what the properties panel edits. — [Design type](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd)
- **One value source inside a DS artifact:** values in `tokens.json` are removed from stylesheets during clean-up so edits win; "Code is truth, screenshots are lossy guidance"; "never invent". — [DS type: craft.md](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd)

**Extraction and drift tooling**

- Dembrandt offers a CI gate that exits 1 when tokens move against a live site — [GitHub](https://github.com/dembrandt/dembrandt) [T/young project]. Designlang compares local tokens with a live site — [GitHub](https://github.com/Manavarya09/design-extract). These detect drift against deployed sites, not prototype extraction.
- A community token-sync skill classifies drift (stale copies, orphans, raw values) and asks which copy is canonical, because direction is a human decision. — [skills.sh](https://www.skills.sh/onewave-ai/claude-skills/design-tokens-sync) [U]
- Component contracts as readable descriptions with a checker on each commit. — [SIDP](https://smart-interface-design-patterns.com/articles/ai-drift-design-systems/) [opinion]
- Handoff gives Claude Code bundle context, but the reverse query path was missing in June — [Issue #60327](https://github.com/anthropics/claude-code/issues/60327). Most prototypes get refactored — [Zheng](https://changying.substack.com/p/case-study-from-figma-first-to-code).

### Inferences
Recommended pipeline (my synthesis; no source documents this exact flow for `.dc.html`):

1. **Freeze and snapshot.** Export the canvas zip and commit it under `design-source/` as a dated, read-only reference.
2. **Extract tokens first, deterministically.** Parse inline `style` values, helmet CSS and `project/ds/*/tokens.json` with a script (an AST or DOM parser, not a model). Produce a frequency report of every colour, size, radius and spacing. Humans or an agent cluster near-duplicates into tokens, and a human decides. Use AI for naming and clustering, and a script for inventory and verification.
3. **Rewrite, don't copy, components.** Have an agent implement production components from artboards, using `x-import` usages and repeated markup as the inventory. Verify against visual snapshots of the artboards. Because `.dc.html` is its own runtime, a pure codemod won't produce production components.
4. **Cut over.** Once a token or component is in the repo, make it canonical. Run `/design-sync` (or GitHub sync) so the DS artifact becomes a generated read-only view, then update canvases by reinstalling the system.
5. **Change flow afterward.** Canvas exploration leads to a changelog (Cisco's pattern), then a PR against code, then review on preview, then merge, then `/design-sync`.
6. **Drift checks.**
   - Script: raw-value scan of the repo; compare `designSystems[].version` in canvas files against the current DS version; list stale canvases.
   - Rule: a canvas is not evidence of what ships. Previews and Storybook are.

Canvas role after extraction: **exploration, proposals and review, non-canonical.** It keeps what it does best: cheap divergence and stakeholder comprehension. Label canvases with the DS version and date, and archive once shipped.

Exception: if a pattern has no code yet, the canvas may temporarily be the only spec. Mark it "proposed", not "system".

### Gaps
- I found no published walkthrough for extracting a production DS from `.dc.html` or equivalent AI canvas HTML. This is new ground, so a time-boxed spike is warranted.
- Whether `/design` import preserves mounted-component mappings into production code is not documented in what I read.

## Governance for a small team: contribution, ownership, deprecation, metrics, staffing, maturity

### Takeaway
Small is normal, and arguably an advantage if you make the decisions deliberately. Most systems have 2–5 people who also do product work. SMSP needs one named owner, lightweight decision records and a shortened version of the classic governance flow, plus machine enforcement. It does not need committees, an elaborate maturity program or a separate docs site yet. AI raises the importance of the shadow-AI bypass problem.

### Cited Findings

**Team size**

- "Small is the norm." Most DS teams are 2–5 people, often also doing product work; 5,000+ employee organisations average 9–11; teams rarely exceed 20–25. Lean teams keep context shared, blur roles and prioritise tightly, but are fragile, with knowledge in heads and docs deprioritised. Method: zeroheight reports plus unspecified practitioner conversations. — [NN/g, 15 May 2026](https://nngroup.com/articles/lean-design-system-teams)
- zeroheight 2025: average team 3 at under 100 employees, 4 at 100–499, 9 at 500+; 41% at smaller companies felt understaffed (search snippet) — [Report PDF](https://othr.zeroheight.com/hubfs/zeroheight%20-%20Design%20System%20Report%202025%20-%20release%20version.pdf) [S/2]. About half of teams are only partially resourced — [zeroheight](https://zeroheight.com/?p=17161) [V].
- "No time" is the top barrier at 25%. — [zeroheight](https://zeroheight.com/resources/state-of-ai-in-design-systems/) [S]

**Models and process**

- Curtis's solitary, centralized and federated models — [EightShapes](https://eightshapes.com/articles/team-models-for-scaling-a-design-system) [P, 2015]. Federated members commonly give about 25% of their time, per a secondary write-up — [Center Centre](https://articles.centercentre.com/?p=860) [2]. Curtis in 2026 argues system thinking and governance remain essential as non-deterministic workflows grow (listing only) — [podcast](https://podcasts.apple.com/us/podcast/id1826876587) [2].
- Frost's 10-step governance flow (2019): use, reach out, classify snowflake vs system, prototype, review, build and test, final review, document, release, adopt. — [Frost](https://bradfrost.com/blog/post/a-design-system-governance-process/) [T]
- Dan Mall (2022, pre-AI): extract from the product rather than build foundations in isolation ("foundations" is one of the most toxic ideas in DS); only support requests appearing in three or more teams; don't be the "design police"; don't become a service desk; your won't-do list should be longer than your will-do list; track retention. — [Reshaped](https://reshaped.so/blog/interviews/dan-mall) [T]. Pilots test the system before v1 — [Frost on Mall](https://bradfrost.com/links/post/design-systems-pilots-scorecards/) [T]. Hot Potato replaces handoff with rapid back-and-forth — [UX Planet](https://uxplanet.org/hot-potato-process-as-replacement-for-design-handoff-8a131e23da04) [2].

**Maturity**

- zeroheight model extends Sparkbox's four stages to six axes: Foundations, Documentation and Knowledge, Governance and Team, Adoption, Measurement and Impact, and AI Readiness; stages are V1, Growing, Teenage, Healthy Product. — [zeroheight](https://zeroheight.com/maturity) [V]. Sparkbox's model is built on client work, its survey and interviews — [Sparkbox](https://sparkbox.com/foundry/design_system_maturity_model_assessment_design_system_evolution) [V]. Latest Sparkbox survey data seen via secondary only.
- Atomic Design remains a reference vocabulary. Frost's current focus is "agentic design systems", with AI assembling UI from production components per a third-party note — [Frost](https://bradfrost.com/blog/link/agentic-design-systems-in-2026-with-brad-frost/), [note](https://samsen-knowledge.pages.dev/external/design-systems/agentic-design-systems) [2]. He co-teaches a paid course on this, so note the interest — [Frost](https://bradfrost.com/notes/post/2026-03-26-0033/).

**Global design system**

- Frost proposed shared common web components to reduce duplicate effort, distinct from new HTML features (Open UI) — [Frost](https://v9.bradfrost.com/blog/post/a-global-design-system), [follow-up](https://v9.bradfrost.com/blog/post/whats-next-for-a-global-design-system). I found no dated 2026 status.

**Adoption data and metrics**

- 7% report full adoption and 61% moderate or below (zeroheight 2026 via blog) — [mean.ceo](https://blog.mean.ceo/?p=11517) [2/U]. Only 8% say their DS is "very stable" — [OverlayQA](https://overlayqa.com/blog/design-system-drift/) [2/U]. Sample size conflict: about 300 per one blog vs 147 on zeroheight's survey page — [zeroheight survey](https://report.zeroheight.com).
- AI users report higher adoption but lower trust (webinar description); 56% use AI and only 15% say it lives up to the hype. Those figures differ from the separate State of AI report's 82%. — [zeroheight webinar](https://webinars.zeroheight.com/register/zeroheight-design-systems-report-2026-ai-and-design-systems-the-promise-and-the-reality) [S/2]
- Omlet (from Zeplin) analyses React and React Native component usage and DS adoption — [Zeplin](https://blog.zeplin.io/meet-omlet-component-analytics-for-developers) [V]. `react-scanner` is an open-source static analyser that Productboard built on — [Productboard](https://www.productboard.com/blog/how-we-measure-adoption-of-a-design-system-at-productboard/) [T].

**Failure modes seen in evidence**

- Stale docs misleading agents — [BILL](https://www.bill.com/engineering/how-we-made-our-design-system-bilingual).
- Parallel sources of truth — [Zheng](https://changying.substack.com/p/case-study-from-figma-first-to-code), [Cisco](https://blogs.cisco.com/cisco-devnet/design-to-code-ai-handoff-workflow).
- Shadow AI bypass (59%) — [zeroheight](https://zeroheight.com/resources/state-of-ai-in-design-systems/).
- Knowledge in one head — [NN/g](https://nngroup.com/articles/lean-design-system-teams).

### Inferences
Suggested lightweight model for SMSP (solitary-to-light-federated):

- **Ownership.** One accountable DS owner with reserved time (a suggestion: about 20–50% in the first 90 days), plus one engineer and one designer as named reviewers. CODEOWNERS on `tokens/`, `components/`, `docs/` and generated output. (CODEOWNERS is a standard GitHub feature; not re-verified in this pass.)
- **Contribution flow,** compressing Frost's 10 steps:
  1. Check the system.
  2. Classify as one-off or system.
  3. Propose on canvas or in a PR.
  4. Review on preview.
  5. Merge with changelog entry.
  6. Run `/design-sync` and notify.

  Adapt Mall's threshold for a small organisation: promote at the second or third real use, not speculatively.
- **Decisions.** A `docs/decisions/` folder with one short markdown record per consequential decision. Copy decisions out of canvas comments, because comments are not durable.
- **Deprecation.** Mark `@deprecated` with a replacement and removal version; lint warns, then errors; one release minimum notice; a codemod or agent prompt for migration; keep a changelog with semver. The evidence for any specific window is absent, so this is a sensible default rather than a finding.
- **Metrics that fit a small team** (cheap and automatable): share of JSX elements from the DS (`react-scanner`), raw-value lint count trend, eval pass rate per release, a11y violations in Storybook or CI, number of one-off components, and time from canvas approval to merge. Skip Omlet until multiple repos justify it, and skip ROI modelling.
- **Maturity use.** Use zeroheight's six axes as a once-a-quarter self-check. The AI Readiness and Documentation axes are the ones to watch. Avoid treating stage scores as a goal.
- **Global design system.** Not relevant to immediate decisions.
- **Bus factor.** It's the top structural risk for SMSP. Mitigate with generated docs and agent-readable runbooks.

### Gaps
- No direct first-hand governance guidance from Jina Anne was found in this pass.
- No evidence comparing RFCs vs ADRs in small DS teams, and no empirical basis for a deprecation window.
- Full zeroheight 2026 report and latest Sparkbox survey numbers were gated or not retrieved. Sparkbox's stage definitions weren't on the page fetched.

## Risks and mitigations

### Takeaway
The most urgent risk is operational and dated: standalone Claude Design closes on **14 December 2026, 41 days from today**, with comments and chats not moving. The largest structural risk is depending on a fast-changing preview-grade product as the sole record. Both are mitigated by getting the source into Git early. Accessibility and sameness are real but controllable through the component layer, CI and human taste review.

### Cited Findings

**Vendor lock-in and data**

- Standalone closes 14 Dec 2026 and becomes read-only. **Chats and comments don't move and are "deleted some time after it closes".** Public links to standalone projects stop working. Moving is irreversible ("this can't be undone"), and only a project's owner can move it. Design systems built from a starter theme and empty systems don't move. A moved system can't be edited directly on its page yet. — [Move guide](https://support.claude.com/en/articles/17440474-move-from-standalone-claude-design-to-claude) [P]
- **Silent deletion risk:** if the org's retention period covers artifacts, a moved project or system "can be permanently deleted if nobody opens it"; the clock restarts when someone opens or edits. — [Move guide](https://support.claude.com/en/articles/17440474-move-from-standalone-claude-design-to-claude), [Admin guide](https://support.claude.com/en/articles/14604406-claude-design-admin-guide-for-team-and-enterprise-plans) [P]
- Backup routes: Project archive zip via Share > Project HTML, free, every file, no usage charge; "Download design system"; bulk export of owned projects, without chats or comments. — [Move guide](https://support.claude.com/en/articles/17440474-move-from-standalone-claude-design-to-claude). Export offers zip, PDF, PPTX, Google Slides and standalone HTML — [Get started](https://support.claude.com/en/articles/14604416-get-started-with-claude-design). Artifacts are stored on Anthropic infrastructure, and Claude Code artifacts are unavailable under CMEK, HIPAA or ZDR policies — [Claude Code docs](https://code.claude.com/docs/en/artifacts).
- No native Figma export per third parties — [Montaldo](https://pietromontaldo.substack.com/p/claude-design-full-tutorial) [2/U]. Data residency unsupported per a third party — [uxpilot](https://uxpilot.ai/blogs/claude-design-review) [V/U]; Anthropic's pages read didn't address this.
- Product pace: launched in April, merged into conversations in September, standalone closing in December — [Release notes](https://support.claude.com/en/articles/12138966-release-notes) [P]. Type files show a versioned runtime contract (`0.2.47`) — [Design type](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd) [P].
- Usage limits: reviewers complain of tight limits — [Boringbot](https://boringbot.substack.com/p/claude-design-what-it-is-how-it-works) [2], and Cisco's designer had to switch tools on token limits — [Cisco](https://blogs.cisco.com/cisco-devnet/design-to-code-ai-handoff-workflow) [T].

**Sameness**

- Anthropic attributes generic output to "distributional convergence": "Safe design choices... dominate web training data." The remedy skill is about 400 tokens. Results are side-by-side images with no measurements. — [Anthropic, Nov 2025](https://www.claude.com/blog/improving-frontend-design-through-skills) [P/V]
- Reviewers say experienced designers claim to spot the look, and loose prompts make the tool "implement the design it has in its system prompt". — [Boringbot](https://boringbot.substack.com/p/claude-design-what-it-is-how-it-works), [Flowstep](https://flowstep.ai/blog/claude-design-review/) [2/V]. The Design type itself warns "Cream, serif display and clay are your habit" — [Design type](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd) [P]. That's a striking primary admission of default bias.

**Accessibility**

- AudioEye [V, sponsored]: five AI tools (OpenAI, Anthropic, Google, xAI, Lovable) built three sites each; all 15 failed WCAG Level A; 55 issues per page on average. 81% of AI-using teams were confident of compliance while 50% noticed more issues. — [VentureBeat, presented by AudioEye](https://venturebeat.com/ai/we-asked-five-ai-tools-to-build-accessible-websites-all-15-sites-failed), [Release](https://www.marketscreener.com/news/audioeye-study-finds-ai-coding-tools-do-not-write-accessible-code-ce785ad2d18bf520)
- WebAIM 2026 reportedly 95.9% of homepages with failures, up 10.1% in errors, AI suggested as a contributor (secondary, not verified at WebAIM). — [same source](https://venturebeat.com/ai/we-asked-five-ai-tools-to-build-accessible-websites-all-15-sites-failed)
- CHI '26 paper on semantic accessibility gaps in LLM-generated UIs — [Calò et al.](https://iris.polito.it/retrieve/handle/11583/3008330/983056) [P, not read in full]. Silktide audit of Antigravity output found a11y deprioritised — [Silktide](https://silktide.com/blog/google-antigravity-accessibility-issues/) [V].
- Claude's own type rules demand real controls and 4.5:1 contrast, but rules are instructions rather than guarantees. — [Design type](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd), [DS craft.md](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd) [P]

**People**

- Fear was the first problem Zheng's programme addressed; manager pushback on Figma skills — [Zheng](https://changying.substack.com/p/case-study-from-figma-first-to-code) [T]. ServiceNow says non-coders struggled with setup and troubleshooting — [ServiceNow](https://www.servicenow.com/community/innovation-office-blog/idea-to-code-in-an-ai-world-do-we-need-figma/ba-p/3394865) [T]. Hand adjustments beat prompts for small tweaks — [note](https://note.com/hgffdgn654/n/n92467b83a1c1?hl=en) [T]. Top concern for DS practitioners is output quality, not job loss — [zeroheight](https://zeroheight.com/resources/state-of-ai-in-design-systems/) [S].

### Inferences

| Risk | Mitigation |
|---|---|
| Standalone closure and loss of comments | This week: inventory what lives in standalone vs artifacts; download zip; copy key comments and decisions to the repo; move projects; check retention settings |
| Lock-in to canvas | Scheduled export of canvases and DS to Git (weekly at first); code canonical; a restore drill once per quarter; keep a script proving that exported HTML renders outside Claude |
| Auto-deletion | Confirm retention configuration; assign owner; Git backup means deletion is survivable |
| Product change | Pin assumptions in a short doc; recheck release notes monthly; avoid building on undocumented internals of `.dc.html` |
| Sameness | Brand-specific README; a real typeface with supplied files; real product copy, including Bahasa Indonesia content; maintain a "banned defaults" list; human taste review before anything becomes a pattern; add distinctive components only where they matter |
| Inconsistency | Lint plus evals; generated metadata; agents open PRs only |
| A11y | Build a11y in DS components (headless primitives if chosen by the other workstream); axe in Storybook or CI; manual keyboard and screen reader pass per component; AI output never counts as verified |
| Loss of designer involvement | Designers own the canvas, review previews and hold approval on visual quality; pair each designer with an engineer; Hot Potato cadence; training budget; don't require coding fluency as a day-one condition |
| Skills gap | Git and preview literacy, not full coding; agent-driven PRs with an engineer reviewer; small papercut fixes first as in Zheng's programme |
| Cost and limits | Budget seats; keep work portable so a limit doesn't halt it; monitor usage |
| Figma exit | Export `.fig` and assets before downgrading; keep view-only access for a period; check export restrictions; save brand assets as source SVGs |

Note on Bahasa Indonesia: agent evals and DS examples should include Indonesian strings, since text length and casing can differ from English defaults. This is my reasoning and I found no source specific to this.

### Gaps
- No measured study of AI UI sameness.
- AudioEye figures are unreplicated and vendor-funded. WebAIM primary was not opened.
- Data residency, Indonesian PDP compliance, and Anthropic's specific retention defaults for Team plans were not established.
- Exact behaviour of artifact export (whether a canvas zip runs standalone) needs a hands-on test.

## Rollout: phased plan, 30/60/90, minimum viable design system, what NOT to do first

### Takeaway
Practitioners agree on small scope, a real pilot and extraction from what exists, but disagree on whether tokens or components lead. No published 30/60/90 exists for a Figma-free, canvas-originated system, so the plan below is a synthesis and should be labelled as such. The key sequencing rule: secure the source first, extract tokens plus a handful of components into code and prove them on one real feature, then add enforcement, and only then consider MCP or wider rollout.

### Cited Findings
- **Start from the product, pilot early.** Mall: "We always start with what's done in the product, and then we pull stuff out"; avoid months of foundations; build what you need, such as a bank's data table. — [Reshaped](https://reshaped.so/blog/interviews/dan-mall) [T]. Pilots before v1. — [Frost](https://bradfrost.com/links/post/design-systems-pilots-scorecards/) [T]
- **Conflict.** Magic Patterns recommends tokens before components, and one new feature built only from DS components within the rollout, with phased rollout for most mid-size teams — [Magic Patterns, Jun 2026](https://www.magicpatterns.com/blog/design-system-implementation) [V]. Interface Shift prefers navigation, buttons and form fields first — [Interface Shift](https://interfaceshift.substack.com/p/introducing-a-design-system-without) [T]. Mall opposes foundations in isolation.
- **90-day frame.** Dan Mall's "Design System in 90 Days" canvas scopes purpose, stakeholders and starting components — [SIDP](https://smart-interface-design-patterns.com/articles/design-system-90-days/) [T]. It predates this workflow and is a Figma template.
- **Change management.** Zheng's four phases took four months for 40 people: training, environment, internal tools, papercuts — [Zheng](https://changying.substack.com/p/case-study-from-figma-first-to-code) [T].
- **Start small in the tool.** Anthropic's guidance for a first system with nothing to build from: 6–10 colours in one theme, 5–7 text styles, 4 spacing steps, 3 radii, a one-paragraph README, no components — [DS type](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd) [P]; "The first draft is deliberately small" — [Academy](https://academy.claude.com/tutorials/create-a-design-system-with-claude) [P].
- **AI order.** zeroheight: "documentation first, MCP second, quality over adoption" — [zeroheight](https://zeroheight.com/resources/state-of-ai-in-design-systems/) [S].
- **Constrain scope.** "Being small makes prioritization visible and defensible" — [NN/g](https://nngroup.com/articles/lean-design-system-teams). Won't-do list longer than will-do list — [Reshaped](https://reshaped.so/blog/interviews/dan-mall).

### Inferences
**Minimum viable design system (synthesized):**

- Git repo with tokens in code and a generated DS artifact
- A README with usage rules
- 8–12 components driven by the pilot, likely Button, Input/Field, Select, Checkbox/Radio, Dialog, Table or List, Navigation, Toast/Alert, plus whatever is core to SMSP's product
- Storybook with states
- One preview per PR
- Raw-value lint in warn mode
- CODEOWNERS
- `CHANGELOG`
- A decisions folder
- Short agent instructions
- 5 eval prompts
- Axe checks

**Day 0–30: Secure and extract.**

- Week 1:
  - Back up everything; move anything from standalone before 14 Dec, and copy comments and decisions to the repo.
  - Export Figma assets and `.fig` files, keeping view-only access.
  - Confirm plan-level features: Team plan needed for org sharing and editors.
  - Name the owner and declare in writing: code is canonical after extraction; the canvas is non-canonical once a piece is extracted.
- Weeks 1–2: spikes to settle unknowns: version history behaviour, zip portability, `/design-sync` with your stack, the React 18 bundle constraint, and a designer-opened PR.
- Weeks 2–4: deterministic inventory from `.dc.html`; define the token set; pick one real pilot feature; build the first 3–5 components it needs; run `/design-sync`; reinstall on the canvas; stand up preview deploys.
- Exit test: a non-coder can review a preview and comment, and a designer can get a small change merged with help.

**Day 31–60: Prove on the pilot.**

- Ship the pilot from DS components only.
- Grow to 8–12 components as the pilot demands.
- Storybook with all states; axe in CI; visual snapshots on key components.
- Short `CLAUDE.md`; generated component metadata.
- First 5–10 prompt eval; lint at warn; measure baseline (hardcoded values, DS share).
- Run the change flow end to end at least twice: canvas proposal, changelog, PR, preview review, merge, sync.
- First retrospective with designers. Fix what's painful before scaling.

**Day 61–90: Enforce and extend.**

- Lint moves to error for new code.
- Deprecation policy and semver release.
- Second product area or migration of the highest-traffic existing screens.
- Add one MCP only if evals show a gap that files don't close.
- Scheduled canvas-to-Git backup automation.
- Stale canvas check.
- Quarterly maturity self-check.
- Decide whether to cancel Figma fully based on real gaps, keeping archives regardless.

**Explicitly do NOT do first:**

- Cancel Figma before the export and bridge period is complete
- Build a large component library, or copy a public system's inventory
- Attempt two-way canvas-code sync
- Build an MCP server before docs are right, or write a long agent instructions file
- Adopt several canvases or AI builders at once
- Build a multi-brand or multi-platform token architecture without a current need
- Build a bespoke docs site, since Storybook and the DS artifact suffice
- Set up heavy governance (committees, RFC templates) or ROI dashboards
- Roll out big-bang across all products
- Require all designers to become coders
- Treat the canvas or AI output as evidence of accessibility or of production behaviour

### Gaps
- No published 30/60/90 for this exact path; dates and component counts above are judgment calls, not findings.
- The number of products and repos at SMSP, team composition, and the production framework would materially change this plan. The React and Storybook assumptions in particular need confirming.

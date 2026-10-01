---
name: codemap
description: Build an evidence-backed interactive code map of a repository — a self-contained dark-theme HTML diagram plus a machine-readable codemap.json and a codemap.lock that fingerprints each module so you can tell what drifted since last time. Use this whenever the user asks to map, diagram, chart or visualize a codebase's architecture, wants to see how modules/services/queues/databases/external dependencies connect, asks "what talks to what", wants end-to-end flows traced through the system, asks to onboard someone onto an unfamiliar repo, or asks to regenerate/refresh an existing codemap. Also use it when they mention docs/codemap, codemap.json or codemap.lock by name, even if they don't say "code map".
---

# Codemap

Produce three files that are always generated together from the current repo:

| File | What it is |
|---|---|
| `codemap.html` | Self-contained interactive diagram. Opens from `file://`, no CDN, no server. |
| `codemap.json` | The same nodes/edges/flows as data, every one carrying a source path + symbol. |
| `codemap.lock` | Commit, tree state, scope, exclusions, and a per-module content fingerprint. |

The point of the exercise is that a reader can **check every claim**. A diagram nobody can verify decays into folklore within a release or two, so every node and edge here cites a file and a symbol that a validator re-greps on each run. If a symbol moves, the build fails instead of the map quietly going stale.

## The one failure mode to design against

The tempting path is to sketch a tidy 15-box diagram from a general sense of the repo, then go looking for files to justify it. That produces a map that looks authoritative and is subtly wrong — and the wrongness is invisible, because nobody can tell a remembered edge from a real one.

Invert it. **Harvest concrete facts first, aggregate second.** Read router registrations, import lines, model classes, external base URLs, task decorators, websocket consumers — collect each as a `(path, symbol)` pair. Only once you have a pile of facts do you group them into nodes. Edges then arrive with their evidence already attached, because the evidence is *where the edge came from*.

## Workflow

### 1. Orient

```bash
git rev-parse HEAD && git status --porcelain
ls docs/codemap/ 2>/dev/null          # does a map already exist?
```

If `codemap.lock` exists, this is a regeneration. Read the old lock, and after generating, report which module fingerprints changed — that is the "what drifted" answer the user came for. `generate.py` prints this comparison automatically.

Then get the shape of the repo: top-level directories, app/package directories, `package.json` workspaces, `INSTALLED_APPS` or equivalent, dependency manifests.

### 2. Harvest evidence

Go after the things that actually reveal structure. Adapt to the stack; the categories generalize even when the syntax doesn't:

- **Entrypoints** — URL/route registrations, CLI commands, `main`, server bootstrap, ASGI/WSGI app
- **Cross-module imports** — `from <other-package> import ...`, especially between top-level modules
- **Persistence** — model/entity/schema classes, migration dirs, connection config
- **External services** — base URLs, API keys in settings, SDK client construction (`boto3.client`, `AsyncOpenAI`, `requests.Session`)
- **Async work** — task decorators, queue publishes, cron/scheduler registrations, consumers
- **Frontend→backend** — the HTTP client instance, per-feature API modules, WebSocket construction
- **Tests** — where they live, and note that the convention may differ per module

Two habits that pay off:

- Prefer `git ls-files` over `find`, so generated and vendored trees never enter the picture.
- When a project doc claims a route or integration exists, **verify it before citing it**. Docs drift faster than code. In the repo this skill was built from, `CLAUDE.md` documented a FirstHx webhook route that no longer existed in `urls.py` — citing it would have put a fabricated edge in the map.

### 3. Choose nodes, deliberately

Cap the diagram at **20 primary nodes**. Above that a diagram stops being readable and becomes a hairball, and the discipline is the point: it forces you to name what matters.

Twenty goes fast. Datastores and externals are nodes too, and they consume half the budget before you've drawn a single application module. So decide the merges explicitly rather than discovering halfway through that you're over:

- Fold shared plumbing (utils, common, config, db adapters) into one platform node.
- Fold operator/dev-only tooling together.
- Promote a service layer to its own node when it owns the external doors — it makes the vendor edges land somewhere honest.
- **Never promote an external you cannot cite a call site for.** A dependency in a manifest is not a runtime edge.

Give each node a `role`; it drives the legend colour and the tier it lands in: `client`, `api`, `service`, `queue`, `datastore`, `external`.

### 4. Write `model.py`

The per-repo model — nodes, edges, flows, module scopes. Full field reference and worked examples: **`references/model-authoring.md`**. Read it before writing the model; it covers the edge-type enum, the `unknown` convention, and the module include/exclude mechanics.

A complete real-world model (20 nodes, 43 edges, 5 flows, Django + two React clients) lives at `docs/codemap/model.py` in the `mqol-aerie` repo, if that's the repo you're in.

### 5. Generate and validate

```bash
python3 <skill>/scripts/generate.py --out docs/codemap --model docs/codemap/model.py
```

This is the whole build. It loads your model, computes layout, writes all three files, prints the stale-module comparison, then validates. `--validate` re-checks what is already on disk without rewriting.

Expect to iterate here. A failing evidence symbol means you cited something that isn't there — **fix the citation, or drop the claim**. Never relax the validator to make a red line green; the validator is the entire value proposition.

### 6. Show the diff

New files produce an empty `git diff`, so stage intent-to-add first:

```bash
git add -N docs/codemap/ && git diff --stat -- docs/codemap
```

If the path is gitignored, `git add -N -f` works and you should tell the user *why* it was ignored rather than editing their `.gitignore` uninvited. A bare `codemap` line in `.gitignore` — meant for a built binary — silently swallows `docs/codemap/`; recommend anchoring it to `/codemap`.

### 7. Report

Cover, in this order: files written; **stale modules** (on a first run, say plainly that there was no prior lock and all modules are new — don't omit the heading); remaining unknowns; the validator's actual stdout, not a paraphrase of it; and the diffstat with an offer of the full text. Then surface the judgment calls you made — the node merges, the scope exclusions, anything you chose not to model — because those are the parts the user might disagree with, and they can't disagree with what they can't see.

## Verify the page before claiming it works

A generated HTML file that throws on load still passes every JSON check. Open it and drive it:

```bash
python3 -m http.server 8931 --bind 127.0.0.1 &   # some automation tools refuse file://
```

Click a node, select a flow, type in search, toggle a legend chip, drag a box, pan the background, hit Reset — then read the console. Tell the user the page opens directly with `open docs/codemap/codemap.html`; the local server is only a workaround for tooling that won't load `file://`.

**Drive it with real input, not `dispatchEvent`.** Synthetic events skip pointer capture entirely, so a whole class of interaction bug is invisible to them — a capture taken on the wrong element silently kills node selection while every synthetic test still passes. That exact bug shipped here. Playwright's `page.mouse.click/move/down/up` is the cheap way to get genuine events:

```js
const { chromium } = require('playwright');
// ... goto, then:
await page.mouse.click(x, y);
```

A useful probe is to log what each of `pointerdown` / `pointerup` / `click` actually targets; a `click` landing on `<svg>` rather than the node is the signature.

## What the page gives the reader

Precomputed layout (barycenter ordering over several seeds, lowest crossing count wins) so the browser runs no physics simulation and needs no D3. Clicking a node highlights upstream callers in pink, downstream dependencies in green, and fills the side panel with evidence, entrypoints, tests, flows and constraints. Selecting a flow traces its full path. Search, legend filtering, zoom, pan and drag all work on plain SVG.

One honesty detail worth preserving if you modify the page: a flow step is an *ordering*, not necessarily a single code edge. Steps backed by a real edge draw solid; steps with no direct edge draw dashed, with a legend note. That keeps the path readable end to end without the map asserting an edge the source doesn't have.

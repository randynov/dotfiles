# Authoring `model.py`

The repo-specific half of a codemap. `generate.py` imports six names from it:
`MODULES`, `NODES`, `EDGES`, `FLOWS`, `SCOPE`, `EXCLUDED_DIRS`.

Contents:
- [MODULES](#modules) — fingerprint and test scopes
- [SCOPE and EXCLUDED_DIRS](#scope-and-excluded_dirs)
- [NODES](#nodes)
- [EDGES](#edges) — including the closed type enum and the `unknown` convention
- [FLOWS](#flows)
- [Traps](#traps)

---

## MODULES

One entry per **internal** node. Externals and datastores have no source, so they are absent here. Keys should match node ids — then next run's "which modules changed" maps straight onto the diagram instead of being a separate vocabulary the reader has to reconcile.

```python
MODULES = {
    "api-surveys": {
        "include": ["server/aerie/surveys/"],
        "exclude": ["server/aerie/surveys/services/"],
    },
    "surveys-services": {
        "include": ["server/aerie/surveys/services/"],
        "exclude": [],
        "tests": ["server/aerie/surveys/tests/"],
        "tests_match": ["switchbird", "firsthx", "dropbox_sign"],
    },
}
```

- `include` / `exclude` — path prefixes matched against `git ls-files`. Exclude wins. This is how a sub-package becomes its own node without being double-counted in its parent's fingerprint.
- `tests` *(optional)* — prefixes for test discovery when tests don't live inside `include`. Frontend suites often sit in `<workspace>/tests/` rather than under `src/`; without this the node reports zero tests and the map looks untested when it isn't.
- `tests_match` *(optional)* — substring filter on the basename, for when several modules share one test directory.

Discovery keeps files whose basename starts with `test_` or contains `.test.` / `.spec.`, skipping `__init__.py` and `conftest.py`, capped at 12 per node.

## SCOPE and EXCLUDED_DIRS

`SCOPE` — the directories the map actually describes. Goes in both `codemap.json` and the lock.

`EXCLUDED_DIRS` — everything deliberately left out. Entries may contain glob segments
(`server/*/migrations`), and `tracked_files()` drops matching paths before anything else
sees them, so fingerprinting *and* test discovery work from the same universe.

That single choke point is the point, and it took two goes to get right. The first
version only recorded the list, so the lock told readers migrations were out of scope
while 202 of them were being hashed into `api-surveys`. The fix for that filtered inside
module membership, which left test discovery still reading excluded directories — the
same concept enforced in one place and forgotten in the other. Filtering where the file
list is born means a future consumer cannot forget it.

Worth separating in your report into two kinds, because they carry different weight:

- **Generated/vendored** — `node_modules`, `dist`, `__pycache__`, `.venv`, `static`, build output. Nobody will argue.
- **Scope judgments** — infrastructure-as-code, specs, migrations, scratch dirs. These are *your* calls and the user may well want one of them included. Say so explicitly in the report.

## NODES

```python
{
    "id": "api-surveys",              # stable slug; matches the MODULES key
    "path": "server/aerie/surveys",   # must exist on disk
    "role": "api",                    # client | api | service | queue | datastore | external
    "title": "surveys (patients, studies, notifications)",
    "summary": "One or two sentences on what this owns.",
    "entrypoints": [
        {"path": "server/aerie/surveys/urls.py", "symbol": "urlpatterns"},
    ],
    "constraints": [
        "Deletes are soft (is_active=False).",
    ],
    "evidence": {"path": "server/aerie/surveys/apps.py", "symbol": "class SurveysConfig"},
}
```

`tests` is filled in by the generator — don't write it by hand.

**Every `symbol` is re-grepped** in the file its `path` names, as a plain substring. So `"class SurveysConfig"` is a good symbol (specific, survives reformatting) and `"Survey"` is a bad one (matches anything). Pick a string that would genuinely disappear if the thing it names disappeared.

`constraints` is where the non-obvious rules go — the invariants someone would otherwise violate on their first day. "Never construct the service directly, use the factory." "IN_PROD is computed at import time." These are the highest-value lines in the whole map and the hardest to recover from code alone.

**Externals** get `path` and `evidence` pointing at the code that *reaches* them — the settings line holding the base URL, or the client construction — since they have no source of their own in this repo.

## EDGES

```python
{
    "from": "surveys-services",
    "to": "ext-switchbird",
    "type": "calls",
    "evidence": {"path": ".../switchbird.py", "symbol": "self.api_base_url"},
}
```

### The type enum is closed

`imports`, `calls`, `reads`, `writes`, `publishes`, `subscribes`. The validator rejects anything else.

This trips people up: when a relationship lacks evidence, the instinct is to write `"type": "unknown"`. That's not a legal type. **Unknown belongs in the `evidence` field**:

```python
{
    "from": "client-v1",
    "to": "ext-firsthx",
    "type": "reads",
    "evidence": "unknown",
    "note": "Config implies this hop, but no call site was found at this commit.",
}
```

A `note` is mandatory when evidence is unknown — an unknown with no explanation is indistinguishable from sloppiness.

### What "unknown" actually means

**"We can see the relationship but not its call site."** It does *not* mean "we suspect a relationship." If you can't find evidence, the honest first question is whether the edge exists at all.

A worked example: a `client-v1 → ext-firsthx` edge was first marked unknown because the vendor domain appeared only in a CSP setting. Two greps later: `client/src/services/firsthx/api.ts` goes through the app's own axios instance to the *backend* (so it's evidence of a client→api edge, not a vendor edge), while `client/src/components/firsthx-iframe.tsx` embeds the vendor origin directly and validates its `postMessage` origin (so the vendor edge is real, and that file is its evidence). The right outcome wasn't an unknown — it was one edge deleted and one edge properly cited. Spend the extra two greps.

## FLOWS

```python
{
    "id": "flow-switchbird-survey",
    "name": "SwitchBird SMS assessment round-trip",
    "trigger": "The self-scheduling background task fires (every 60s when ...).",
    "steps": [
        {"node": "task-queue", "detail": "start_once schedules the repeating sync."},
        {"node": "api-surveys", "detail": "The task walks Organizations with an inbox id."},
    ],
    "outcome": "Patient SMS responses land as Survey rows and reach the dashboard.",
}
```

Pick 3–5 flows you can trace **end to end in the source today**. A flow that's half-remembered is worse than one fewer flow — it's the part a new reader will trust most and verify least.

Every `step.node` must be an existing node id. Consecutive steps need not correspond to a graph edge; the page draws those hops dashed rather than pretending an edge exists.

## Traps

**Git state is provenance, not a gate.** The lock records the commit it was generated from and whether the tree was dirty, and both degrade in ordinary use: the generating commit stops being reachable after a squash or rebase merge and is absent entirely from a shallow clone (`actions/checkout` defaults to depth 1), and `dirty` describes the whole tree, so one unrelated edit would condemn an otherwise accurate map. The generator warns on both and fails only on a fingerprint mismatch. Keep it that way — the fingerprints are the drift check; the commit is there so a reader can find the source state.

**The lock lives in the tree it measures**, so a naive dirty flag would always read true. Let git exclude the output directory with a pathspec — `git status --porcelain -- . ':(exclude)<rel>'` — rather than hand-parsing porcelain to strip a prefix. The hand-rolled version mis-reads renames (`R  old -> new` yields the arrow and both paths) and quoted paths, and when the output lives outside the repo the prefix degrades to `../../..` and silently matches nothing.

**A validator that reports its own results by matching its own error text will eventually lie.** Deriving a PASS/FAIL summary from substrings of the failure messages means a reworded message, or a new failure kind nobody wrote a matcher for, prints PASS while the run exits non-zero. Measured here: two real failure kinds did exactly that. Have each checker return its name alongside its failures. And whatever the summary does, corrupt something on purpose and confirm the run goes red — a gate that has only ever been seen passing has not been tested.

**The repo name is not the directory name.** A clone directory is whatever the person who ran `git clone` chose, and in a worktree it is usually the branch — so `basename(cwd)`, `rev-parse --show-toplevel` and `--git-common-dir` all give an answer that differs between checkouts, which makes the committed page fail validation for everyone else. Derive it from the `origin` remote, falling back to the directory only when there is no remote. Both variants of this bug shipped once already.

**Node paths and evidence paths are repo-relative.** Always. The generator resolves them against the repo root, not the output directory.

**An untracked file is invisible.** Scopes are computed from `git ls-files`. A brand-new file contributes nothing to a fingerprint until it's at least `git add -N`'d.

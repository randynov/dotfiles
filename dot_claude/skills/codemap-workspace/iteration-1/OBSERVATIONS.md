# Iteration 1 — observations to weigh when reading the benchmark

## eval-1-regeneration is contaminated. Discount it.

The target repo for eval 1 is the Aerie lane, and that repo has `docs/codemap/generate.py`
vendored in it — the very generator the skill bundles. The no-skill baseline found it and ran
it. So the baseline inherited the skill's main artifact, and any pass-rate parity between the
two configurations on this eval says nothing about whether the skill helps.

A true regeneration baseline needs a repo that has a codemap but *not* a vendored generator.
Fix for a future iteration: seed a prior map for `scrumlr.io` into the workspace only, and
point eval 1 there.

## The seeded drift is detectable as artificial

To give the drift report something to catch, I corrupted two module fingerprints in the
previous lock to all-zeros and backdated `generated_at`. The baseline agent noticed: an
all-zeros value is not the sha256 of any content, the backdated `generated_at` disagreed with
its sibling `codemap.json`, and `git diff` between the lock's commit and HEAD was empty for
those paths. It correctly reported the two modules as flagged-but-not-really-changed.

That is good reasoning, but it means the eval measures "can you spot a doctored lock" as much
as "can you report drift." A cleaner design mutates real files and lets fingerprints diverge
honestly.

## A real generator behavior surfaced, worth keeping

When `--out` points outside the repo, `dirty_excludes` becomes a long `../../..` relative path
and no longer covers the repo's own `docs/codemap/`, so `dirty` flips to true. Harmless here
(the only uncommitted paths were outside every module's scope), and it only happens under the
eval harness's unusual out-of-tree output arrangement, not in normal use. Not worth
special-casing, but worth knowing before someone reports it as a bug.

## eval-2's premise was wrong — my verification was too narrow

I claimed AuditKit had no payments or analytics provider, having grepped only `*.go`, `*.js`
and `*.json`. Both exist, in files I excluded: a Stripe Payment Link appears in 26 tracked
files (25 HTML pages plus README), and `site/cookie-consent.js:37` injects `gtag.js` with an
`AW-` id. So the prompt's premise was true, not a trap.

That makes eval 2 a different and arguably better test — the correct answer is nuanced rather
than a flat denial. A Payment Link is a browser navigation, not an integration: no SDK, no
keys, no webhook, and no permitted edge type describes it. An `AW-` id is Google Ads, not
Google Analytics. The no-skill baseline got all of this right, including refusing to force
Stripe into an edge and filing it as an external node with an unknown relationship instead.

Consequence: eval 2 probably does not discriminate either. A strong model reaches the careful
answer without the skill.

## What eval 0 still measures cleanly

Both target repos (`scrumlr.io`, `AuditKit-Community-Edition`) have no codemap and no vendored
generator, so their baselines are genuine. Weight those two when judging the skill.

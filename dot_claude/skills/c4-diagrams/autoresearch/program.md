# C4 Diagrams Autoresearch Loop

## Purpose

Autonomously improve the `/c4-diagrams` SKILL.md by generating C4 diagrams, evaluating them
against fixed test scenarios, and mutating the skill instructions to maximize the score.

The artifact being optimized is `SKILL.md`. The test harness is `evaluate.py` + `scenarios.json`.
Both the evaluator and scenarios are **immutable** — never modify them.

---

## Paths

```
SKILL_MD     = ~/.claude/skills/c4-diagrams/SKILL.md
AUTORESEARCH = ~/.claude/skills/c4-diagrams/autoresearch/
SCENARIOS    = {AUTORESEARCH}/scenarios.json
EVALUATOR    = {AUTORESEARCH}/evaluate.py
RESULTS      = {AUTORESEARCH}/results.tsv
BACKUPS      = {AUTORESEARCH}/backups/
OUTPUTS      = {AUTORESEARCH}/outputs/
```

---

## Loop Algorithm

**On startup:**
1. Read `results.tsv` to find the last iteration number and best score so far.
2. Set `N = last_iteration + 1` (or `N = 1` if no prior iterations).
3. Set `best_score = max score seen in results.tsv` (or `-1` if none).

**Each iteration:**

### Step 1 — Read current state
- Read `SKILL.md` (phases 2–4 guide diagram generation; ignore phase 1 and 5).
- Read `scenarios.json` to get all 10 scenarios.

### Step 2 — Generate 10 .puml files
- Create directory: `{OUTPUTS}/iteration-{N:03d}/`
- For each scenario `S` in `scenarios.json`:
  - Follow SKILL.md phases 2–4 to produce a valid `.puml` for the scenario's `diagram_type`.
  - Write the file to `{OUTPUTS}/iteration-{N:03d}/scenario-{S.id}.puml`
  - **Do NOT render** (skip phase 5 — no PlantUML server calls).
  - **IMPORTANT**: After generating each diagram, note which specific SKILL.md section
    guided each decision. If you had to rely on general C4 knowledge rather than SKILL.md,
    mark it as a gap.

### Step 3 — Evaluate
Run:
```bash
python3 {EVALUATOR} --batch {OUTPUTS}/iteration-{N:03d}/ {SCENARIOS}
```
Parse the JSON output. Extract:
- `score` (total, max 40)
- `totals.completeness` (out of 10)
- `totals.technology` (out of 10)
- `totals.relationships` (out of 10)
- `totals.abstraction` (out of 10)

### Step 4 — Record result
Append a tab-separated row to `results.tsv`:
```
{N}  {ISO_TIMESTAMP}  {score}  {completeness}  {technology}  {relationships}  {abstraction}  {best_score}  {action}  {notes}
```
- `action`: `"baseline"` if N=1, `"keep"` if score > best_score, `"revert"` otherwise.
- `notes`: one-line summary of what was mutated (or "baseline" for first run).

### Step 5 — Check stop condition
- **If `score >= 39`: STOP.** Report final score and which mutations helped most.

### Step 6 — Keep or revert
- **If `score > best_score`**: update `best_score = score`. Keep SKILL.md as-is.
- **If `score <= best_score`**: revert SKILL.md from `{BACKUPS}/skill-{N-1:03d}.md`.
  (On iteration 1, there is nothing to revert — just record the baseline.)

### Step 7 — Analyze failures
Look at the per-scenario breakdown. Identify:
- Which criterion has the lowest pass rate?
- Which scenarios consistently fail?
- Is the failure due to missing instruction, ambiguous instruction, or wrong example?

### Step 8 — Mutate SKILL.md
**Targeting the weakest criterion**, make ONE focused change to SKILL.md:

| Weak criterion | Mutation strategies |
|---|---|
| completeness | Add explicit checklist of required elements per diagram type; strengthen "Every actor/system MUST appear" language |
| technology | Add a mandatory rule: "ALL Container and Component elements MUST include a technology parameter" with ✗/✓ examples |
| relationships | Add explicit rule: "ALL Rel() calls MUST have both a verb label AND a protocol/technology 4th param" |
| abstraction | Strengthen element type restrictions per diagram type; add a "forbidden types" callout box |

**Mutation guidelines:**
- Change ONE thing per iteration (makes it easier to attribute score changes).
- Prefer adding explicit rules over rewording existing ones.
- If rules already exist, make them more prominent (move to top, add ❌/✅ markers).
- If score is stuck for 5+ iterations without improvement, try a LARGER structural change:
  - Reorder sections
  - Add a "Quick Rules Checklist" at the top of the skill
  - Add per-diagram-type element tables
  - Strengthen or simplify examples

### Step 9 — Backup mutated SKILL.md
```bash
cp {SKILL_MD} {BACKUPS}/skill-{N:03d}.md
```

### Step 10 — Increment N and GOTO Step 1

---

## Mutation Constraints

- **NEVER** modify `scenarios.json` or `evaluate.py`.
- **NEVER** modify templates (unless stuck for 10+ iterations).
- **NEVER** add fictional features to SKILL.md (e.g., fake macros, invented syntax).
- **ALWAYS** validate any new syntax examples against `reference/syntax-reference.md`.
- **SIMPLICITY RULE**: If a mutation adds >50 words for <1 point gain, discard it and try a simpler alternative.

---

## Stopping Conditions

| Condition | Action |
|---|---|
| `score >= 39` | Stop. Report summary. |
| `N > 50` | Stop. Report plateau analysis. |
| Manual interruption | Stop. Save state. Report last score. |

---

## Expected Score Ranges

- **Baseline (iteration 1)**: 25–32 (partial compliance due to general C4 knowledge)
- **After 5 iterations**: 33–36 (explicit rules added)
- **After 15 iterations**: 37–39 (fine-tuned rules)
- **Goal**: 39–40

---

## Resume Instructions

If resuming after interruption:
1. Read `results.tsv` — find the last row.
2. Check if the last action was `"keep"` or `"revert"` — if `"revert"`, SKILL.md was already restored.
3. Set `N = last_iteration + 1`, `best_score = max score in file`.
4. Continue from Step 1.

---

## Output Format Per Iteration

After each iteration, print a compact status line:

```
[Iter N] score={score}/40  C={completeness}/10  T={technology}/10  R={relationships}/10  A={abstraction}/10  action={action}
Mutation: {one-line description of change made}
```

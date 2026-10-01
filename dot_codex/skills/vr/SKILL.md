---
name: vr
description: Validate implementation plans against the actual codebase to identify risks, breaking changes, missed edge cases, dependency impacts, test gaps, and simplification opportunities. Use when the user asks to review, validate, sanity-check, pressure-test, or assess a plan before implementation, especially when they mention /vr or "validate reasonableness".
---

# VR - Validate Reasonableness

Validate an implementation plan against the actual codebase. Be deliberately skeptical. Assume the plan has flaws: find what will break, what was missed, and what can be simplified.

This is a read-first workflow. Do not make implementation changes unless the user explicitly asks you to update the plan file or apply revisions.

## Inputs

Use the plan from the current conversation when present. If the user points to a plan file, read that file. If the target plan is ambiguous, ask one concise question before proceeding.

Collect quick repository context before judging the plan:

- `git status --short`
- `git diff --name-only HEAD~5` when the repository has enough history
- `git log --oneline -10`
- relevant files named by the plan
- adjacent callers, tests, schemas, config, and existing helpers

---

## Phase 1: Plan Extraction

Identify from the plan: proposed changes, files/components touched, expected outcome, assumptions, risks, and dependencies.

Write down the extracted assumptions before validating them. Treat unverified assumptions as risks until the codebase confirms them.

---

## Phase 2: Codebase Grounding

Trace the affected paths directly in the repo:

- map callers and dependencies for files the plan changes
- inspect existing tests around those paths
- compare the plan with established local patterns
- check API contracts, migrations, auth, config, observability, and rollout assumptions where relevant
- cite specific file paths and line numbers for concrete claims

Use local searches (`rg`, `rg --files`) and targeted file reads first. Browse or use documentation only when the plan depends on external behavior that may have changed or cannot be inferred from local code.

### Optional Parallel Review

Use subagents only when the user explicitly asks for parallel agents, delegation, or cross-agent review. If authorized, assign each subagent one bounded question and require file:line references.

---

## Phase 3: Gemini Cross-Model Review

Run Gemini as an optional independent reviewer when the local `gemini` CLI is installed and usable in the current execution environment. Gemini is additive; the validation must still stand on the local analysis if Gemini is unavailable or quota-limited.

Fill in [`reference/gemini-prompt.md`](reference/gemini-prompt.md), then run:

```bash
gemini -p "<filled prompt>" --approval-mode plan --output-format text --skip-trust
```

Rules:
- Keep Gemini read-only with `--approval-mode plan`.
- Do not use `--yolo`.
- Use `--skip-trust` for this read-only validation run so workspace trust prompts do not block the check.
- Treat Gemini availability as environment-specific. It may work in the user's terminal while failing inside a Codex sandbox due to TTY, auth, browser, network, or process restrictions.
- Do not disable telemetry by default. If local telemetry produces sandbox-only noise such as `connect EPERM 127.0.0.1:4318`, mention the noise in the status and continue; only retry with `GEMINI_TELEMETRY_ENABLED=false` if telemetry errors are the only thing preventing useful output.
- In non-interactive Codex sessions, do not try to answer Gemini prompts unless the command was started with a TTY. If Gemini prints `Opening authentication page in your browser. Do you want to continue? [Y/n]:`, stop the process, verify no `gemini -p` child process remains, mark Gemini unavailable in the current environment due to authentication, and continue.
- If Gemini prints repeated capacity messages such as `You have exhausted your capacity on this model. Your quota will reset after Ns`, let one short retry window pass. If it does not produce findings promptly, stop it, verify cleanup, and mark cross-model review `timed out (Gemini quota/capacity)`.
- If Gemini times out, returns empty output, or keeps emitting telemetry errors after interruption, clean up the Gemini process, verify cleanup, and continue without cross-model review.
- Keep Gemini findings in a separate `Cross-Model Review (Gemini)` section. Note agreement and novel findings; do not merge Gemini output blindly into your own severity calls.

---

## Phase 4: Validation

For each part of the plan, answer the questions in [`reference/validation-questions.md`](reference/validation-questions.md). Run through the deep validation checklist in that file.

---

## Phase 5: Synthesis & Resolution

1. Lead with findings ordered by severity.
2. Separate observed facts from inferences.
3. Include file:line references for code-grounded claims.
4. Identify simplifications and their tradeoffs.
5. If the user asked to update the plan file, revise the original plan directly and document revisions made.
6. If a critical decision cannot be resolved from code, ask the user a concise question before finalizing.

---

## Output

Use [`reference/output-template.md`](reference/output-template.md) when writing results into a plan file. For chat-only reviews, use the same structure but keep it concise.

When updating a plan file:
- fix plan conflicts directly when the correction is clear
- document what changed in "Plan Revisions Made"
- update the original plan only unless the user asks for a separate file

---

## Finish

End with a clear verdict:

- `CRITICAL`: plan has blockers that are likely to break implementation
- `CAUTION`: plan is directionally workable but needs revisions before implementation
- `REASONABLE`: no major blockers found; note residual risks and tests

---

## Success Criteria

- [ ] Plan assumptions extracted
- [ ] Affected code paths inspected
- [ ] All validation questions answered with file:line references
- [ ] Concerns categorized by severity with mitigations
- [ ] Simplification opportunities identified
- [ ] Gemini review completed or explicitly marked unavailable
- [ ] Original plan file updated if the user requested file changes
- [ ] Clear verdict (CRITICAL | CAUTION | REASONABLE)

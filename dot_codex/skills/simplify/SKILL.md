---
name: simplify
description: Review changed code for simplification opportunities, reuse of existing utilities, code quality problems, and efficiency issues. Use when the user asks to simplify, clean up, review changed files for reuse or quality, run a cleanup pass after implementation, or apply a multi-agent changed-code review before fixing issues.
---

# Simplify

Review changed files for reuse, quality, and efficiency. Fix confirmed issues directly after the review passes finish.

## Workflow

1. Identify the changed files.
   - Run `git diff --stat` and `git diff`.
   - If there are staged changes, run `git diff HEAD`.
   - If there are no git changes, review the most recently modified files the user mentioned or that you edited in the current task.

2. Respect repository instructions before exploring.
   - If repo guidance requires graph or indexing tools before text search, use those tools first.
   - Use `rg` after the required project-specific exploration tools, unless the repo provides a better local search path.

3. Launch three independent review agents in parallel when subagents are available.
   - Use the available subagent tool. In Codex, prefer `multi_tool_use.parallel` with three `functions.spawn_agent` calls.
   - Pass each agent the full diff plus the repository path.
   - Tell agents to return findings only and not edit files.
   - If subagents are unavailable, run the three review passes yourself before editing.

4. Aggregate findings.
   - Fix clear, scoped issues.
   - Skip false positives or changes that would widen scope. Mention skipped items briefly in the final answer.
   - Preserve user changes and unrelated work in the worktree.

5. Verify the result.
   - Run the smallest relevant formatter, lint, type-check, or test command that covers the edited files.
   - If no suitable command exists or a command cannot run, state that clearly.

## Agent Prompts

Use these prompts as the core of each parallel agent request. Add the full diff after the prompt.

### Code Reuse Review

Review the changed files for reuse opportunities.

- Search for existing utilities, helpers, shared modules, and adjacent patterns that could replace new code.
- Flag new functions that duplicate existing functionality.
- Flag inline logic that should use existing helpers, especially custom string manipulation, path handling, environment checks, type guards, parsing, or formatting.
- Return concise findings with file paths, line references when available, and the existing code to reuse.
- Do not edit files.

### Code Quality Review

Review the changed files for quality issues and over-complication.

- Flag redundant state, cached derived values, avoidable observers, and effects that could be direct calls.
- Flag parameter sprawl where a new parameter weakens an existing abstraction.
- Flag copy-paste variants that should share a helper.
- Flag leaky abstractions and raw string use where constants, enums, string unions, or branded types already exist.
- Flag unnecessary JSX nesting or wrappers that add no layout value.
- Flag nested conditionals three or more levels deep and suggest guard clauses, early returns, lookup tables, or flatter cascades.
- Flag comments that narrate what the code does, reference the task, or repeat clear identifiers. Keep only comments that explain non-obvious constraints.
- Return concise findings with file paths and line references when available.
- Do not edit files.

### Efficiency Review

Review the changed files for avoidable work and resource risks.

- Flag redundant computations, repeated file reads, duplicate network or API calls, and N+1 patterns.
- Flag independent operations that run sequentially and can run concurrently.
- Flag blocking work added to startup, request, render, polling, or event-handler hot paths.
- Flag recurring no-op updates. Check whether updater callbacks can return the same reference to suppress downstream notifications, and whether wrappers preserve that no-change signal.
- Flag pre-checks for resource existence before operating when direct operation plus error handling would avoid TOCTOU risk.
- Flag unbounded data structures, missing cleanup, and event listener leaks.
- Flag overly broad reads or loads when a narrower query or slice would work.
- Return concise findings with file paths and line references when available.
- Do not edit files.

## Final Response

Keep the final response brief:

- State what was fixed.
- State any skipped finding and why.
- State the exact validation command and result.

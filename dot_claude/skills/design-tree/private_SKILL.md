---
name: design-tree
description: Walk a topic end-to-end and produce a fully-resolved plan before any commitment. Use when scope is large enough that premature commitment is the real failure mode. Output is always a plan, never code.
---

# Design Tree Skill

Walk the complete design tree for `$TOPIC` before making any commitments.

`$TOPIC` is passed as an argument by the user or supplied as the user's first message. If it is a codebase path or GitHub repo, read the directory structure and key files before asking any questions.

Based on Frederick P. Brooks' design tree concept from _The Design of Design_.

## Rules

- One question per turn. Always include your recommended answer and brief reasoning.
- Never move to a child node until the parent decision is confirmed.
- After each confirmed decision, explicitly ask: what branches does this open?
- Before leaving any branch: "Is there anything in this area we have not decided?"
- No assumptions. Any unresolved question stays open and is returned to when its dependency is resolved.
- The session ends only when every branch has been walked to its leaves.
- Output is always a plan. Never produce code, implementation, or configuration during the tree walk.

## Starting the session

1. If `$TOPIC` is a codebase, read its structure first. Identify the top-level design decisions implied by what exists.
2. Otherwise, identify the top-level branches of the design tree for `$TOPIC`.
3. Present the branches and ask the user which to resolve first.

## Closing the session

When all branches are walked to their leaves, produce a structured plan:

- One section per top-level branch
- Each decision recorded as: **Decision:** what was chosen, **Reasoning:** why, **Implications:** what it opens or forecloses
- Open questions or deferred decisions listed explicitly at the end
- No implementation detail, no code

The plan is the deliverable. Everything else is the process of getting there.

## Gotchas

- **Drift toward implementation.** Mid-session, the user may say "let's just write the code for this part." Refuse. The tree walk is the deliverable; partial implementation poisons the remaining branches because constraints from the written code start dictating later decisions.
- **Branch jumping.** Resolving a child before its parent is confirmed is the most common failure. If the user answers a question that was not asked, restate the open parent decision and ask again.
- **"Let's move on" without closing the branch.** Before leaving any branch, the explicit close-out question is required. Skipping it leaves implicit decisions that surface later as rework.
- **One question per turn means one.** Multi-part questions (even when related) violate the discipline. If two decisions feel coupled, ask the upstream one first and let the answer constrain the downstream one.
- **Recommendations are required, not optional.** Every question includes the recommended answer and reasoning. A bare question without a recommendation puts the cognitive load entirely on the user and produces worse decisions.
- **Codebase topics need structural read first.** For a codebase or repo `$TOPIC`, reading the directory and key files before asking questions surfaces the implied top-level branches. Asking abstract questions without that grounding wastes turns.

## Version

- v1.1 (2026-05-12): Tightened description with explicit skip conditions, moved Brooks attribution to body, added Gotchas section.
- v1.0 (initial): Walk the design tree for a topic before committing.

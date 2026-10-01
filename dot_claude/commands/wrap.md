---
description: Tear down a finished workstream — branch, refs, tasks, scratch — after verifying the work is safe.
argument-hint: [pr-number]
allowed-tools: Bash, Read, Grep, Glob, TaskList, TaskStop
---

$ARGUMENTS or current branch. Row from `gh pr view --json state` — detect, never ask.

| State | Branch |
|---|---|
| Merged, on base | delete local, prune |
| Merged, not on base | STOP — report |
| Open, fully pushed | delete local, keep remote |
| Open, unpushed | STOP — push first |
| Abandoned, has PR | push, then delete local |
| Abandoned, no PR | show commits, confirm, delete |

*on base* — grep base for a line the PR added; squash breaks ancestry, `git branch -d` lies.
*unpushed* — `git rev-list <branch> --not --remotes --count`

TaskStop anything running.

**Scratch** — remove the dir this workstream owns; delete flat files you created by explicit path, then re-list. Never a glob: shared scratch holds other sessions' work, and a prompt is the gate working.

**Never touch** other worktrees, branches, stashes, anything you did not create — report them.

**Report** SHA, branch, tasks, files by name, what was spared, what is open.

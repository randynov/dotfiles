---
name: pkm
description: Capture, sort, and review Apple Notes via `memo` CLI — Second Brain methodology with classifier prompts and daily nudges. Use for PKM workflows.
---

# PKM (Personal Knowledge Management)

A Claude Code skill that implements the "Second Brain" methodology using Apple Notes via the `memo` CLI.

## Overview

This skill provides AI-powered knowledge management based on 8 building blocks and 12 principles:

**8 Building Blocks:**
1. **Drop Box** - Frictionless capture (`pkm capture`)
2. **Sorter** - AI classification and routing (`pkm sort`)
3. **Form** - Structured templates (`pkm template`)
4. **Filing Cabinet** - Folder-based organization (automatic)
5. **Receipt** - Audit trail (logs at `~/.pkm/log.md`)
6. **Bouncer** - Confidence filtering (built into sort)
7. **Tap on Shoulder** - Daily nudges (`pkm nudge`)
8. **Fix Button** - Easy corrections (`pkm review`)

**12 Principles:**
- One Reliable Human Behavior
- Separate Memory, Compute, and Interface
- Treat Prompts Like APIs
- Build Trust Mechanisms
- Default to Safe Behavior
- Small, Frequent, Actionable Outputs
- Use Next Action as Execution Unit
- Prefer Routing Over Organizing
- Keep Categories Painfully Small
- Design for Restart, Not Perfection
- Build Core Loop, Then Add Modules
- Optimize for Maintainability Over Cleverness

## Prerequisites

- macOS with Apple Notes
- `memo` CLI installed (for Apple Notes access)
- Python 3.8+

## Folder Structure

The skill creates these folders in Apple Notes:

```
Inbox       → Raw captures (#capture tag)
Processing  → AI-sorted items awaiting review
Projects    → Active goals with next actions
Areas       → Domains of responsibility
Resources   → Reference material
Archives    → Completed/dormant items
_System     → Templates and configuration
```

## Commands

### Setup
```bash
python3 ~/.claude/skills/pkm/utils.py
```
Creates folder structure in Apple Notes.

### Capture (Drop Box)
```bash
python3 ~/.claude/skills/pkm/capture.py "My idea about X"
```
Quick capture to Inbox with timestamp and metadata.

### Sort (Sorter)
```bash
python3 ~/.claude/skills/pkm/sorter.py
```
AI classifies Inbox notes and routes to appropriate folders.

### Nudge (Daily Priorities)
```bash
python3 ~/.claude/skills/pkm/nudge.py
```
Generates top 3 priorities from active projects.

### Review (Fix Button)
```bash
python3 ~/.claude/skills/pkm/review.py
```
Interactive review of low-confidence classifications.

## Configuration

Logs are stored at: `~/.pkm/log.md`

## Tags

- `#capture` - Raw inbox item
- `#project` - Multi-step goal
- `#todo` - Single action item
- `#idea` - Concept to explore
- `#meeting` - Meeting notes
- `#waiting` - Waiting on someone else
- `#resource` - Reference material
- `#someday` - Future aspiration

## Skills Activation

This skill auto-loads when you mention:
- "notes", "capture", "inbox"
- "knowledge management", "pkm", "second brain"
- "organize my thoughts", "daily priorities"

## Files

- `SKILL.md` - This file
- `utils.py` - Memo CLI wrapper and logging
- `capture.py` - Quick capture to Inbox
- `sorter.py` - AI classification and routing
- `nudge.py` - Daily priority generator
- `review.py` - Interactive review queue
- `templates.py` - Note templates

## Verification

After setup:
```bash
# 1. Capture a test note
python3 ~/.claude/skills/pkm/capture.py "Test note content"

# 2. Check it appears in Inbox
memo notes -f Inbox

# 3. Sort the inbox
python3 ~/.claude/skills/pkm/sorter.py

# 4. Verify logs
cat ~/.pkm/log.md
```

## Architecture

```
Apple Notes (Memory)
       ↕
  memo CLI (Interface)
       ↕
  pkm skill (Compute)
       ↕
  Claude AI (Intelligence)
```

Follows Principle 2: Separate Memory, Compute, and Interface.

---

**Version**: 1.0
**Last Updated**: 2026-01-25

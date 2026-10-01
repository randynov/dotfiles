# Validation Output Template

Append this to the plan file when the user asks for file updates. Fill in all [bracketed] sections.

```markdown
---

# Validation Results

**Validated:** [YYYY-MM-DD]
**Verdict:** CRITICAL | CAUTION | REASONABLE

## Issues Found

### Critical (Must Address)

- **[Issue]**: [Description]
  - _Impact_: [What breaks]
  - _Mitigation_: [How to fix]
  - _File_: `path/to/file.py:line`

### High Risk (Should Address)

- **[Issue]**: [Description]
  - _Impact_: [Problem]
  - _Recommendation_: [Action]

### Simplification Opportunities

- **[Current approach]** -> **[Simpler alternative]** (tradeoff: [what changes])

## Cross-Model Review (Gemini)

*Tool: gemini CLI | Mode: read-only plan approval | Status: completed|unavailable|timed out*

### Findings

- **[Issue]**: [Description]
  - _Severity_: Critical | High | Medium
  - _Impact_: [What breaks]
  - _File_: `path/to/file.py:line`

### Agreement with Primary Analysis
- [Areas where Gemini independently confirmed the primary findings]

### Novel Findings
- [Issues Gemini found that the primary analysis did not]

> If Gemini was unavailable, replace the above with:
> `*Status: unavailable ([reason]). Validation completed without cross-model review.*`

## Plan Revisions Made

- Changed [section] from [old approach] to [new approach] because [reason]
- Removed [item] because [validation finding]

## Decisions Confirmed

- [x] **[Decision]**: Chose [option] because [reasoning]

## Dependencies Affected

| Component | Impact          | Action Needed  |
| --------- | --------------- | -------------- |
| `file.py` | Breaking change | Update callers |

## Test Implications

- Tests expected to fail: [list]
- Tests needing updates: [list]
- New coverage needed: [list]
```

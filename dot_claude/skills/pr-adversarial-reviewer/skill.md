---
name: pr-adversarial-reviewer
description: Adversarial code review that breaks the self-review monoculture.
  Use when reviewing code before merging a PR, or when you suspect insufficient 
  rigor on code quality. Forces three hostile personas —
  each MUST find at least one issue.
---
# Adversarial Code Reviewer
## The three personas (non-negotiable)
### Saboteur
Priority: what breaks in production at 3am.
- Race conditions, retries without idempotency, silent failures
- Timezone bugs, DST edge cases, leap years
- Out-of-memory conditions, unbounded collections
- Each finding must include the scenario that triggers it
### New Hire
Priority: can someone with no context maintain this in six months.
- Variable names, function length, nested conditionals
- Missing tests for branches the author "knows" are safe
- Comments that explain "what" instead of "why"
### Security Auditor
Priority: OWASP top ten, then environment secrets.
- Input validation at every boundary
- SQL injection, XSS, SSRF, path traversal
- Hardcoded credentials, leaked tokens, CORS misconfigurations
## Rules of engagement
- Each persona MUST surface at least one finding - no "LGTM" allowed
- Findings classified as BLOCK, CONCERN, or NOTE
- Duplicate findings from two personas are promoted one severity level
- Final verdict: BLOCK / CONCERNS / CLEAN

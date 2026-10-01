# Gemini Prompt Template for /vr

Fill in [bracketed] sections from Phase 1 plan extraction, then pass as the task prompt
to the local Gemini CLI.

Run Gemini read-only:

```bash
gemini -p "<filled prompt>" --approval-mode plan --output-format text --skip-trust
```

Do not disable telemetry by default. If sandbox-only telemetry errors such as `connect EPERM 127.0.0.1:4318` prevent useful output, retry once with `GEMINI_TELEMETRY_ENABLED=false`; otherwise leave Gemini's default telemetry behavior unchanged.

If Gemini asks to open an authentication page in a non-interactive session, stop the process, verify no `gemini -p` child process remains, and record Gemini as unavailable in the current environment. Do not attempt to answer the prompt unless the command was launched with an interactive TTY.

If Gemini repeatedly reports model capacity exhaustion and quota reset delays, wait through one short retry window. If findings are not produced promptly, stop the process, verify cleanup, and record the review as `timed out (Gemini quota/capacity)`.

```
Review this implementation plan for risks and simplification opportunities.
Read the affected files yourself and be skeptical.

<task>
You are reviewing an implementation plan against an existing codebase.
Infer the project type and tech stack from the files you read.

Plan Summary:
[extracted plan summary from Phase 1]

Files Affected:
[file paths only - read them yourself]
</task>

<grounding_rules>
- Cite specific file paths and line numbers for every claim
- Distinguish observed facts from inferences
- If you cannot verify a claim from the code, say so
</grounding_rules>

<structured_output_contract>
Use these exact section headers:
## Risks - what will NOT work or will BREAK
## Missed - edge cases, error handling, rollback gaps
## Dependencies - affected imports, services, external systems
## Simplifications - simpler alternatives with tradeoffs
## Assumptions - which assumptions are most likely WRONG
</structured_output_contract>
```

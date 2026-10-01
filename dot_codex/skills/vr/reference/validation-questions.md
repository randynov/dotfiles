# Validation Questions

For each part of the plan, systematically answer:

| Question                               | Focus Area                                          |
| -------------------------------------- | --------------------------------------------------- |
| **Why will this NOT work?**            | Fundamental flaws, incorrect assumptions            |
| **What will BREAK?**                   | Existing functionality, APIs, contracts             |
| **What was MISSED?**                   | Edge cases, error handling, rollback                |
| **What DEPENDENCIES are affected?**    | Imports, services, external systems                 |
| **What TESTS will fail?**              | Unit, integration, e2e implications                 |
| **What EDGE CASES weren't addressed?** | Null, empty, concurrent, large scale                |
| **Is there a SIMPLER way?**            | Existing utilities, framework features, fewer files |
| **What DECISIONS need input?**         | Ambiguous requirements, multiple valid approaches   |

## Deep Validation Checklist

- [ ] API contracts preserved (or migration planned)
- [ ] Database schema changes have migrations
- [ ] Authentication/authorization implications
- [ ] Error handling for new failure modes
- [ ] Logging and observability (no sensitive data exposed)
- [ ] Performance implications at scale
- [ ] Rollback strategy if deployment fails
- [ ] Feature flag or gradual rollout needed
- [ ] Documentation updates required
- [ ] Test coverage for new code paths
- [ ] Version compatibility with dependencies
- [ ] No hardcoded values that should be configurable

## Validation Mindset

Be the devil's advocate:

- Assume the plan has flaws
- Look for hidden dependencies the author forgot
- Consider race conditions and concurrency
- Check for breaking changes in public APIs
- Verify backward compatibility
- Consider what happens if deployment fails mid-way
- Think about monitoring and alerting gaps
- Question optimistic assumptions
- Find ways to more effectively leverage existing frameworks and packages

The goal is to surface concerns early, not to block progress.

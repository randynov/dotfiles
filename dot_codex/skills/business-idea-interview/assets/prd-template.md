# PRD Template

Delete instruction text in italics before sharing a completed PRD.

## Rules

- One PRD per feature. If describing it requires an "and," write separate PRDs.
- Use non-technical framing. Include implementation details only when they change product behavior or a reader's decision.
- Do not include effort or timeline estimates.
- Prefer a concrete example to an abstraction.
- Use consistent plain-language terms. Define unfamiliar terms on first use.
- Do not write notes about the document itself.
- Omit optional sections when they do not apply. Never leave an empty section.

---

# PRD: [Area] | [Feature]

*In one or two sentences, explain what this is and who it is for.*

| Impact | Value |
| :---- | :---- |
| [What changes] | [Value] |
| [What does not change] | [Value] |

*This table shows blast radius, not a summary. Choose rows that change what a reader does, such as affected users, data handling, billing, permissions, compliance, integrations, or operations. Every row must be a checkable fact.*

## Links

*Optional. Include when the work is tracked.*

- Issue:
- Project tracker:
- Pull request:
- Other:

## The problem

*Explain what is true today and what it costs. Use bullets or short prose, whichever reads faster.*

## What we want

*Describe the outcome in plain language for a reader who will never open the code. Detailed behavior belongs below.*

## What we are deliberately not doing

*List each non-goal with its reason. A non-goal without a reason tends to be reconsidered later.*

## Who needs what

*Describe the need by audience. "No changes" is a useful answer for an audience this feature does not affect.*

## What the system should do

*Number each behavior. Make every line testable by someone who cannot see the code. Use subheadings when a behavior needs more than one line.*

1.
2.
3.

## Existing services and custom work

*Optional. Include when the feature depends on external products or requires a buy-versus-build decision.*

| Capability | Provided by | Why | Data or handoff | Known constraint |
| :---- | :---- | :---- | :---- | :---- |
|  |  |  |  |  |

*Include expected monthly cost at initial usage and at ten times that usage when the information is available. State whether data can be exported and what changes if a vendor changes terms.*

## User-facing messages

*Optional. Include when the feature adds or changes anything a user receives.*

*Put every new or changed message in one place, in the format used for delivery, so it can be reviewed, translated, and tested. Mark draft copy as illustrative when another party must approve it.*

```yaml
message_key: [key]
audience: [audience]
channel: [screen, email, text, push, or other]
text: "[Text]"
actions:
  - "[Action]"
```

## Settings

*Optional. Include when the feature adds or changes a setting.*

| Setting | Scope | Default | Set by | Where |
| :---- | :---- | :---- | :---- | :---- |
|  |  |  |  |  |

*Use the scopes that fit the product, such as platform, organization, team, account, or user.*

## Acceptance

*Use one row per behavior that needs a non-obvious check.*

| What we check | Expected | How |
| :---- | :---- | :---- |
|  |  |  |

## Success measures

*Optional. Include when there is an outcome to move. Acceptance asks whether the feature was built. Success measures ask whether it worked. Do not invent a metric when none is useful.*

## Open questions

*Optional. Include only questions that cannot be answered from available evidence or by asking the requester. State what each answer would change.*

## Future enhancements

*List deliberately deferred work and the reason for each deferral.*

## References

*Include relevant files, issues, pull requests, research, plans, or tests. State what each reference gives the reader.*

-

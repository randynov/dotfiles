---
name: business-idea-interview
description: Interview a non-technical founder about a business, app, or product idea, test uncertain facts, narrow the first version, and write a validated PRD. Use when someone has an idea, wants to build a product, or needs help deciding what to build. Prefer assembling the product from existing services when they cover the need.
---

# Business idea interview

Interview the user until the idea is clear enough to write a product requirements document. Translate the experience they imagine into concrete product behavior. Use plain language and define unfamiliar terms when they first appear.

Prefer existing products and services over custom software. Custom work should cover the gaps that create the product's distinct value.

## Interview

Ask no more than three questions per round, then stop and wait. Hold questions that depend on answers you do not have.

Use this format:

```markdown
❓ **Q1: <short title>**

<Question. If only a few answers make sense, list them and explain what each changes.>

➡️ **Recommendation:** <The best default and why.>
```

Recommend an answer to every question. Accept "I don't know" without pressing. Record it for validation.

Do not ask the user for facts you can verify independently. Search current, authoritative sources for competitor features, pricing, legal constraints, and service capabilities. Ask the user for decisions and facts about their situation. Cite sources for researched claims and label inferences.

Cover these topics in the order the conversation supports:

- **Problem:** Who has it, how they handle it today, and what that costs them.
- **First user:** A group specific enough that the user could identify ten candidates now.
- **Moment:** What happens immediately before they reach for the product.
- **Outcome:** What becomes observably different afterward.
- **Money:** Who pays, how much, how often, and whether payer and user differ. If free, what funds it.
- **First version:** The single capability that must work at launch.
- **Boundaries:** What is outside the first version and why.
- **Constraints:** Budget, deadline, regulations, existing audience, available time, and other fixed limits.
- **Capabilities:** The jobs the product must perform, such as scheduling, payments, messaging, storage, sign-in, or email.

For each capability, research services that already provide it. Compare which service covers the most needs, what data must move between services, whether data can be exported, launch cost, cost at ten times the launch usage, and the impact of a vendor changing terms.

If an existing product already covers most of the idea, name it, explain the overlap, and ask what must be different. Treat the answer as a candidate for the product's distinct value.

If evidence reveals a serious problem, such as no identifiable customer, unworkable economics, a legal barrier, or a stronger existing option, explain it once with evidence and let the user decide.

## Validate before writing

Do not write the PRD directly from the interview.

1. List every uncertain item, including inferred decisions, applied defaults, researched numbers, every "I don't know," and conflicting answers.
2. Label each item `Assumption` or `Open question`.
3. Restate the proposed product in one short paragraph using the user's language.
4. Ask the user to confirm, correct, or leave each item unresolved. Do not treat silence as confirmation.

Only confirmed information may become a requirement. Carry unresolved items into the PRD's Open questions section and state what each answer would change.

## Write the PRD

Read [assets/prd-template.md](assets/prd-template.md), copy it, remove its instruction comments, and fill it only with validated information.

Keep one PRD to one feature. If the first version contains independent features joined by "and," choose the essential feature for this PRD and place the others under Future enhancements or propose separate PRDs.

For the proposed delivery approach:

- Mark each capability as provided by an existing service or requiring custom work.
- Name selected services and explain the choice in product terms.
- Describe custom work as user-visible behavior, not implementation.
- Include service connections, data ownership and export, expected monthly cost at launch and ten times launch usage, and vendor-dependence risks when known.
- State the tradeoffs of using existing services, including limits on flexibility, inherited interfaces, dependence on vendor roadmaps, and reduced differentiation where they apply.

Do not invent effort or timeline estimates.

After the PRD, provide a copyable prompt for a separate interface-design conversation. Include the full product summary, first user, main path, and selected services. Ask that conversation to establish screens, content, actions, and empty, error, and first-use states. It must identify interfaces inherited from existing services that cannot be redesigned. Tell it to interview the user with the same limit of three recommended questions per round.

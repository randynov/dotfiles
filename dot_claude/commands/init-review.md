---
description: Review and improve CLAUDE.md files based on Anthropic's best practices for effective project documentation
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(find:*), Bash(ls:*), Bash(wc:*), Bash(head:*), Bash(tail:*)
argument-hint: [path-to-claude-md]
---

# CLAUDE.md Review & Improvement

Review and improve CLAUDE.md files following Anthropic's best practices for effective project documentation.

**IMPORTANT:** CLAUDE.md is guidance for Claude Code when WRITING CODE, not comprehensive project documentation.

## Context

### Documentation Discovery
!`find . -maxdepth 2 -name "*.md" -type f 2>/dev/null | grep -v node_modules | head -20`

### Root-Level Docs
!`ls -la *.md 2>/dev/null | head -10`

### CLAUDE.md Stats
!`wc -l CLAUDE.md .claude/CLAUDE.md 2>/dev/null || echo "No CLAUDE.md found"`

### Project Type Detection
!`ls package.json pyproject.toml Cargo.toml go.mod pom.xml 2>/dev/null | head -5`

## Key Files

@CLAUDE.md
@README.md
@CONTRIBUTING.md
@DEPLOYMENT.md

---

## Phase 1: Analysis & Documentation Review

### Understand the CLAUDE.md

Analyze the provided CLAUDE.md to understand:
- What is this file trying to accomplish?
- What are the main goals and intended use cases?
- What type of project is this for?
- Are there unclear, ambiguous, or confusing sections?

### Review Existing Documentation

**BEFORE proceeding to Phase 2:**

1. **Review ALL existing documentation files** found in discovery
2. **Identify what information is ALREADY documented elsewhere**
3. **Quickly review the code structure** to understand how it works

### Documentation Architecture Check

Map existing documentation coverage:

| File | Exists | Coverage |
|------|--------|----------|
| README.md | ? | Project overview, setup, usage |
| CONTRIBUTING.md | ? | Contribution guidelines |
| DEPLOYMENT.md | ? | Deployment/operations |
| TESTING.md | ? | Testing procedures |
| CHECKLIST.md | ? | QA checklists |
| Other *.md | ? | Additional docs |

### Key Litmus Test

> "Would this information help Claude Code WRITE CODE, or is it operational/end-user documentation?"

If anything is unclear, ask specific questions about:
- The project's purpose and architecture
- Development workflow and team practices
- Specific technical decisions or conventions
- Any ambiguous instructions or guidelines

---

## Phase 2: Evaluation Against Best Practices

### SHOULD Include

#### Code Style & Standards (for writing code)
- Specific formatting rules (e.g., "Use 2-space indentation", "camelCase vs snake_case")
- Naming conventions for variables, functions, classes, files, directories
- Language-specific patterns and idioms
- File organization preferences and structure requirements
- Code commenting standards and documentation expectations

#### Project-Specific Context (for writing code)
- Architecture patterns and design principles (MVC, microservices, etc.)
- Common development commands (`npm run dev`, `npm test`, `npm run lint`)
- Technology stack, frameworks, and key dependencies
- Important file/directory locations and their purposes
- Development environment setup (NOT production deployment)
- Code organization patterns specific to this project

#### Development Workflow (developer actions during coding)
- Git workflow and branching strategy (GitFlow, trunk-based, etc.)
- Testing requirements and conventions (HOW to write tests, not QA checklists)
- Code review criteria (what makes code ready for review)
- Deployment commands that DEVELOPERS run (`npm run build`, etc.)
- Dependency management patterns (when to add deps, how to update)

**Note:** Focus on developer actions during coding, not operations/DevOps procedures.

#### Security & Compliance (as it affects code)
- Security policies and specific requirements
- Data handling guidelines and privacy considerations
- Compliance requirements (GDPR, HIPAA, PCI, etc.)
- Access control patterns and authentication/authorization rules
- Audit logging and monitoring requirements

---

### SHOULD NOT Include

#### Secrets & Credentials
- API keys, tokens, passwords, or authentication secrets
- Database connection strings with credentials
- Private URLs, endpoints, or internal service addresses
- Personal access tokens or SSH keys

#### Overly Generic Instructions
- Vague statements like "write good code" or "follow best practices"
- Obvious best practices without project-specific context
- Redundant information already covered in other documentation
- Subjective quality statements without measurable criteria

#### Excessive Detail
- Complete API documentation (link to external docs instead)
- Large code examples (use separate example files)
- Verbose explanations that reduce scannability
- **Duplicate information from README or other project docs** - CHECK EXISTING DOCS FIRST

#### Content That Belongs Elsewhere

| Content Type | Belongs In |
|--------------|------------|
| Browser compatibility | README.md |
| Deployment troubleshooting | DEPLOYMENT.md |
| QA test plans | TESTING.md or CHECKLIST.md |
| Performance optimization | DEPLOYMENT.md or PERFORMANCE.md |
| End-user guides | README.md or user docs |

#### Temporary Information
- Personal sandbox URLs or development environments
- One-off task instructions or temporary workarounds
- Debugging notes or incident post-mortems
- Personal preferences that aren't team standards

---

## Phase 3: Specific Feedback

Based on the evaluation, provide specific, actionable feedback:

### 1. What's Working Well
Highlight sections that follow best practices effectively, explaining why they work well.

### 2. What's Missing
Identify important categories from "SHOULD Include" that are absent or underdeveloped.

### 3. What Should Be Removed
Point out items from "SHOULD NOT Include" that are present.
Recommend alternatives (e.g., "Move browser compatibility to README.md").

### 4. Organization Improvements
Suggest better structure, formatting, or information hierarchy.

### 5. Specific Additions
Recommend concrete, actionable guidelines to add.
Not generic suggestions—specific examples tailored to this project.

### 6. Revised Version
Provide an improved version of the CLAUDE.md with clear explanations for each change.

---

## Critical Behavioral Instructions

### Check Existing Documentation First

Before recommending ANY new sections for CLAUDE.md:

1. Verify the information isn't already in README, DEPLOYMENT, or other docs
2. Ask: "Does Claude Code need this to WRITE/MODIFY code effectively?"
3. If the answer is "this helps users RUN/DEPLOY the app" - it belongs elsewhere

### CLAUDE.MD IS NOT

| Not This | Put Here Instead |
|----------|-------------------|
| Comprehensive project guide | README.md |
| End-user documentation | README.md or /docs |
| Deployment/operations manual | DEPLOYMENT.md |
| QA testing procedures | TESTING.md |
| Troubleshooting guide for users | README.md |
| Browser compatibility reference | README.md |
| Performance optimization guide | PERFORMANCE.md |

### CLAUDE.MD IS

- Code style guidance specific to this project
- Architecture patterns for developers
- "How to add X feature" patterns
- "Don't do Y when coding" anti-patterns, with alternatives
- Project-specific conventions that affect code changes
- State management patterns
- Common code patterns with examples

---

## Decision Framework

### The Litmus Test

> **"Would a developer need to know this to make a code change?"**

| Answer | Action |
|--------|--------|
| Yes | Keep in CLAUDE.md |
| No | Move to appropriate doc |
| Unsure | Ask clarifying question |

### Length Guidelines

| Project Type | Recommended Lines |
|--------------|-------------------|
| Solo/prototype | 50-75 |
| Small team MVP | 100-150 |
| Medium team | 150-250 |
| Large/enterprise | 200-300+ (consider modular) |

### Modular Architecture (for large projects)

Consider splitting into:
- `CLAUDE.md` (root) - Navigation hub, <100 lines
- `backend/CLAUDE.md` - API and database guidelines
- `frontend/CLAUDE.md` - Component standards
- `.github/CLAUDE.md` - CI/CD workflows

---

## Success Criteria

- [ ] All existing documentation reviewed for duplicates
- [ ] SHOULD Include categories evaluated
- [ ] SHOULD NOT Include items identified
- [ ] Specific, actionable feedback provided
- [ ] Revised version includes explanations
- [ ] Length appropriate for project size
- [ ] No secrets or credentials present
- [ ] Focus on code-writing guidance maintained

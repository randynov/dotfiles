---
name: c4-diagrams
description: Creates and manages C4 architecture diagrams using PlantUML. Use when the user wants to visualize software architecture, create context/container/component/sequence diagrams, document system design with the C4 model, or mentions architecture diagrams, system design, or PlantUML. Supports iterative diagram building through conversational workflow.
license: Complete terms in LICENSE.txt
---

# C4 Architecture Diagrams

This skill helps you create and manage C4 architecture diagrams using the PlantUML format. C4 diagrams provide a hierarchical way to visualize software architecture at different levels of detail, from high-level system context down to low-level components.

The C4 model uses four diagram types:

- **Context**: Shows the system in its environment with external actors and systems
- **Container**: Zooms into the system to show high-level technical building blocks
- **Component**: Zooms into a container to show its internal structure
- **Sequence**: Shows how elements interact with each other over time

All diagrams are stored as `.puml` files in `docs/diagrams/` and rendered to PNG images using the public PlantUML server.

## Requirements

Before using this skill, ensure you have:

- **Bash** - For directory setup (available on Linux, macOS, WSL)
- **Python 3.6+** - For diagram rendering (uses standard library only, no pip install needed)
- **Internet access** - To reach the public PlantUML server (https://www.plantuml.com/plantuml/)
- **File system write permissions** - In your project's working directory

**Note:** This skill uses only standard library dependencies. No package managers or external installations required beyond Python itself.

## High-Level Workflow

Creating C4 diagrams follows a five-phase workflow:

1. **Initialize Directory Structure** - Set up `docs/diagrams/` with subdirectories for each diagram type
2. **Choose Diagram Type & Create File** - Select appropriate diagram type and initialize from template
3. **Add Elements** - Define the entities in your diagram (people, systems, containers, components)
4. **Define Relationships** - Connect elements with labeled relationships
5. **Render Diagram** - Generate PNG image from PlantUML source

Each phase includes validation steps to ensure correctness before proceeding to the next phase.

---

## Phase 1: Initialize Directory Structure

### 1.1 Check for Existing Structure

**Before creating diagrams**, verify that the directory structure exists:

Use the Bash tool to check:

```bash
ls -la docs/diagrams 2>/dev/null
```

If the output shows subdirectories `context/`, `container/`, `component/`, and `sequence/`, proceed to Phase 2.

### 1.2 Create Directory Structure

**If the structure doesn't exist**, run the initialization script:

```bash
bash ~/.claude/skills/c4-diagrams/scripts/init-structure.sh
```

**Expected behavior:**

- Creates `docs/diagrams/` at project root if missing
- Creates four subdirectories:
  - `docs/diagrams/context/` - For context-level diagrams
  - `docs/diagrams/container/` - For container-level diagrams
  - `docs/diagrams/component/` - For component-level diagrams
  - `docs/diagrams/sequence/` - For sequence diagrams
- Reports what was created or verified
- Idempotent: safe to run multiple times

### 1.3 Verify Success

**After running the script**, confirm the structure was created:

```bash
ls -R docs/diagrams
```

You should see all four subdirectories.

**Error handling:**

- If the script fails with a permission error, ensure you have write permissions in the project directory
- If you're in the wrong directory, navigate to the project root first
- The script will provide specific error messages to guide troubleshooting

---

## References

Phases 2-5 and common pitfalls are documented in dedicated reference files:

- `references/diagram-types.md` — Phase 2: Choose diagram type & create file (context/container/component/sequence guidance, file creation from template)
- `references/elements.md` — Phase 3: Add elements (naming rules, element types by diagram, syntax, validation)
- `references/relationships.md` — Phase 4: Define relationships (Rel syntax, directional variants, sequence diagram dividers/groups, validation)
- `references/rendering.md` — Phase 5: Render diagram (PNG generation, error handling, iteration paths)
- `references/pitfalls.md` — Common syntax pitfalls + cross-references to deeper reference docs (C4 model, syntax, best practices, C4-PlantUML library)

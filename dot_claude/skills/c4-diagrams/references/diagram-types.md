## Phase 2: Choose Diagram Type & Create File

### 2.1 Understand Diagram Types

Choose the appropriate diagram type based on what you want to visualize:

**Context Diagrams** (`context/`)

- **Purpose**: Show the system in its environment
- **Elements**: People, systems, external systems
- **Use when**: Explaining what the system does and who uses it
- **Audience**: Everyone (technical and non-technical)

**Container Diagrams** (`container/`)

- **Purpose**: Show high-level technical building blocks
- **Elements**: Web apps, mobile apps, databases, microservices
- **Use when**: Explaining the system's runtime architecture
- **Audience**: Technical stakeholders (developers, architects)

**Component Diagrams** (`component/`)

- **Purpose**: Show components within a container
- **Elements**: Controllers, services, repositories, modules
- **Use when**: Explaining internal structure of a specific container
- **Audience**: Developers working on the system

**Sequence Diagrams** (`sequence/`)

- **Purpose**: Show interactions between elements over time
- **Elements**: Any of the above, with time-ordered relationships
- **Use when**: Explaining workflows, processes, or API call chains
- **Audience**: Developers and architects
- **⚠️ Important constraints**:
  - ❌ **NO boundaries** - Container_Boundary, System_Boundary are not supported
  - ❌ **NO \_Ext suffixes** - Use Container(), not Container_Ext()
  - ✅ Participants must be in a **flat list** (no nesting or grouping structures)
  - ✅ Relationships are **time-ordered** from top to bottom

**For detailed guidance on when to use each type**, see [Diagram Types Guide](./diagram-types.md).

### 2.2 Check if Diagram Already Exists

**Before creating a new diagram**, check if it already exists:

Determine the diagram name (convert to lowercase, replace spaces with hyphens):

- User says: "Create a system context diagram" → name: `system-context`
- User says: "Web application container diagram" → name: `web-application`

Check for existing file:

```bash
ls docs/diagrams/{type}/{name}.puml 2>/dev/null
```

**If the file exists:**

- Read the file using the Read tool to understand its current state
- Skip to Phase 3 or Phase 4 to modify it

**If the file doesn't exist:**

- Continue to create a new diagram

### 2.3 Initialize New Diagram from Template

**To create a new diagram**, read the appropriate template and write it to the target location:

1. Read the template:

   ```
   Read ~/.claude/skills/c4-diagrams/templates/{type}.puml
   ```

   Where `{type}` is one of: `context`, `container`, `component`, `sequence`

2. Optionally customize the template:
   - Replace title placeholder with user-specified title
   - Add initial comments or notes
   - Keep all C4-PlantUML directives intact

3. Write to target location:
   ```
   Write docs/diagrams/{type}/{name}.puml
   ```

**Validation:**

- Verify the file was created: `ls docs/diagrams/{type}/{name}.puml`
- Briefly read the file to confirm contents
- Proceed to Phase 3

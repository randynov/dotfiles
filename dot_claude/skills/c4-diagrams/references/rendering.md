## Phase 5: Render Diagram

### 5.1 Generate PNG from PUML

**To render the diagram**, run the rendering script:

```bash
python3 ~/.claude/skills/c4-diagrams/scripts/render-diagram.py docs/diagrams/{type}/{name}.puml
```

**Example:**

```bash
python3 ~/.claude/skills/c4-diagrams/scripts/render-diagram.py docs/diagrams/context/system-context.puml
```

**Expected behavior:**

- Reads the PUML file
- Encodes content for PlantUML server
- POSTs to https://www.plantuml.com/plantuml/
- Saves PNG response to same directory with same name
- Example: `docs/diagrams/context/system-context.png`

### 5.2 Verify Output

**After rendering**, confirm the PNG was created:

```bash
ls -lh docs/diagrams/{type}/{name}.png
```

**The script includes:**

- **Retry logic**: Attempts up to 3 times with exponential backoff (1s, 2s, 4s delays)
- **Timeout handling**: 15 second timeout per request
- **Clear error messages**: Specific errors for network, syntax, and server issues

### 5.3 Error Handling

**If rendering fails**, the script will provide specific error messages:

**Network errors:**

- Connection issues or timeouts
- Check internet connectivity
- Try again after a few moments

**HTTP 400 errors:**

- Invalid PlantUML syntax in the PUML file
- Read the file and check for syntax errors
- Common issues: unclosed boundaries, missing quotes, invalid IDs
- Manually validate at https://www.plantuml.com/plantuml/uml/

**HTTP 429 errors:**

- Rate limited by server
- Wait a minute before retrying
- Consider reducing render frequency

**HTTP 5xx errors:**

- PlantUML server issues
- Try again later
- Server typically recovers quickly

### 5.4 Next Steps

**After successful rendering:**

**Option 1: Iterate on the diagram**

- View the generated PNG
- If changes needed, return to Phase 3 or 4
- Edit elements or relationships
- Re-render (return to Phase 5.1)

**Option 2: Create additional diagrams**

- Return to Phase 2 to create a new diagram
- Consider creating diagrams at different levels:
  - Start with Context (big picture)
  - Add Container (technical structure)
  - Add Component (internal details)
  - Add Sequence (workflows)

**Option 3: Explore advanced features**

- Load [Best Practices Guide](./best-practices.md) for design tips
- Load [C4 Model Concepts](./c4-model.md) to understand deeper principles
- Load [C4-PlantUML Library Docs](./c4-plantuml-readme.md) for advanced syntax

## Phase 4: Define Relationships

### 4.1 Parse Existing Elements and Relationships

**Before adding relationships**, read the diagram to identify:

1. All defined elements and their IDs
2. Existing relationships (to avoid duplicates)
3. Logical connections that need to be added

### 4.2 Determine Relationships to Add

**Based on the user's request and diagram logic**, identify which elements should be connected:

**Relationship syntax:**

```plantuml
Rel(source_id, target_id, "Description")
Rel(source_id, target_id, "Description", "Technology/Protocol")
```

**Directional variants** (optional, for layout control):

- `Rel_U` - Relationship pointing up
- `Rel_D` - Relationship pointing down
- `Rel_L` - Relationship pointing left
- `Rel_R` - Relationship pointing right

**Examples:**

```plantuml
Rel(user, web_app, "Uses", "HTTPS")
Rel(web_app, api, "Makes API calls", "REST/JSON")
Rel(api, database, "Reads/writes", "JDBC")
Rel(main_system, payment_gateway, "Processes payments", "API")
```

### 4.3 Add Relationship Definitions

**To add relationships**, use the Edit tool to insert them after the element definitions:

**Best practices:**

- Add relationships in a dedicated section (after all elements)
- Group related relationships together
- Use descriptive labels that explain the interaction
- Include technology/protocol information when relevant

**For sequence diagrams:**

- Relationships are time-ordered (top to bottom)
- Use dividers to group logical steps: `== Step Name ==`
- Consider using `group` blocks for sub-processes:
  ```plantuml
  == Authentication ==
  group Login Process
    Rel(user, api, "Submits credentials")
    Rel(api, database, "Verifies user")
  end
  ```

### 4.4 Validate Relationships

**After adding relationships**, verify correctness:

1. Confirm both source and target IDs exist in the diagram
2. Check that relationship directions make logical sense
3. Ensure descriptions are clear and meaningful
4. Verify technology/protocol parameters are accurate
5. For sequence diagrams, confirm ordering is correct

**If validation fails:**

- Fix ID mismatches
- Correct syntax errors
- Adjust descriptions for clarity
- Re-read the file to verify fixes

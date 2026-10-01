## Common Pitfalls

❌ **Don't** use hyphens in element IDs → ✅ **Do** use underscores:

```plantuml
System(web-app, "Web App", "Desc")      // WRONG
System(web_app, "Web App", "Desc")      // CORRECT
```

❌ **Don't** omit technology for containers/components → ✅ **Do** always include it:

```plantuml
Container(api, "API Server", "Handles logic")               // WRONG
Container(api, "API Server", "Node.js", "Handles logic")    // CORRECT
```

❌ **Don't** forget closing braces → ✅ **Do** always close boundaries:

```plantuml
System_Boundary(backend, "Backend") {
  Container(api, "API", "Node.js", "Server")
// WRONG - missing }
}  // CORRECT
```

❌ **Don't** reference undefined IDs → ✅ **Do** ensure all IDs are defined:

```plantuml
Rel(user, app, "Uses")  // WRONG if 'user' not defined first
```

❌ **Don't** use boundaries in sequence diagrams → ✅ **Do** use flat participant lists:

```plantuml
' WRONG - sequence diagrams don't support boundaries
Container_Boundary(backend, "Backend") {
  Container(api, "API", "Node.js", "Server")
}

' CORRECT - flat list of participants
Container(api, "API", "Node.js", "Server")
```

❌ **Don't** use \_Ext suffixes in sequence diagrams → ✅ **Do** use regular variants:

```plantuml
Container_Ext(cache, "Cache", "Redis", "Cache")     // WRONG in sequence
Container(cache, "Cache", "Redis", "Cache")          // CORRECT
```

⚠️ **Important:** Place diagrams in correct subdirectories (`docs/diagrams/context/`, `container/`, `component/`, `sequence/`)

⚠️ **Important:** Validate PUML syntax before rendering to avoid errors and server requests

⚠️ **Important:** Sequence diagrams have unique syntax constraints - see template and syntax reference

---

## Reference Documentation

Load these on-demand for deeper information:

- **[C4 Model Concepts](./c4-model.md)** - Theory, principles, and abstraction levels
- **[Diagram Types Guide](./diagram-types.md)** - When to use each type, examples, audience considerations
- **[Syntax Reference](./syntax-reference.md)** - Complete macro reference, ID rules, boundaries, relationships
- **[Best Practices](./best-practices.md)** - Design patterns, layout, naming, anti-patterns
- **[C4-PlantUML Library Documentation](./c4-plantuml-readme.md)** - Complete upstream docs, advanced features, customization

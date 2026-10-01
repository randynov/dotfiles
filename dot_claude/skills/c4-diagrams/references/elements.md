## Phase 3: Add Elements

### 3.1 Parse Current Diagram State

**Before adding elements**, read the diagram file to understand what's already there:

```
Read docs/diagrams/{type}/{name}.puml
```

**Identify:**

- Existing elements (Person, System, Container, Component)
- Any boundaries or groupings
- Current layout and organization

### 3.2 Determine Elements to Add

**Based on the user's request**, identify what elements need to be added:

> **⚠️ CRITICAL — Name Elements After Their Identifying Term**
>
> When the prompt names a specific technology, product, or role, the element's **Name parameter MUST include that identifying term**:
>
> - ✅ `ContainerDb(redis_cache, "Redis Cache", "Redis", "Caches sessions")` — name contains "Redis"
> - ❌ `ContainerDb(session_cache, "Session Cache", "Redis", "Caches sessions")` — name omits "Redis"
> - ✅ `System_Ext(payment_processor, "Payment Processor", "Handles payments via Stripe")` — name contains "Payment"
> - ❌ `System_Ext(stripe, "Stripe", "Handles payments")` — name omits category keyword "Payment"
> - ✅ `Person(user, "User", "A user of the system")` — matches role term in prompt
> - ❌ `Person(user, "Customer", "A user of the system")` — wrong term if prompt says "User"
>
> Apply this to **every element**: if the prompt says "Elasticsearch for search", the name is "Search Index (Elasticsearch)" or just "Elasticsearch". If it says "Redis for caching", use "Redis Cache". Match the term the prompt uses to identify the element.

**Common element types by diagram:**

**Context diagrams:**

- `Person(id, "Name", "Description")` - Users and actors
- `System(id, "Name", "Description")` - Your system
- `System_Ext(id, "Name", "Description")` - External systems

**Container diagrams:**

- `Container(id, "Name", "Technology", "Description")` - Apps, services, databases
- `ContainerDb(id, "Name", "Technology", "Description")` - Databases specifically
- `ContainerQueue(id, "Name", "Technology", "Description")` - Message queues

**Component diagrams:**

- `Component(id, "Name", "Technology", "Description")` - Components within a container
- `ComponentDb(id, "Name", "Technology", "Description")` - Database components
- `ComponentQueue(id, "Name", "Technology", "Description")` - Queue components

**Sequence diagrams:**

- Use the same element types as above (Person, Container, Component, etc.)
- ⚠️ **CRITICAL**: Do NOT use boundaries (System_Boundary, Container_Boundary) - sequence diagrams require a **flat participant list**
- ⚠️ **CRITICAL**: Do NOT use \_Ext suffixes (System_Ext, Container_Ext, ContainerDb_Ext) - use regular variants instead
- Example: Use `Container(cache, "Cache", "Redis", "Desc")` not `Container_Ext(...)`

**Boundaries** (Context/Container/Component diagrams only - NOT sequence):

```
System_Boundary(id, "Name", "Optional Description") {
  // Elements inside the boundary (indented with 2 spaces)
}
```

**For complete syntax reference**, see [Syntax Reference](./syntax-reference.md).

### 3.3 Add Element Definitions

**To add elements**, use the Edit tool to insert element definitions at the appropriate location:

**Important syntax rules:**

- **IDs must be valid identifiers**: Use letters, numbers, underscores only
- **Sanitize IDs**: Replace hyphens and special characters with underscores
  - Example: "web-app" → "web_app"
  - Example: "API Gateway" → "API_Gateway"
- **Technology parameter**: Required for Container and Component elements (3rd parameter)
- **Quote all strings**: Names, technologies, and descriptions must be in quotes

**Example additions:**

For a context diagram:

```plantuml
Person(user, "User", "A customer using the system")
System(main_system, "Main System", "The core application")
System_Ext(payment_gateway, "Payment Gateway", "External payment processor")
```

For a container diagram:

```plantuml
Container(web_app, "Web Application", "React", "Provides UI for users")
ContainerDb(database, "Database", "PostgreSQL", "Stores application data")
Container(api, "API Server", "Node.js/Express", "Handles business logic")
```

### 3.4 Validate Element Additions

**After adding elements**, verify correctness:

1. Read the edited file to confirm changes
2. Check for syntax errors:
   - Unclosed parentheses
   - Missing quotes
   - Invalid IDs (hyphens, spaces, special characters)
   - Missing technology parameter for containers/components
3. Ensure all elements have proper types, names, and descriptions
4. Fix any errors before proceeding to Phase 4

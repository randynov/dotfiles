---
name: docs-generator
description: Generate or update repo documentation — README sections, API reference docs, code-derived doc pages, doc-site scaffolding. Use when the user says 'document this', 'generate docs', 'update README', 'create API docs', 'write a doc-site', or asks for documentation of a function/module/feature. Picks the right template, fills it from the code, and produces a writeable file.
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

# Documentation Generator

## When to Use

Activate this skill when:
- User requests to "document this code" or "generate documentation"
- User says "update README" or "create README"
- User mentions "API docs" or "API reference"
- User asks to "add JSDoc" or "add comments"
- User wants to "document functions" or "document components"
- User requests "usage examples" or "code examples"
- User says "create documentation" or "write docs"
- New features need documentation
- User mentions "docstrings", "typedoc", or "jsdoc"

## Instructions

### Step 1: Identify Documentation Type

Determine what needs documentation:

1. **Code Documentation**: JSDoc/TSDoc comments in source files
2. **README**: Project overview, setup, usage
3. **API Reference**: Function/class documentation
4. **Component Docs**: React/Vue component props and usage
5. **Architecture Docs**: System design, data flow
6. **Tutorial/Guide**: Step-by-step instructions

### Step 2: Analyze Code to Document

1. Find files needing documentation:
```bash
# Find all source files
find src -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) \
  -not -path "*/node_modules/*"
```

2. Read and analyze code:
   - Function signatures
   - Parameters and return types
   - Component props
   - Class methods
   - Exported APIs

3. Identify existing documentation:
```bash
# Check for existing docs
ls -la README.md docs/ CONTRIBUTING.md API.md 2>/dev/null
```

### Step 3: Generate Appropriate Documentation

#### For Functions (JSDoc/TSDoc):

```typescript
/**
 * Calculates the sum of two numbers
 *
 * @param a - The first number
 * @param b - The second number
 * @returns The sum of a and b
 * @throws {Error} If parameters are not numbers
 *
 * @example
 * ```typescript
 * const result = add(2, 3);
 * console.log(result); // 5
 * ```
 */
function add(a: number, b: number): number {
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Parameters must be numbers');
  }
  return a + b;
}
```

#### For React Components:

```typescript
/**
 * A reusable button component
 *
 * @component
 * @example
 * ```tsx
 * <Button onClick={handleClick} variant="primary">
 *   Click me
 * </Button>
 * ```
 */
interface ButtonProps {
  /** The button text or content */
  children: React.ReactNode;
  /** Click handler function */
  onClick?: () => void;
  /** Visual style variant */
  variant?: 'primary' | 'secondary' | 'danger';
  /** Whether the button is disabled */
  disabled?: boolean;
}
```

#### For Classes:

```typescript
/**
 * Manages user authentication and session
 *
 * @class UserManager
 */
class UserManager {
  async login(email: string, password: string): Promise<User> {
    // Implementation
  }
}
```

### Step 4: Generate README (if needed)

See `references/templates.md` for a full README template and worked examples.

### Step 5: Generate API Documentation

Use documentation generators (TypeDoc, JSDoc, Storybook) — see `references/tools.md`.

### Step 6: Update Existing Documentation

1. Read current documentation
2. Identify outdated sections
3. Update with current information
4. Maintain consistent formatting
5. Add new sections as needed

### Step 7: Verify Documentation

Check for clarity, working code examples, correct types, up-to-date API references, working links. See `references/checklist.md`.

## References

- `references/templates.md` — Worked examples (functions, components, READMEs, API refs) + README template sections
- `references/checklist.md` — Pre/during/post checklists + JSDoc/TSDoc documentation standards
- `references/tools.md` — TypeDoc, JSDoc, Storybook, Docusaurus, VitePress setup + CI/CD automation
- `references/troubleshooting.md` — Common doc generation issues and fixes
- `references/best-practices.md` — DO/DON'T list, JSDoc/TSDoc tags, documentation structure

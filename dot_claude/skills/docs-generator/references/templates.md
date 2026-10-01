## Examples

### Example 1: Document a Utility Function

```typescript
// Before
function formatDate(date) {
  return date.toISOString().split('T')[0];
}

// After
/**
 * Formats a Date object into ISO date string (YYYY-MM-DD)
 *
 * @param date - The date to format
 * @returns ISO formatted date string (YYYY-MM-DD)
 * @throws {TypeError} If date is not a valid Date object
 *
 * @example
 * ```typescript
 * const date = new Date('2024-01-15T10:30:00');
 * const formatted = formatDate(date);
 * console.log(formatted); // "2024-01-15"
 * ```
 */
function formatDate(date: Date): string {
  if (!(date instanceof Date) || isNaN(date.getTime())) {
    throw new TypeError('Invalid date object');
  }
  return date.toISOString().split('T')[0];
}
```

### Example 2: Generate README for New Project

```bash
# Step 1: Analyze project structure
ls -la
cat package.json

# Step 2: Create README.md with Write tool
# Include: title, description, installation, usage, examples

# Step 3: Add badges
# Build status, coverage, version, license

# Step 4: Add screenshots/demos if applicable
```

### Example 3: Document React Component

```typescript
/**
 * Card component for displaying content in a contained box
 *
 * @component
 * @example
 * ```tsx
 * <Card title="Welcome" variant="outlined">
 *   <p>Card content goes here</p>
 * </Card>
 * ```
 */
interface CardProps {
  /** Card title displayed at the top */
  title?: string;
  /** Visual style variant */
  variant?: 'filled' | 'outlined' | 'elevated';
  /** Card content */
  children: React.ReactNode;
  /** Optional click handler */
  onClick?: () => void;
  /** Additional CSS classes */
  className?: string;
}

export function Card({
  title,
  variant = 'filled',
  children,
  onClick,
  className = ''
}: CardProps) {
  return (
    <div
      className={`card card-${variant} ${className}`}
      onClick={onClick}
    >
      {title && <h3 className="card-title">{title}</h3>}
      <div className="card-content">{children}</div>
    </div>
  );
}
```

### Example 4: Generate API Reference

```bash
# Step 1: Install TypeDoc
npm install --save-dev typedoc

# Step 2: Create typedoc.json
cat > typedoc.json << 'EOF'
{
  "entryPoints": ["src/index.ts"],
  "out": "docs",
  "excludePrivate": true,
  "excludeProtected": false,
  "readme": "README.md"
}
EOF

# Step 3: Generate docs
npx typedoc

# Step 4: Review generated docs
open docs/index.html
```

### Example 5: Update Existing README

```bash
# Step 1: Read current README
cat README.md

# Step 2: Identify changes needed
# - New features added
# - API changes
# - Updated dependencies
# - New installation steps

# Step 3: Update README with Edit tool
# Add new sections
# Update examples
# Fix broken links

# Step 4: Verify changes
cat README.md
```

### README Template Sections:

```markdown
# Project Title
## Badges (build, coverage, version)
## Description
## Features
## Screenshots/Demo
## Installation
## Quick Start
## Usage
## API Reference
## Examples
## Configuration
## Development
## Testing
## Deployment
## Contributing
## License
## Authors
## Acknowledgments
## FAQ
## Troubleshooting
## Changelog
```

## Documentation Checklist

Before writing documentation:
- [ ] Identified what needs documenting
- [ ] Analyzed code thoroughly
- [ ] Understood use cases
- [ ] Prepared examples
- [ ] Checked existing documentation

While writing documentation:
- [ ] Clear, concise descriptions
- [ ] All parameters documented
- [ ] Return types specified
- [ ] Error cases covered
- [ ] Working examples included
- [ ] Consistent formatting
- [ ] Proper grammar and spelling
- [ ] Code examples tested

After writing documentation:
- [ ] Examples actually work
- [ ] All links valid
- [ ] Consistent with project style
- [ ] No outdated information
- [ ] Covers common use cases
- [ ] Easy to understand for target audience
- [ ] Generated docs build without errors

## Documentation Standards

### Function Documentation:
```typescript
/**
 * Brief one-line summary
 *
 * Longer description explaining what the function does,
 * when to use it, and any important notes.
 *
 * @param paramName - Parameter description
 * @returns Description of return value
 * @throws {ErrorType} When error occurs
 *
 * @example
 * ```typescript
 * const result = functionName('example');
 * ```
 *
 * @see relatedFunction
 * @since 1.0.0
 */
```

### Component Documentation:
```typescript
/**
 * Component summary
 *
 * @component
 * @example
 * ```tsx
 * <ComponentName prop="value">
 *   Content
 * </ComponentName>
 * ```
 */
```

### Class Documentation:
```typescript
/**
 * Class summary
 *
 * @class ClassName
 * @example
 * ```typescript
 * const instance = new ClassName();
 * instance.method();
 * ```
 */
```

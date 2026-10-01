## Troubleshooting

**Issue**: Generated docs have broken links
**Solution**: Check file paths, ensure all referenced files exist, use relative links correctly.

**Issue**: Code examples don't work
**Solution**: Test examples in isolation. Ensure imports are included. Check for missing dependencies.

**Issue**: Documentation out of sync with code
**Solution**: Set up automated doc generation in CI/CD. Add pre-commit hooks to check docs.

**Issue**: TypeDoc/JSDoc fails to generate
**Solution**: Check for syntax errors in comments. Ensure entry points are correct. Verify tsconfig.json settings.

**Issue**: Too much/too little documentation
**Solution**: Focus on public APIs. Document "why" not "how". Skip self-explanatory code.

**Issue**: Documentation unclear to users
**Solution**: Get feedback from target audience. Add more examples. Use simpler language.

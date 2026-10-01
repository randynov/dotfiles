## Documentation Tools

### TypeDoc (TypeScript)
```bash
npm install --save-dev typedoc

# Generate docs
npx typedoc --out docs src

# With config file
npx typedoc
```

### JSDoc (JavaScript)
```bash
npm install --save-dev jsdoc

# Generate docs
npx jsdoc -c jsdoc.json src
```

### Storybook (React Components)
```bash
npx sb init

# Run storybook
npm run storybook

# Build static docs
npm run build-storybook
```

### Docusaurus (Full Documentation Site)
```bash
npx create-docusaurus@latest docs classic

# Run dev server
cd docs
npm start

# Build
npm run build
```

### VitePress (Vue Documentation)
```bash
npm install -D vitepress

# Init docs
npx vitepress init

# Run dev server
npm run docs:dev
```

## Automation

### Generate docs on commit (package.json):
```json
{
  "scripts": {
    "docs": "typedoc",
    "docs:watch": "typedoc --watch",
    "predocs": "npm run lint"
  },
  "husky": {
    "hooks": {
      "pre-commit": "npm run docs"
    }
  }
}
```

### CI/CD Documentation Deployment:
```yaml
# GitHub Actions
- name: Generate documentation
  run: npm run docs

- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs
```

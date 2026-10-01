**Review and commit changes to github**

**Steps:**
Analyze my uncommitted changes and:

1. Run `git diff --stat` to list changed files
2. For each file, review key changes using `git diff <file>`
3. Generate a commit message following Conventional Commits:
   - Format:
     ```
     <type>(<scope>): <subject>
     [BLANK LINE]
     <body>
     [BLANK LINE]
     <footer>
     ```
   - Types:
     - `✨ feat` - New feature
     - `🐛 fix` - Bug fix
     - `📚 docs` - Documentation changes
     - `💎 style` - Code style/formatting
     - `♻️ refactor` - Code restructuring
     - `🧪 test` - Test-related changes
     - `🏗️ chore` - Build process/auxiliary tools
     - `⚡ perf` - Performance improvements
     - `🌱 ci` - CI/CD pipeline changes
   - Scope (optional): Noun describing affected area
   - Subject: Imperative mood ("Add feature" not "Added feature"), ≤50 chars recommended
   - Body: Detailed description, ≤72 chars/line recommended
   - Footer:
     - "BREAKING CHANGE: <description>" (with space after colon)
     - Or other metadata like issue references
4. Double-check your work and message (is it accurate and concise?), if no, fix. If yes:
   - `git commit -am "[message]"`
   - `git push origin [current-branch]`

Important:
- Reference agent.md for project-specific rules
- Flag any TODOs or commented-out code
- Verify no secrets/credentials are exposed

**Goal:** Ensure the commit message issue is useful for future developers.


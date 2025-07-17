#!/bin/zsh

echo "=== Zsh Performance Optimization ==="
echo

# 1. Check completion system
echo "1. Completion system issues:"
echo "   - compinit taking 74% of startup time"
echo "   - compdef taking 25% of startup time"
echo

# 2. Check for completion dumps
echo "2. Completion dump files:"
ls -la ~/.zcompdump* 2>/dev/null || echo "   No completion dumps found"
echo

# 3. Fix slow completions
echo "3. Optimization strategies:"
echo "   a) Skip security checks for completions (if trusted environment)"
echo "   b) Use completion caching"
echo "   c) Lazy load plugins"
echo "   d) Optimize conda initialization"
echo

# 4. Check conda setup
echo "4. Conda initialization:"
grep -n "conda" ~/.zshrc | head -5
echo

# 5. Check plugin loading
echo "5. Plugin loading:"
grep -n "plugins\|source.*oh-my-zsh" ~/.zshrc | head -5
echo

echo "Recommendations:"
echo "1. Add 'skip_global_compinit=1' to speed up compinit"
echo "2. Use lazy conda initialization"
echo "3. Consider disabling unused plugins"
echo "4. Use completion caching"
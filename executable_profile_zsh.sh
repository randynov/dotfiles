#!/bin/zsh

# Zsh startup profiling script
echo "=== Zsh Startup Profiling ==="
echo

# Method 1: Simple timing
echo "1. Basic timing:"
time zsh -i -c exit

echo
echo "2. Detailed zsh profiling with zprof:"
echo "   Run: zsh -i -c 'zprof | head -20'"
zsh -i -c 'zprof | head -20'

echo
echo "3. Manual timing sections:"
echo "   Add these to your .zshrc to profile sections:"
echo
cat << 'EOF'
# Add at the top of .zshrc
zmodload zsh/datetime
setopt PROMPT_SUBST
PS4='+$EPOCHREALTIME %N:%i> '
exec 3>&2 2>/tmp/zsh_profile.$$
setopt XTRACE

# Add at the bottom of .zshrc  
unsetopt XTRACE
exec 2>&3 3>&-

echo "Startup time: $(( EPOCHREALTIME - START_TIME ))s"
EOF

echo
echo "4. Check for problematic commands:"
echo "   These commands might be slow:"
echo "   - git status in large repos"
echo "   - network calls (curl, wget)"
echo "   - filesystem operations"
echo "   - large plugin initialization"
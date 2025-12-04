# Setting Up a New Mac with Dotfiles

Complete step-by-step guide to configure a new Mac with your dotfiles and development environment.

## Prerequisites

- New or clean macOS installation
- Admin access
- GitHub account with SSH key or GitHub CLI auth
- Internet connection
- Approximately 30-45 minutes

## Phase 1: System Preparation

### 1.1 Install Xcode Command Line Tools

Required for Homebrew and development:

```bash
xcode-select --install
```

Wait for the installation to complete (5-10 minutes).

### 1.2 Verify Installation

```bash
xcode-select --version
```

## Phase 2: Install Homebrew

### 2.1 Install Homebrew Package Manager

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2.2 Add Homebrew to PATH (Apple Silicon only)

If using M1/M2/M3 Mac:

```bash
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

### 2.3 Verify Installation

```bash
brew --version
```

## Phase 3: Clone and Setup Chezmoi

### 3.1 Install Chezmoi via Homebrew

```bash
brew install chezmoi
```

### 3.2 Initialize from Your Dotfiles Repository

```bash
chezmoi init --apply https://github.com/randynov/dotfiles.git
```

This will:
- Clone your dotfiles repo to `~/.local/share/chezmoi`
- Apply all managed files to your home directory
- Set up symlinks for Vim configuration

### 3.3 Verify Chezmoi Setup

```bash
chezmoi status
```

Should show no differences or only expected changes.

## Phase 4: Install Core Development Tools

### 4.1 Install Key Brewable Tools

```bash
# Version managers
brew install mise

# Shell and terminal
brew install zsh zoxide starship atuin

# Version control
brew install git gh

# Editors
brew install neovim

# Development utilities
brew install fzf delta htop
```

### 4.2 Install Python

```bash
brew install python@3.11
```

### 4.3 Install Node.js via mise

```bash
mise install node@latest
mise use node@latest
```

### 4.4 Install Ruby (optional, if needed)

```bash
mise install ruby@latest
```

### 4.5 Update Homebrew

```bash
brew update && brew upgrade
```

## Phase 5: Configure Shell

### 5.1 Set Zsh as Default Shell

```bash
chsh -s /bin/zsh
```

Restart terminal to confirm.

### 5.2 Install Oh My Zsh (Optional)

If you prefer Oh My Zsh over plain Zsh:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

### 5.3 Reload Shell Configuration

```bash
source ~/.zshrc
```

## Phase 6: Setup Git Authentication

### 6.1 Generate SSH Key

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

Press Enter for defaults. **Do not set a passphrase for headless use.**

### 6.2 Add SSH Key to GitHub

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy output and add to GitHub: https://github.com/settings/keys

### 6.3 Test SSH Connection

```bash
ssh -T git@github.com
```

Should respond: `Hi USERNAME! You've successfully authenticated...`

### 6.4 Configure Git User

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

## Phase 7: Install Application-Specific Tools

### 7.1 Terminal Multiplexer (tmux)

```bash
brew install tmux
```

### 7.2 Docker (if needed)

```bash
brew install docker docker-compose
```

### 7.3 Database Tools (if needed)

```bash
brew install postgresql@17 redis
```

### 7.4 Additional CLI Tools

```bash
# File processing
brew install jq ripgrep tree

# HTTP client
brew install curl wget

# System monitoring
brew install bottom
```

## Phase 8: Install GUI Applications (Homebrew Cask)

### 8.1 Install Applications

```bash
# Editors and IDEs
brew install --cask zed visual-studio-code

# Browsers
brew install --cask arc firefox

# Communication
brew install --cask slack discord

# Utilities
brew install --cask 1password iterm2 rectangle alfred

# Other development tools
brew install --cask postman insomnia
```

Adjust based on your actual needs.

## Phase 9: Apply Final Configuration

### 9.1 Sync All Dotfiles

After manual installations, ensure everything is in sync:

```bash
chezmoi status
chezmoi diff
```

Review any differences.

### 9.2 Apply Any Changes

```bash
chezmoi apply
```

### 9.3 Setup Chezmoi Alias

Already configured in your dotfiles:

```bash
alias czup="chezmoi re-add && chezmoi git add . && chezmoi git -- commit -m 'Auto-sync dotfiles' && chezmoi git push && chezmoi update"
alias cz="chezmoi"
```

Test it:

```bash
czup
```

## Phase 10: System Settings (Manual)

These cannot be automated and must be done manually:

### 10.1 Keyboard & Input

- System Settings > Keyboard > Key repeat rate
- System Settings > Keyboard > Delay until repeat
- System Settings > Keyboard > Shortcuts (customize as needed)

### 10.2 Trackpad

- System Settings > Trackpad > Tracking speed
- System Settings > Trackpad > Tap to click

### 10.3 Finder

- Finder > Settings > Advanced > Show filename extensions
- Finder > Settings > Sidebar (customize visible items)

### 10.4 Dock

- Drag preferred applications to Dock
- System Settings > Dock > Minimize using: Scale effect

### 10.5 Terminal/iTerm2

- Import color schemes if preferred
- Set font to your preference (Menlo, Monaco, etc.)

## Phase 11: Verification

### 11.1 Check All Components

```bash
# Chezmoi
chezmoi --version

# Version managers
mise --version

# Shell
echo $SHELL
zsh --version

# Git
git --version
gh --version

# Editors
nvim --version

# Tools
node --version
python3 --version
```

### 11.2 Test Aliases

```bash
# Test your aliases
alias | grep -E "^alias (cz|cc-|czup)"
```

### 11.3 Verify Dotfiles Applied

```bash
# Check that key files exist
ls -la ~/.zshrc
ls -la ~/.config/nvim/init.lua
ls -la ~/.config/starship.toml
```

## Phase 12: Troubleshooting

### Problem: Chezmoi init fails with GitHub auth

**Solution:** Use GitHub CLI to authenticate first:

```bash
gh auth login
# Follow prompts to authenticate

# Then retry chezmoi init
chezmoi init --apply https://github.com/randynov/dotfiles.git
```

### Problem: Shell not sourcing aliases

**Solution:** Verify `.zshrc` is sourcing `.zalias`:

```bash
grep "zalias" ~/.zshrc
```

If missing, chezmoi should have applied it. Try:

```bash
chezmoi apply
```

### Problem: Python/Node not found after installation

**Solution:** Restart your terminal or reload shell:

```bash
exec zsh
```

### Problem: Git SSH connection fails

**Solution:** Verify SSH key:

```bash
ssh -vT git@github.com
# Look for "Offering public key" messages
```

If no keys offered, add to SSH agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

### Problem: Chezmoi apply reports conflicts

**Solution:** Review differences:

```bash
chezmoi diff
```

If you made local changes you want to keep:

```bash
chezmoi re-add   # Add your local changes to source
chezmoi apply    # Then apply managed files
```

## Quick Reference: Essential Commands

```bash
# Clone and apply dotfiles
chezmoi init --apply https://github.com/randynov/dotfiles.git

# Check what would change
chezmoi status
chezmoi diff

# Apply all managed files
chezmoi apply

# Add local file changes back to chezmoi
chezmoi add ~/.zshrc

# Update from remote
chezmoi update

# Sync (pull + push with commit)
czup

# Edit a managed file
chezmoi edit ~/.zshrc
```

## After Setup

1. **Customize for your needs:**
   - Edit `~/.zalias` for personal shortcuts
   - Add project-specific configs in `~/.local/share/chezmoi`
   - Install additional tools as needed

2. **Keep dotfiles in sync:**
   - After modifying dotfiles, run `czup` to sync
   - Review `chezmoi diff` before applying changes

3. **Backup important settings:**
   - GitHub account recovery codes
   - SSH key passphrases (in password manager)
   - API keys and secrets (never in dotfiles)

## Additional Resources

- Chezmoi documentation: https://www.chezmoi.io
- Homebrew documentation: https://brew.sh
- GitHub CLI documentation: https://cli.github.com

# Setting Up a New Mac with Dotfiles

Step-by-step guide to configure a new Mac with these dotfiles and the development environment.

Apps and CLI tools are reinstalled from the `Brewfile`, not copied. User data (`~/code`, secrets, tool state) moves separately with rsync over SSH.

## Prerequisites

- New or clean macOS installation
- Admin access
- SSH access to the old Mac, or the old Mac's SSH keys available another way
- Internet connection

## Phase 1: System Preparation

### 1.1 Install Xcode Command Line Tools

```bash
xcode-select --install
xcode-select --version
```

## Phase 2: Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"
brew --version
```

Do not append Homebrew PATH lines to `~/.zprofile` by hand. chezmoi manages that file and will overwrite or conflict with the edit.

## Phase 3: SSH Keys

Copy the existing keys from the old Mac instead of generating new ones. GitHub and servers already trust them.

On the new Mac:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
rsync -aX -e 'ssh -4' OLD_MAC_HOSTNAME:.ssh/ ~/.ssh/
chmod 600 ~/.ssh/* && chmod 644 ~/.ssh/*.pub
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
ssh -T git@github.com
```

Replace `OLD_MAC_HOSTNAME` before running. Keys with a passphrase prompt once, then the passphrase is stored in the macOS keychain.

If generating a new key instead, set a passphrase and store it in the password manager.

## Phase 4: Clone and Apply Dotfiles

### 4.1 Install chezmoi and initialize without applying

```bash
brew install chezmoi
chezmoi init git@github.com:randynov/dotfiles.git
```

### 4.2 Review before applying

```bash
chezmoi diff
```

If `~/.zshrc` was already copied from the old Mac, it is newer than the repo copy and contains local secrets. Apply everything except it:

```bash
chezmoi apply $(chezmoi managed --path-style=absolute | grep -v '/\.zshrc$')
```

Otherwise, apply everything:

```bash
chezmoi apply
chezmoi status
```

`chezmoi apply` writes `~/Brewfile`.

## Phase 5: Install Packages from the Brewfile

```bash
brew bundle check --file=~/Brewfile
brew bundle --file=~/Brewfile
```

The Brewfile covers taps, formulae, casks, VS Code extensions, and npm, uv, go, and cargo tools.

Not in the Brewfile; install separately:

- Docker Desktop: `brew install --cask docker-desktop`, or download from docker.com
- uv: `brew install uv` (the old Mac had a pip-installed uv)

### 5.1 Keep the Brewfile current

On the machine with the newest package set:

```bash
brew bundle dump --force --file=~/.local/share/chezmoi/Brewfile
```

## Phase 6: Language Toolchains

Reinstall from version managers and project lockfiles. Do not copy toolchain directories (`~/.rustup`, `~/.cargo`, `~/.nvm`, `~/.rbenv`, `~/.bun`) or caches (`~/.cache`, `~/.npm`).

```bash
mise install            # tools listed in ~/.config/mise/config.toml
```

In each project, install dependencies from its lockfile (`uv sync`, `npm ci`, `pnpm install`, `bundle install`, `cargo build`).

## Phase 7: Configure Shell

```bash
chsh -s /bin/zsh
exec zsh
```

Oh My Zsh, if used:

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --keep-zshrc
```

`--keep-zshrc` stops the installer from replacing the chezmoi-managed `~/.zshrc`.

## Phase 8: Git Identity

`~/.gitconfig` comes from chezmoi. Verify instead of re-setting:

```bash
git config --global user.name
git config --global user.email
```

## Phase 9: System Settings (Manual)

### 9.1 Keyboard & Input

- System Settings > Keyboard > Key repeat rate
- System Settings > Keyboard > Delay until repeat
- System Settings > Keyboard > Shortcuts

### 9.2 Trackpad

- System Settings > Trackpad > Tracking speed
- System Settings > Trackpad > Tap to click

### 9.3 Finder

- Finder > Settings > Advanced > Show filename extensions
- Finder > Settings > Sidebar

### 9.4 Dock

- Drag preferred applications to Dock
- System Settings > Dock > Minimize using: Scale effect

## Phase 10: Verification

```bash
chezmoi status
brew bundle check --file=~/Brewfile
echo $SHELL
git --version && gh --version && nvim --version
node --version && python3 --version
ssh -T git@github.com
ls -la ~/.zshrc ~/.config/nvim/init.lua ~/.config/starship.toml
```

## Secrets and This Repo

This repo is public. Keep secrets out of every managed file.

- Put tokens and API keys in 1Password and read them at shell start (`op read op://...`), or in an unmanaged file such as `~/.zshrc.local`.
- `chezmoi re-add` warns when it finds a secret but still writes the file into the source directory. Run `git diff` before every commit.
- The `czup` alias runs `chezmoi re-add`, commits, and pushes in one step. Do not use it while any managed file contains a secret.

## Troubleshooting

### chezmoi init fails with GitHub auth

```bash
gh auth login
chezmoi init git@github.com:randynov/dotfiles.git
```

### Shell not sourcing aliases

```bash
grep "zalias" ~/.zshrc
chezmoi apply
```

### Python/Node not found after installation

```bash
exec zsh
```

### Git SSH connection fails

```bash
ssh -vT git@github.com
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

### chezmoi apply reports conflicts

```bash
chezmoi diff
chezmoi re-add ~/path/to/file   # keep the local version
chezmoi apply                   # or take the repo version
```

### Shell errors mentioning `\r`

A file has Windows line endings. Convert it back to LF before committing:

```bash
git -C ~/.local/share/chezmoi ls-files --eol | grep crlf
```

## Quick Reference

```bash
chezmoi init git@github.com:randynov/dotfiles.git
chezmoi diff
chezmoi apply
chezmoi re-add ~/.zshrc
chezmoi update
chezmoi edit ~/.zshrc
brew bundle --file=~/Brewfile
```

## Additional Resources

- chezmoi: https://www.chezmoi.io
- Homebrew Bundle: https://docs.brew.sh/Brew-Bundle-and-Brewfile
- GitHub CLI: https://cli.github.com

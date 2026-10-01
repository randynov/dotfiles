#!/bin/bash
# Dock, Finder, keyboard, trackpad, and screenshot settings captured from the old Mac.
# Run once by hand on a new Mac: bash ~/macos-defaults.sh
set -euo pipefail

# Dock
defaults write com.apple.dock autohide -bool false
defaults write com.apple.dock tilesize -float 31
defaults write com.apple.dock largesize -float 122
defaults write com.apple.dock magnification -bool true
defaults write com.apple.dock orientation -string left
defaults write com.apple.dock show-recents -bool true
defaults write com.apple.dock mru-spaces -bool false
# Hot corners: TL Quick Note, TR Desktop, BL Notification Center, BR Application Windows
defaults write com.apple.dock wvous-tl-corner -int 14
defaults write com.apple.dock wvous-tr-corner -int 4
defaults write com.apple.dock wvous-bl-corner -int 10
defaults write com.apple.dock wvous-br-corner -int 3

# Finder
defaults write com.apple.finder ShowPathbar -bool true
defaults write com.apple.finder ShowStatusBar -bool true
defaults write com.apple.finder FXPreferredViewStyle -string Nlsv
defaults write com.apple.finder FXDefaultSearchScope -string SCcf
defaults write com.apple.finder _FXSortFoldersFirst -bool true
defaults write com.apple.finder NewWindowTarget -string PfLo
defaults write com.apple.finder NewWindowTargetPath -string "file://$HOME/Downloads/"
defaults write com.apple.finder ShowExternalHardDrivesOnDesktop -bool true
defaults write com.apple.finder ShowRemovableMediaOnDesktop -bool true
defaults write com.apple.finder ShowHardDrivesOnDesktop -bool true

# Global
defaults write NSGlobalDomain AppleShowAllExtensions -bool true
defaults write NSGlobalDomain NSAutomaticCapitalizationEnabled -bool true
defaults write NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled -bool true
defaults write NSGlobalDomain AppleInterfaceStyle -string Dark
defaults write NSGlobalDomain AppleKeyboardUIMode -int 2
defaults write NSGlobalDomain com.apple.swipescrolldirection -bool false
defaults write NSGlobalDomain AppleShowScrollBars -string Always

# Trackpad
defaults write com.apple.AppleMultitouchTrackpad Clicking -int 0
defaults write com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag -bool false
defaults write com.apple.AppleMultitouchTrackpad TrackpadRightClick -bool true

# Screenshots
mkdir -p "$HOME/Downloads/Screenshots"
defaults write com.apple.screencapture location -string "$HOME/Downloads/Screenshots"
defaults write com.apple.screencapture type -string png

killall Dock Finder SystemUIServer 2>/dev/null || true
echo "Done. Log out and back in for keyboard and trackpad settings to take full effect."

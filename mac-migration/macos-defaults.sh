#!/bin/bash
# Dock, Finder, keyboard, trackpad, and screenshot settings captured from the old Mac.
# Preview: bash ~/mac-migration/macos-defaults.sh --dry-run
# Apply:   bash ~/mac-migration/macos-defaults.sh
set -euo pipefail

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true
changes=0

# set_default DOMAIN KEY TYPE VALUE; booleans as true/false.
set_default() {
  local domain=$1 key=$2 type=$3 want=$4 have cmp
  have=$(defaults read "$domain" "$key" 2>/dev/null || echo "<unset>")
  cmp=$want
  [[ $type == bool ]] && { [[ $want == true ]] && cmp=1 || cmp=0; }
  if [[ "$have" == "$cmp" ]]; then
    printf "  same     %-38s %-32s %s\n" "$domain" "$key" "$have"
    return
  fi
  printf "  CHANGE   %-38s %-32s %s -> %s\n" "$domain" "$key" "$have" "$want"
  changes=$((changes + 1))
  $DRY_RUN || defaults write "$domain" "$key" "-$type" "$want"
}

# Dock
set_default com.apple.dock autohide bool false
set_default com.apple.dock tilesize float 31
set_default com.apple.dock largesize float 122
set_default com.apple.dock magnification bool true
set_default com.apple.dock orientation string left
set_default com.apple.dock show-recents bool true
set_default com.apple.dock mru-spaces bool false
# Hot corners: TL Quick Note, TR Desktop, BL Put Display to Sleep, BR Application Windows
set_default com.apple.dock wvous-tl-corner int 14
set_default com.apple.dock wvous-tr-corner int 4
set_default com.apple.dock wvous-bl-corner int 10
set_default com.apple.dock wvous-br-corner int 3

# Finder
set_default com.apple.finder ShowPathbar bool true
set_default com.apple.finder ShowStatusBar bool true
set_default com.apple.finder FXPreferredViewStyle string Nlsv
set_default com.apple.finder FXDefaultSearchScope string SCcf
set_default com.apple.finder _FXSortFoldersFirst bool true
set_default com.apple.finder NewWindowTarget string PfLo
set_default com.apple.finder NewWindowTargetPath string "file://$HOME/Downloads/"
set_default com.apple.finder ShowExternalHardDrivesOnDesktop bool true
set_default com.apple.finder ShowRemovableMediaOnDesktop bool true
set_default com.apple.finder ShowHardDrivesOnDesktop bool true

# Global
set_default NSGlobalDomain AppleShowAllExtensions bool true
set_default NSGlobalDomain NSAutomaticCapitalizationEnabled bool true
set_default NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled bool true
set_default NSGlobalDomain AppleInterfaceStyle string Dark
set_default NSGlobalDomain AppleKeyboardUIMode int 2
set_default NSGlobalDomain com.apple.swipescrolldirection bool false
set_default NSGlobalDomain AppleShowScrollBars string Always

# Trackpad
set_default com.apple.AppleMultitouchTrackpad Clicking int 0
set_default com.apple.AppleMultitouchTrackpad TrackpadThreeFingerDrag bool false
set_default com.apple.AppleMultitouchTrackpad TrackpadRightClick bool true

# Screenshots
set_default com.apple.screencapture location string "$HOME/Downloads/Screenshots"
set_default com.apple.screencapture type string png

if $DRY_RUN; then
  echo "Dry run: $changes setting(s) would change. Nothing was written."
  exit 0
fi
mkdir -p "$HOME/Downloads/Screenshots"
killall Dock Finder SystemUIServer 2>/dev/null || true
echo "Applied $changes change(s). Log out and back in for keyboard and trackpad settings to take full effect."

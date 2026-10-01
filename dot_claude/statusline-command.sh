#!/bin/bash
# Rich 3-line statusline for Claude Code on macOS

# Error handling - always output something
trap 'echo "Claude"' ERR

# Color definitions
BLUE='\033[38;2;0;153;255m'
ORANGE='\033[38;2;255;176;85m'
GREEN='\033[38;2;0;160;0m'
CYAN='\033[38;2;46;149;153m'
RED='\033[38;2;255;85;85m'
YELLOW='\033[38;2;230;200;0m'
PURPLE='\033[38;2;180;150;255m'
PEACH='\033[38;2;255;180;130m'
DIM='\033[2m'
RESET='\033[0m'

# Read JSON from stdin
input=$(</dev/stdin)

# Extract all fields from input JSON in a single jq call
IFS=$'\t' read -r model context_size used_pct input_tokens output_tokens cache_creation cache_read current_dir <<< \
  "$(echo "$input" | /usr/bin/jq -r '[
    (.model.display_name // "Unknown"),
    (.context_window.context_window_size // 0),
    (.context_window.used_percentage // 0),
    (.context_window.current_usage.input_tokens // 0),
    (.context_window.current_usage.output_tokens // 0),
    (.context_window.current_usage.cache_creation_input_tokens // 0),
    (.context_window.current_usage.cache_read_input_tokens // 0),
    (.workspace.current_dir // .cwd // "")
  ] | @tsv')"

current_tokens=$((input_tokens + output_tokens + cache_creation + cache_read))

# Format token counts with k/m suffixes
format_tokens() {
  local tokens=${1%.*}
  if ((tokens >= 1000000)); then
    printf "%d.%dm" $((tokens / 1000000)) $(( (tokens % 1000000) / 100000 ))
  elif ((tokens >= 1000)); then
    printf "%dk" $((tokens / 1000))
  else
    printf "%d" "$tokens"
  fi
}

# Build a ●/○ progress bar with color thresholds
# Usage: build_bar <percent> <show_pct> [threshold_profile]
#   show_pct: 1 to prefix "NN% ", 0 for bar only
#   threshold_profile: "context" (default: green<40, yellow<75, red>=75)
#                      "usage" (green<50, orange<70, yellow<90, red>=90)
build_bar() {
  local percent=$1
  local show_pct=${2:-0}
  local profile=${3:-context}
  local width=10
  local pct_int=${percent%.*}

  local filled=$((pct_int * width / 100))
  local empty=$((width - filled))

  # Choose color based on profile
  local bar_color="${GREEN}"
  if [[ "$profile" == "usage" ]]; then
    if ((pct_int >= 90)); then bar_color="${RED}"
    elif ((pct_int >= 70)); then bar_color="${YELLOW}"
    elif ((pct_int >= 50)); then bar_color="${ORANGE}"
    fi
  else
    if ((pct_int >= 75)); then bar_color="${RED}"
    elif ((pct_int >= 40)); then bar_color="${YELLOW}"
    fi
  fi

  local bar=""
  for ((i = 0; i < filled; i++)); do bar="${bar}●"; done
  for ((i = 0; i < empty; i++)); do bar="${bar}○"; done

  if ((show_pct)); then
    printf "${bar_color}%.0f%% %s${RESET}" "$percent" "$bar"
  else
    printf "${bar_color}%s${RESET}" "$bar"
  fi
}

current_display=$(format_tokens $current_tokens)
total_display=$(format_tokens $context_size)
context_bar=$(build_bar "$used_pct" 1 context)

# Shorten HOME to ~
current_dir="${current_dir/#$HOME/\~}"
dir_basename=$(basename "${current_dir/#\~/$HOME}")

# Git info
git_branch=""
git_changes=""
git_worktree=""
if git rev-parse --git-dir > /dev/null 2>&1; then
  git_branch=$(git branch --show-current 2> /dev/null || git rev-parse --short HEAD 2> /dev/null)

  diff_stat=$(git diff --shortstat 2> /dev/null)
  if [ -n "$diff_stat" ]; then
    ins=$(echo "$diff_stat" | grep -o '[0-9]* insertion' | grep -o '[0-9]*' || true)
    del=$(echo "$diff_stat" | grep -o '[0-9]* deletion' | grep -o '[0-9]*' || true)
    [ -z "$ins" ] && ins=0
    [ -z "$del" ] && del=0
    git_changes="+${ins},-${del}"
  fi

  git_dir=$(git rev-parse --git-dir 2> /dev/null)
  git_common=$(git rev-parse --git-common-dir 2> /dev/null)
  if [ "$git_dir" != "$git_common" ]; then
    git_worktree=$(basename "$(git rev-parse --show-toplevel 2> /dev/null)")
  fi
fi

# Line 1: Model | Tokens | Context Bar | Dir | Branch (changes) [worktree]
printf "🤖 ${BLUE}%s${RESET} ${DIM}|${RESET} 🎰 ${ORANGE}%s${RESET} ${DIM}/${RESET} ${ORANGE}%s${RESET} ${DIM}|${RESET} 📊 %b" \
  "$model" "$current_display" "$total_display" "$context_bar"

[ -n "$dir_basename" ] && printf " ${DIM}|${RESET} 📁 ${CYAN}%s${RESET}" "$dir_basename"
[ -n "$git_branch" ] && printf " ${DIM}|${RESET} 🌿 ${GREEN}%s${RESET}" "$git_branch"
[ -n "$git_changes" ] && printf " ✏️  ${PEACH}%s${RESET}" "$git_changes"
[ -n "$git_worktree" ] && printf " 🌳 ${DIM}[${RESET}${PURPLE}%s${RESET}${DIM}]${RESET}" "$git_worktree"

printf '\n'

# --- Usage data (lines 2-3) ---

CACHE_FILE="/tmp/claude-statusline-usage-cache.json"
CACHE_TTL=60

is_cache_valid() {
  [ -f "$CACHE_FILE" ] || return 1
  local age=$(( $(/bin/date +%s) - $(/usr/bin/stat -f %m "$CACHE_FILE" 2>/dev/null || echo 0) ))
  ((age < CACHE_TTL))
}

# Fetch usage data from API, write to CACHE_FILE
# Set STATUSLINE_DEBUG=1 to enable debug logging
fetch_usage_data() {
  local debug_log="/tmp/claude-statusline-debug.log"
  log() { [[ "${STATUSLINE_DEBUG:-0}" == "1" ]] && echo "$(date): $1" >> "$debug_log"; }

  local credentials
  credentials=$(security find-generic-password -s "YOUR_CC_CREDENTIALS" -w 2>/dev/null) || {
    log "Failed to get credentials from keychain"; return 1
  }
  [ -n "$credentials" ] || { log "Empty credentials"; return 1; }

  local access_token
  access_token=$(echo "$credentials" | /usr/bin/jq -r '.claudeAiOauth.accessToken // empty' 2>/dev/null)
  [ -n "$access_token" ] || { log "Failed to parse access token"; return 1; }

  log "Fetching usage data..."
  local response
  response=$(curl -s -H "Authorization: Bearer $access_token" \
    -H "anthropic-beta: oauth-2025-04-20" \
    "https://api.anthropic.com/api/oauth/usage" 2>/dev/null)

  if [ -n "$response" ] && echo "$response" | /usr/bin/jq -e '.five_hour' >/dev/null 2>&1; then
    log "Success"
    echo "$response" > "$CACHE_FILE"
    return 0
  fi

  log "Invalid or empty response"
  rm -f "$CACHE_FILE"
  return 1
}

# Get or fetch usage data
usage_data=""
if is_cache_valid; then
  usage_data=$(<"$CACHE_FILE")
elif fetch_usage_data; then
  usage_data=$(<"$CACHE_FILE")
fi

# Display lines 2-3 if we have valid usage data
if [ -n "$usage_data" ] && echo "$usage_data" | /usr/bin/jq -e '.five_hour' >/dev/null 2>&1; then
  # Single jq call for all usage fields
  IFS=$'\t' read -r current_pct current_reset weekly_pct weekly_reset <<< \
    "$(echo "$usage_data" | /usr/bin/jq -r '[
      (.five_hour.utilization // 0),
      (.five_hour.resets_at // "N/A"),
      (.seven_day.utilization // 0),
      (.seven_day.resets_at // "N/A")
    ] | @tsv')"

  current_bar=$(build_bar "$current_pct" 0 usage)
  weekly_bar=$(build_bar "$weekly_pct" 0 usage)

  # Format reset times (ISO 8601 → local)
  format_reset_time() {
    local t=$1
    [[ -z "$t" || "$t" == "null" || "$t" == "N/A" ]] && { echo "N/A"; return; }
    local clean=${t%%.*}  # strip fractional seconds and everything after
    local fmt
    fmt=$(/bin/date -j -f "%Y-%m-%dT%H:%M:%S" "$clean" "+%b %d %I:%M %p" 2>/dev/null) && echo "$fmt" || echo "$t"
  }

  current_reset_fmt=$(format_reset_time "$current_reset")
  weekly_reset_fmt=$(format_reset_time "$weekly_reset")

  # Line 2: Usage bars
  printf "${DIM}Current (5h):${RESET} %s ${CYAN}%.0f%%${RESET} ${DIM}|${RESET} ${DIM}Weekly (7d):${RESET} %s ${CYAN}%.0f%%${RESET}\n" \
    "$current_bar" "$current_pct" "$weekly_bar" "$weekly_pct"

  # Line 3: Reset times
  printf "${DIM}Resets:${RESET} ${CYAN}%s${RESET} ${DIM}|${RESET} ${DIM}Weekly:${RESET} ${CYAN}%s${RESET}\n" \
    "$current_reset_fmt" "$weekly_reset_fmt"
fi

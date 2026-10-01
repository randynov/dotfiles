#!/bin/bash

# Base setup uses starship.rs and nerdfonts for icons
# - UbuntuMono Nerd Font — proportional icon widths (recommended for general use)
# - UbuntuMono Nerd Font Mono — all icons forced to single-width (monospace strict)
# - UbuntuMono Nerd Font Propo — proportional variant

# Read JSON input from Claude Code
input=$(cat)

# ── Extract values (single jq call) ─────────────────────────────────
eval "$(echo "$input" | jq -r '
  @sh "model=\(.model.display_name // "Unknown")",
  @sh "session_id=\(.session_id // "unknown")",
  @sh "cwd=\(.workspace.current_dir // .cwd)",
  @sh "context_used=\(.context_window.used_percentage // "null")",
  @sh "context_size=\(.context_window.context_window_size // 0)",
  @sh "total_input=\(.context_window.total_input_tokens // 0)",
  @sh "total_output=\(.context_window.total_output_tokens // 0)",
  @sh "cache_read=\(.context_window.current_usage.cache_read_input_tokens // 0)",
  @sh "cost_usd=\(.cost.total_cost_usd // 0)",
  @sh "duration_ms=\(.cost.total_duration_ms // 0)",
  @sh "api_duration_ms=\(.cost.total_api_duration_ms // 0)",
  @sh "lines_added=\(.cost.total_lines_added // 0)",
  @sh "lines_removed=\(.cost.total_lines_removed // 0)"
')"

# ── ANSI colors ─────────────────────────────────────────────────────
R="\033[0m"
C_BCYAN="\033[1;36m"
C_CYAN="\033[36m"
C_GREEN="\033[32m"
C_BGREEN="\033[1;32m"
C_BYELLOW="\033[1;33m"
C_BRED="\033[1;31m"
C_MAGENTA="\033[35m"
C_BWHITE="\033[1;37m"
C_GRAY="\033[90m"
C_BBLUE="\033[1;34m"

# ── Nerdfont icons (using escape sequences for reliability) ─────────
i_model=$'\U000F06A9'     # 󰚩 nf-md-robot
i_folder=$'\uF120'        #  nf-fa-terminal
i_branch=$'\uE725'        #  nf-dev-git_branch (feature)
i_branch_main=$'\uE726'   #  nf-dev-git_pull_request (main/protected)
i_clock=$'\uF017'         #  nf-fa-clock_o
i_ctx=$'\U000F0349'       # 󰍉 nf-md-magnify
i_in=$'\uF019'            #  nf-fa-download
i_out=$'\uF093'           #  nf-fa-upload
i_cost=$'\uF09D'          #  nf-fa-credit_card
i_cache=$'\uF0E7'         #  nf-fa-bolt
i_api=$'\U000F08A9'       # 󰢩 nf-md-api
i_lines=$'\uF1C9'         #  nf-fa-file_code_o
i_week=$'\uF073'          #  nf-fa-calendar
i_chart=$'\uF080'         #  nf-fa-bar_chart

# ── Separator & divider ────────────────────────────────────────────
sep="${C_GRAY}  │  ${R}"
# Terminal width: prefer $COLUMNS, then tput/stty, default 120
# Statusline scripts often lack a TTY so detectors return 80 — override that
cols=${COLUMNS:-0}
if [ "$cols" -le 0 ] 2>/dev/null; then
    cols=$(tput cols 2>/dev/null || stty size 2>/dev/null | awk '{print $2}' || echo 0)
fi
[ "$cols" -le 80 ] 2>/dev/null && cols=120
# ── Helpers ─────────────────────────────────────────────────────────
visible_len() {
    local clean
    clean=$(printf "%b" "$1" | sed $'s/\033\\[[0-9;]*m//g')
    echo "${#clean}"
}

print_lr() {
    local left="$1" right="$2"
    local llen rlen pad
    llen=$(visible_len "$left")
    rlen=$(visible_len "$right")
    pad=$((cols - llen - rlen))
    [ "$pad" -lt 2 ] && pad=2
    printf "%b%*s%b\n" "$left" "$pad" "" "$right"
}

format_duration() {
    local ms=$1
    local total_sec=$((ms / 1000))
    local h=$((total_sec / 3600))
    local m=$(((total_sec % 3600) / 60))
    local s=$((total_sec % 60))
    if [ $h -gt 0 ]; then
        printf "%dh %dm %ds" $h $m $s
    elif [ $m -gt 0 ]; then
        printf "%dm %ds" $m $s
    else
        printf "%ds" $s
    fi
}

format_num() {
    local n=$1
    if [ "$n" -ge 1000000 ]; then
        printf "%.1fM" "$(echo "scale=1; $n / 1000000" | bc 2>/dev/null || echo "$n")"
    elif [ "$n" -ge 1000 ]; then
        printf "%.1fK" "$(echo "scale=1; $n / 1000" | bc 2>/dev/null || echo "$n")"
    else
        printf "%d" "$n"
    fi
}

# Build a dots progress bar: filled in $1 color, empty in gray
# Usage: make_dots_bar <color> <percent> <width>
make_dots_bar() {
    local color="$1" pct="$2" width="$3"
    local pct_int filled empty bar_filled="" bar_empty=""
    pct_int=$(printf "%.0f" "$pct")
    [ "$pct_int" -gt 100 ] && pct_int=100
    filled=$((pct_int * width / 100))
    empty=$((width - filled))
    for ((i=0; i<filled; i++)); do bar_filled+="●"; done
    for ((i=0; i<empty; i++)); do bar_empty+="●"; done
    printf "%b%s%b%s%b" "$color" "$bar_filled" "$C_GRAY" "$bar_empty" "$R"
}

# ── Git branch ──────────────────────────────────────────────────────
branch=""
if [ -d "$cwd/.git" ] || git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
    branch=$(git -C "$cwd" --no-optional-locks branch --show-current 2>/dev/null || echo "detached")
fi

# Pick icon based on branch type
if [[ "$branch" == "main" || "$branch" == "master" || "$branch" == "develop" ]]; then
    branch_icon="$i_branch_main"
    branch_color="$C_BGREEN"
else
    branch_icon="$i_branch"
    branch_color="$C_BYELLOW"
fi

# ── Shorten path ────────────────────────────────────────────────────
display_path="$cwd"
[ -n "$HOME" ] && display_path="${cwd/#$HOME/\~}"

# ── Timers ──────────────────────────────────────────────────────────
session_time=$(format_duration "$duration_ms")
api_time=$(format_duration "$api_duration_ms")

# ── Context progress bar (10 dots to match rate limit bars) ─────────
ctx_bar="" ctx_tokens_display="" bar_color=""
if [ "$context_used" != "null" ] && [ -n "$context_used" ]; then
    used_int=$(printf "%.0f" "$context_used")
    if [ "$used_int" -ge 80 ]; then bar_color="$C_BRED"
    elif [ "$used_int" -ge 50 ]; then bar_color="$C_BYELLOW"
    else bar_color="$C_BGREEN"; fi
    ctx_bar=$(make_dots_bar "$bar_color" "$context_used" 10)

    # Token fraction: colored_used / total
    ctx_used_tokens=$((total_input + total_output))
    ctx_tokens_display="${bar_color}$(format_num "$ctx_used_tokens")${R} ${C_GRAY}/${R} ${C_BWHITE}$(format_num "$context_size")${R}"
fi

# ── Cost ────────────────────────────────────────────────────────────
cost_display=$(printf "\$%.2f" "$cost_usd" 2>/dev/null || printf "\$%s" "$cost_usd")

# ── Config ──────────────────────────────────────────────────────────
CONFIG_FILE="$HOME/.claude/statusline-config.json"
if [ -f "$CONFIG_FILE" ]; then
    configured_width=$(jq -r '.width // 0' "$CONFIG_FILE" 2>/dev/null)
    [ "$configured_width" -gt 0 ] 2>/dev/null && cols=$configured_width
fi

# Rebuild divider with final width
divider="${C_GRAY}$(printf '%.0s─' $(seq 1 "$cols"))${R}"

# ── Rate limit usage (from Anthropic OAuth API, cached 60s) ─────────
USAGE_CACHE="$HOME/.claude/statusline-usage-cache.json"
CREDS_FILE="$HOME/.claude/.credentials.json"
CACHE_TTL=90  # seconds

five_hr_pct=0 five_hr_reset="" seven_day_pct=0 seven_day_reset=""

fetch_usage() {
    [ -f "$CREDS_FILE" ] || return 1
    local token
    token=$(jq -r '.claudeAiOauth.accessToken // empty' "$CREDS_FILE" 2>/dev/null)
    [ -z "$token" ] && return 1
    curl -s --max-time 3 "https://api.anthropic.com/api/oauth/usage" \
        -H "Authorization: Bearer $token" \
        -H "anthropic-beta: oauth-2025-04-20" \
        -H "Accept: application/json" 2>/dev/null
}

# Check cache freshness, refresh if stale
usage_data=""
if [ -f "$USAGE_CACHE" ]; then
    cache_age=$(( $(date +%s) - $(stat -c %Y "$USAGE_CACHE" 2>/dev/null || echo 0) ))
    if [ "$cache_age" -lt "$CACHE_TTL" ]; then
        usage_data=$(cat "$USAGE_CACHE")
    fi
fi

if [ -z "$usage_data" ]; then
    usage_data=$(fetch_usage)
    if [ -n "$usage_data" ] && echo "$usage_data" | jq -e '.five_hour' >/dev/null 2>&1; then
        echo "$usage_data" > "$USAGE_CACHE"
    fi
fi

if [ -n "$usage_data" ]; then
    five_hr_pct=$(echo "$usage_data" | jq -r '.five_hour.utilization // 0' 2>/dev/null)
    five_hr_reset_raw=$(echo "$usage_data" | jq -r '.five_hour.resets_at // empty' 2>/dev/null)
    seven_day_pct=$(echo "$usage_data" | jq -r '.seven_day.utilization // 0' 2>/dev/null)
    seven_day_reset_raw=$(echo "$usage_data" | jq -r '.seven_day.resets_at // empty' 2>/dev/null)

    # Format reset times as relative durations
    format_reset() {
        local iso="$1"
        [ -z "$iso" ] && return
        local reset_epoch now_epoch diff
        reset_epoch=$(date -d "$iso" +%s 2>/dev/null) || return
        now_epoch=$(date +%s)
        diff=$((reset_epoch - now_epoch))
        [ "$diff" -le 0 ] && { echo "now"; return; }
        local h=$((diff / 3600)) m=$(((diff % 3600) / 60))
        if [ $h -gt 24 ]; then
            printf "%dd %dh" $((h / 24)) $((h % 24))
        elif [ $h -gt 0 ]; then
            printf "%dh %dm" $h $m
        else
            printf "%dm" $m
        fi
    }

    five_hr_reset=$(format_reset "$five_hr_reset_raw")
    seven_day_reset=$(format_reset "$seven_day_reset_raw")
fi

# Bar colors based on utilization
pct_color() {
    local pct_int
    pct_int=$(printf "%.0f" "$1" 2>/dev/null || echo 0)
    if [ "$pct_int" -ge 80 ]; then echo "$C_BRED"
    elif [ "$pct_int" -ge 50 ]; then echo "$C_BYELLOW"
    else echo "$C_BGREEN"; fi
}

five_hr_color=$(pct_color "$five_hr_pct")
seven_day_color=$(pct_color "$seven_day_pct")
five_hr_bar=$(make_dots_bar "$five_hr_color" "$five_hr_pct" 10)
seven_day_bar=$(make_dots_bar "$seven_day_color" "$seven_day_pct" 10)

# ── Weekly token count (from stats-cache.json) ──────────────────────
STATS_FILE="$HOME/.claude/stats-cache.json"
weekly_tokens=0
if [ -f "$STATS_FILE" ]; then
    cutoff_7d=$(date -d "7 days ago" +%Y-%m-%d 2>/dev/null || date -v-7d +%Y-%m-%d 2>/dev/null || echo "1970-01-01")
    weekly_tokens=$(jq -r --arg cutoff "$cutoff_7d" \
        '[.dailyModelTokens[] | select(.date >= $cutoff) | [.tokensByModel | to_entries[] | .value] | add // 0] | add // 0' \
        "$STATS_FILE" 2>/dev/null || echo 0)
fi

# ═══════════════════════════════════════════════════════════════════
#  LINE 1 — Model · Path · Code changes · Branch
# ═══════════════════════════════════════════════════════════════════
left1="${C_BCYAN}${i_model}  ${C_BWHITE}${model}${R}"
left1+="${sep}${C_BBLUE}${i_folder}  ${R}${display_path}"

right1=""
if [ "$lines_added" != "0" ] || [ "$lines_removed" != "0" ]; then
    right1+="${i_lines}  ${C_BGREEN}+${lines_added}  ${C_BRED}-${lines_removed}${R}"
fi
if [ -n "$branch" ]; then
    [ -n "$right1" ] && right1+="${sep}"
    right1+="${branch_color}${branch_icon}  ${branch}${R}"
fi

print_lr "$left1" "$right1"
printf "%b\n" "$divider"

# ═══════════════════════════════════════════════════════════════════
#  LINE 2 — Time · Tokens · Cache · Weekly · Cost
# ═══════════════════════════════════════════════════════════════════
left2="${C_BYELLOW}${i_clock}  ${session_time}${R}"
if [ "$api_duration_ms" != "0" ]; then
    left2+="  ${C_GRAY}(${i_api}  ${api_time})${R}"
fi
left2+="${sep}${C_GREEN}${i_in}  ${R}In: ${C_BWHITE}$(format_num "$total_input")${R}"
left2+="${sep}${C_MAGENTA}${i_out}  ${R}Out: ${C_BWHITE}$(format_num "$total_output")${R}"
if [ "$cache_read" != "0" ] && [ "$cache_read" != "null" ]; then
    left2+="${sep}${C_CYAN}${i_cache}  ${R}Cache: ${C_BWHITE}$(format_num "$cache_read")${R}"
fi
left2+="${sep}${C_BBLUE}${i_chart}  ${R}Week: ${C_BWHITE}$(format_num "$weekly_tokens")${R}"

right2="${C_BYELLOW}${i_cost}  ${cost_display}${R}"

print_lr "$left2" "$right2"
printf "%b\n" "$divider"

# ═══════════════════════════════════════════════════════════════════
#  LINE 3 — Context · 5h rate limit · 7d rate limit
# ═══════════════════════════════════════════════════════════════════
left3=""
if [ -n "$ctx_bar" ]; then
    left3+="${C_BWHITE}Now:${R}  ${ctx_bar}  ${ctx_tokens_display}${sep}"
fi

left3+="${C_BWHITE}5h:${R}  ${five_hr_bar}  ${five_hr_color}${five_hr_pct}%${R}"
if [ -n "$five_hr_reset" ]; then
    left3+=" ${C_GRAY}resets in ${five_hr_reset}${R}"
fi

left3+="${sep}${C_BWHITE}7d:${R}  ${seven_day_bar}  ${seven_day_color}${seven_day_pct}%${R}"
if [ -n "$seven_day_reset" ]; then
    left3+=" ${C_GRAY}resets in ${seven_day_reset}${R}"
fi

print_lr "$left3" ""
printf "%b\n" "$divider"
Actions

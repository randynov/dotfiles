# Apple Shortcuts for PKM CLI

Integration shortcuts for the PKM (Personal Knowledge Management) skill using Apple's Shortcuts app.

## Prerequisites

- macOS 12+ (Monterey or later)
- Apple Shortcuts app installed
- PKM skill installed at `~/.claude/skills/pkm/`
- Python 3.8+ available at `/usr/bin/python3`

---

## 1. Universal Capture

**Purpose**: Quick capture from anywhere - text, URLs, web content, or clipboard

### Shortcut Actions

```
1. Get text from "Shortcut Input" [fallback: Clipboard]
2. If "Shortcut Input" has any value
   → Set variable "Content" to "Shortcut Input"
   Otherwise
   → Set variable "Content" to "Clipboard"
3. Run Shell Script over SSH (Local):
   /usr/bin/python3 ~/.claude/skills/pkm/capture.py "$Content"
4. Show Notification:
   Title: "PKM Captured"
   Body: "Content"
```

### How to Create

**Option A: Manual Creation**

1. Open Shortcuts app
2. Click "+" to create new shortcut
3. Name it "PKM Capture"
4. Add actions in order:
   - **Get text from** → Choose "Shortcut Input" with fallback "Clipboard"
   - **If** → Condition: "Shortcut Input has any value"
   - **Set Variable** → Name: "Content", Value: "Shortcut Input"
   - **Otherwise**
   - **Set Variable** → Name: "Content", Value: "Clipboard"
   - **End If**
   - **Run Shell Script** → Script: `/usr/bin/python3 ~/.claude/skills/pkm/capture.py "Content"`
     - Input: "Content" variable
     - Shell: `/bin/zsh`
   - **Show Notification** → Title: "PKM Captured", Body: First 50 chars of "Content"

**Option B: Import from File** (Coming Soon)

1. Download `PKM-Capture.shortcut` from skill directory
2. Double-click to import into Shortcuts app
3. Grant permissions when prompted

### Trigger Configuration

**Siri**:
- "Hey Siri, PKM Capture"
- "Hey Siri, Capture this note"

**Control Center**:
1. Settings → Control Center
2. Add "Shortcuts" widget
3. Long-press Shortcuts widget to select "PKM Capture"

**Share Sheet**:
1. In Shortcuts app, select "PKM Capture"
2. Toggle "Show in Share Sheet"
3. Now available when sharing from Safari, Notes, etc.

**Keyboard Shortcut**:
1. System Settings → Keyboard → Keyboard Shortcuts → Services
2. Find "PKM Capture" under "General"
3. Assign: `⌘⇧C` (Command-Shift-C)

**Menu Bar**:
1. In Shortcuts app, select "PKM Capture"
2. Toggle "Pin in Menu Bar"
3. Click shortcut icon in menu bar to run

---

## 2. Daily Nudge

**Purpose**: Morning priorities - runs at 8 AM daily, shows top 3 tasks

### Shortcut Actions

```
1. Run Shell Script:
   /usr/bin/python3 ~/.claude/skills/pkm/nudge.py
2. Set variable "Priorities" to "Shell Script Result"
3. Show Notification:
   Title: "🎯 Today's Priorities"
   Body: "Priorities"
```

### How to Create

1. Open Shortcuts app
2. Create new shortcut: "PKM Daily Nudge"
3. Add actions:
   - **Run Shell Script** → Script: `/usr/bin/python3 ~/.claude/skills/pkm/nudge.py`
     - Shell: `/bin/zsh`
   - **Set Variable** → Name: "Priorities", Value: "Shell Script Result"
   - **Show Notification**
     - Title: "🎯 Today's Priorities"
     - Body: "Priorities" variable

### Trigger Configuration

**Time Automation**:
1. Open Shortcuts app → Automation tab
2. Click "+" → "Time of Day"
3. Set time: 8:00 AM
4. Repeat: Daily
5. Run Immediately: ON
6. Notify When Run: OFF (notification is built-in)
7. Select "PKM Daily Nudge" shortcut

**Manual Triggers**:
- Siri: "Hey Siri, Daily Nudge"
- Menu Bar: Pin shortcut for quick access
- Widget: Add to Today View

---

## 3. Sort Inbox

**Purpose**: Background inbox processing - runs every 15 min when idle

### Shortcut Actions

```
1. Run Shell Script:
   /usr/bin/python3 ~/.claude/skills/pkm/sorter.py
2. Set variable "Results" to "Shell Script Result"
3. If "Results" contains "Processed:"
   → Show Notification:
     Title: "PKM Inbox Sorted"
     Body: Extract count from "Results"
```

### How to Create

1. Open Shortcuts app
2. Create new shortcut: "PKM Sort Inbox"
3. Add actions:
   - **Run Shell Script** → Script: `/usr/bin/python3 ~/.claude/skills/pkm/sorter.py`
   - **Set Variable** → Name: "Results", Value: "Shell Script Result"
   - **If** → "Results contains 'Processed:'"
   - **Get Text** → Extract using regex: `Processed: (\d+)`
   - **Show Notification** → Title: "PKM Sorted", Body: "Results" (truncated to 100 chars)

### Trigger Configuration

**Time Automation (Idle Only)**:
1. Open Shortcuts app → Automation tab
2. Click "+" → "Time of Day"
3. Set interval: Every 15 minutes
4. Time Range: 9:00 AM - 6:00 PM (work hours)
5. Repeat: Weekdays
6. **Important**: Run only when Mac is unlocked and idle
7. Select "PKM Sort Inbox" shortcut

**Manual Triggers**:
- Siri: "Hey Siri, Sort Inbox"
- Keyboard: Assign `⌘⇧S`

**Note**: For true idle detection, consider using `launchd` with idle timer instead:

```bash
# ~/.pkm/sort-on-idle.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pkm.sort-idle</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/.claude/skills/pkm/sorter.py</string>
    </array>
    <key>StartInterval</key>
    <integer>900</integer>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

---

## 4. Quick Review

**Purpose**: Open review queue for manual correction of low-confidence items

### Shortcut Actions

```
1. Run Shell Script:
   /usr/bin/python3 ~/.claude/skills/pkm/review.py
2. Set variable "ReviewQueue" to "Shell Script Result"
3. Show Result:
   "ReviewQueue" in large text format
4. If "ReviewQueue" contains "items needing review"
   → Open URL: "notes://show"
```

### How to Create

1. Open Shortcuts app
2. Create new shortcut: "PKM Review Queue"
3. Add actions:
   - **Run Shell Script** → Script: `/usr/bin/python3 ~/.claude/skills/pkm/review.py`
   - **Set Variable** → Name: "ReviewQueue", Value: "Shell Script Result"
   - **Show Result** → Display "ReviewQueue" in large text
   - **If** → "ReviewQueue contains 'items needing review'"
   - **Open URL** → URL: `notes://` (opens Apple Notes)

### Trigger Configuration

**Siri**:
- "Hey Siri, Review Queue"
- "Hey Siri, PKM Review"

**Focus Mode**:
1. Settings → Focus → Work
2. Add Smart Activation: "When using Notes app"
3. Add Automation: Run "PKM Review Queue" on focus start

**Menu Bar**:
- Pin shortcut for quick access during review sessions

**Keyboard**:
- Assign `⌘⇧R` for rapid review workflow

---

## Advanced Integration

### Capture from Safari

**Purpose**: Save articles with metadata

1. Create shortcut "PKM Save Article"
2. Actions:
   - Get **URLs** from Safari Web Page
   - Get **Name** from Safari Web Page
   - Get **Selection** from Safari Web Page
   - Combine Text:
     ```
     [Name]
     URL: [URLs]

     [Selection]
     ```
   - Run Shell Script: `/usr/bin/python3 ~/.claude/skills/pkm/capture.py "Combined Text"`
3. Enable in Share Sheet

### Capture Voice Memos

**Purpose**: Transcribe and capture voice notes

1. Create shortcut "PKM Voice Capture"
2. Actions:
   - **Dictate Text** → Language: English
   - **Set Variable** → Name: "Transcription"
   - **Run Shell Script**: `/usr/bin/python3 ~/.claude/skills/pkm/capture.py "Transcription"`
3. Trigger: Siri phrase or Back Tap (Settings → Accessibility → Touch)

### Daily Summary

**Purpose**: End-of-day review notification

1. Create shortcut "PKM Daily Summary"
2. Actions:
   - **Run Shell Script**: `cat ~/.pkm/log.md | tail -20`
   - **Show Notification**: Title: "PKM Daily Summary", Body: Last 20 log entries
3. Automation: 6:00 PM daily

---

## Permissions Required

When first running shortcuts, macOS will prompt for:

1. **Automation** → Allow Shortcuts to run scripts
2. **Files & Folders** → Allow access to `~/.claude/` directory
3. **Apple Events** → Allow Shortcuts to control Notes app
4. **Notifications** → Allow Shortcuts to show notifications

Grant all permissions for full functionality.

---

## Troubleshooting

### "Permission Denied" errors

**Issue**: Shell script can't access Python files

**Fix**:
1. Open Terminal
2. Run: `chmod +x ~/.claude/skills/pkm/*.py`
3. Verify: `ls -la ~/.claude/skills/pkm/`

### "No module named 'utils'" errors

**Issue**: Python can't find skill modules

**Fix**: Update Shell Script action to:
```bash
cd ~/.claude/skills/pkm && /usr/bin/python3 capture.py "Content"
```

### Automation not triggering

**Issue**: Time-based automation not running

**Check**:
1. Settings → Screen Time → Off (can block automations)
2. Shortcuts app Preferences → Enable "Private Sharing"
3. System Settings → Notifications → Shortcuts → Allow notifications

### Capture not saving to Inbox

**Issue**: Notes folder doesn't exist

**Fix**:
1. Open Terminal
2. Run: `python3 ~/.claude/skills/pkm/utils.py` (creates folders)
3. Verify in Apple Notes app

---

## Best Practices

### 1. Start Simple
- Install Universal Capture first
- Use for 1 week before adding automations
- Build habit of quick capture

### 2. Tune Automation Frequency
- Daily Nudge: 8 AM works for most
- Sort Inbox: Adjust based on capture volume
- High capture → More frequent sorting (every 30 min)
- Low capture → Less frequent (2x daily)

### 3. Review Regularly
- End of day: Quick scan of Processing folder
- End of week: Run full review queue
- End of month: Archive completed projects

### 4. Combine with Focus Modes
- Work Focus → Enable Daily Nudge + Sort Inbox
- Personal Focus → Disable work automations
- Sleep Focus → Disable all PKM notifications

---

## Related Documentation

- **[SKILL.md](SKILL.md)** - Full PKM skill documentation
- **[README.md](README.md)** - Quick start guide
- **Apple Shortcuts Guide**: https://support.apple.com/guide/shortcuts-mac

---

**Version**: 1.0
**Last Updated**: 2026-01-25
**Compatibility**: macOS 12+ (Monterey and later)

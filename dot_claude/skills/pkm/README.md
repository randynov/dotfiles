# PKM (Personal Knowledge Management) Skill

AI-powered "Second Brain" for Apple Notes using the `memo` CLI.

## Quick Start

### 1. Setup (One-Time)
```bash
python3 ~/.claude/skills/pkm/utils.py
```

Creates these folders in Apple Notes:
- **Inbox** - Raw captures
- **Processing** - AI-sorted items
- **Projects** - Active goals
- **Areas** - Life domains
- **Resources** - Reference material
- **Archives** - Completed items
- **_System** - Templates

### 2. Capture Notes
```bash
python3 ~/.claude/skills/pkm/capture.py "Meeting with Sarah about Q1 goals"
```

### 3. Sort Inbox (AI Classification)
```bash
python3 ~/.claude/skills/pkm/sorter.py
```

### 4. Daily Nudge
```bash
python3 ~/.claude/skills/pkm/nudge.py
```

### 5. Review Queue
```bash
python3 ~/.claude/skills/pkm/review.py
```

## Templates

Create structured notes:
```bash
python3 ~/.claude/skills/pkm/templates.py project "Build PKM Skill" Projects
python3 ~/.claude/skills/pkm/templates.py meeting "Weekly Standup" Processing
python3 ~/.claude/skills/pkm/templates.py idea "AI-powered task router" Processing
```

## Logs

Activity logs: `~/.pkm/log.md`

```bash
cat ~/.pkm/log.md
```

## Architecture

Based on 8 Building Blocks:
1. **Drop Box** → `capture.py`
2. **Sorter** → `sorter.py`
3. **Form** → `templates.py`
4. **Filing Cabinet** → Apple Notes folders
5. **Receipt** → `~/.pkm/log.md`
6. **Bouncer** → Confidence filtering in sorter
7. **Tap on Shoulder** → `nudge.py`
8. **Fix Button** → `review.py`

## Apple Intelligence Integration

**AI-Powered Classification** (when server running):
- Uses on-device Apple Intelligence for privacy
- Server: https://github.com/gety-ai/apple-on-device-openai
- Port: 11535 (default)

**Automatic Fallback**:
- If AI server unavailable → keyword heuristics
- Logs show `[AI]` or `[FALLBACK]` for transparency

**Check AI Status:**
```bash
python3 ~/.claude/skills/pkm/ai_client.py
```

**Start AI Server** (if not running):
1. Download from GitHub releases
2. Launch app, set port 11535
3. Click "Start Server"

---

## Troubleshooting

**Capture not working?**
- Ensure "Inbox" folder exists in Apple Notes
- Grant AppleScript permissions when prompted

**AI not being used?**
- Check if server running: `curl http://127.0.0.1:11535/v1/models`
- System automatically falls back to keywords
- Check logs for `[AI]` vs `[FALLBACK]`: `cat ~/.pkm/log.md | tail -5`

**Low confidence classifications?**
- AI server may be down (check above)
- Notes without content default to 40% confidence
- Review queue: `pkm-review`

## Next Steps

1. Add cron job for daily nudge:
   ```bash
   # Run at 8 AM daily
   0 8 * * * python3 ~/.claude/skills/pkm/nudge.py
   ```

2. Create aliases in `~/.zshrc`:
   ```bash
   alias pkm-capture="python3 ~/.claude/skills/pkm/capture.py"
   alias pkm-sort="python3 ~/.claude/skills/pkm/sorter.py"
   alias pkm-nudge="python3 ~/.claude/skills/pkm/nudge.py"
   ```

---

**Version**: 1.0
**Status**: Phase 1 Complete (Foundation)

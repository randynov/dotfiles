#!/usr/bin/env python3
"""
PKM Capture - Frictionless note capture (Building Block 1: Drop Box)

Implements Principle 1: One Reliable Human Behavior
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Add skill directory to path for imports
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from utils import MemoWrapper, PKMLogger


def capture(content: str) -> bool:
    """
    Capture content to Inbox folder

    Args:
        content: Note content to capture

    Returns:
        True if successful
    """
    if not content or not content.strip():
        print("❌ Cannot capture empty note")
        return False

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"INBOX - {timestamp}"

    # Format note content with metadata
    note_body = f"""#capture

{content}

---
Captured: {timestamp}
"""

    # Use AppleScript since memo CLI doesn't support content
    applescript = f'''
tell application "Notes"
    tell folder "Inbox"
        make new note with properties {{name:"{title}", body:"{note_body}"}}
    end tell
end tell
'''

    try:
        subprocess.run(
            ["osascript", "-e", applescript],
            check=True,
            capture_output=True
        )

        PKMLogger.log("CAPTURE", f"Added to Inbox: {content[:50]}...")
        print(f"✅ Captured: {content[:50]}...")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Capture failed: {e}")
        print("   Make sure 'Inbox' folder exists in Apple Notes")
        return False


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: pkm capture <content>")
        print("\nExample:")
        print('  pkm capture "Meeting notes with Sarah about Q1 planning"')
        sys.exit(1)

    # Join all arguments as content
    content = ' '.join(sys.argv[1:])
    capture(content)


if __name__ == "__main__":
    main()

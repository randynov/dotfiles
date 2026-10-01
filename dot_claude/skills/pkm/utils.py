#!/usr/bin/env python3
"""
PKM Utilities - Memo CLI wrapper and logging utilities
"""

import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# PKM folder structure
PKM_FOLDERS = [
    "Inbox",
    "Processing",
    "Projects",
    "Areas",
    "Resources",
    "Archives",
    "_System"
]

# Log file location
LOG_DIR = Path.home() / ".pkm"
LOG_FILE = LOG_DIR / "log.md"


def strip_html(html: str) -> str:
    """
    Strip HTML tags from note content

    Args:
        html: HTML string from Apple Notes

    Returns:
        Plain text with HTML tags removed
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', html)
    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    # Clean up whitespace
    text = ' '.join(text.split())
    return text.strip()


class MemoWrapper:
    """Wrapper for memo CLI operations"""

    def __init__(self):
        self.ensure_log_dir()

    def ensure_log_dir(self):
        """Create log directory if it doesn't exist"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not LOG_FILE.exists():
            LOG_FILE.write_text("# PKM Activity Log\n\n")

    def run_command(self, args: List[str], timeout: int = 10) -> Tuple[bool, str]:
        """
        Run memo CLI command

        Returns:
            (success: bool, output: str)
        """
        try:
            result = subprocess.run(
                ["memo"] + args,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def list_folders(self) -> List[str]:
        """List all folders in Apple Notes via AppleScript"""
        applescript = 'tell application "Notes" to get name of every folder'

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            # Parse comma-separated list
            folders = [f.strip() for f in result.stdout.split(',')]
            return folders

        except Exception as e:
            print(f"Failed to list folders: {e}")
            return []

    def list_notes(self, folder: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List notes via AppleScript (memo CLI is too slow)

        Returns:
            List of dicts with 'folder', 'title'
        """
        if folder:
            applescript = f'tell application "Notes" to get name of every note of folder "{folder}"'
        else:
            applescript = 'tell application "Notes" to get name of every note'

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )

            # Parse comma-separated list
            note_names = [n.strip() for n in result.stdout.split(',') if n.strip()]

            notes = []
            for i, title in enumerate(note_names, 1):
                notes.append({
                    'number': str(i),
                    'folder': folder if folder else 'Unknown',
                    'title': title
                })

            return notes

        except Exception as e:
            print(f"Failed to list notes: {e}")
            return []

    def get_note_content(self, note_title: str, folder: str) -> str:
        """
        Get full content/body of a note via AppleScript

        Args:
            note_title: Exact note title
            folder: Folder name where note is located

        Returns:
            Note body content (HTML), or empty string on error
        """
        applescript = f'''
tell application "Notes"
    get body of note "{note_title}" of folder "{folder}"
end tell
'''

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            print(f"Timeout reading note: {note_title}")
            return ""
        except subprocess.CalledProcessError as e:
            print(f"Failed to read note '{note_title}' in '{folder}': {e.stderr}")
            return ""
        except Exception as e:
            print(f"Error reading note: {e}")
            return ""

    def add_note(self, folder: str, title: str, content: str = "") -> bool:
        """Add a note to specified folder"""
        # memo CLI doesn't support content in add - need to use AppleScript
        # For now, just add title and user can edit
        success, _ = self.run_command(["notes", "-a", "-f", folder])
        return success

    def move_note(self, note_title: str, from_folder: str, to_folder: str) -> bool:
        """
        Move a note from one folder to another via AppleScript

        Args:
            note_title: Exact note title
            from_folder: Source folder name
            to_folder: Destination folder name

        Returns:
            True if successful, False otherwise
        """
        applescript = f'''
tell application "Notes"
    move note "{note_title}" of folder "{from_folder}" to folder "{to_folder}"
end tell
'''

        try:
            subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            return True
        except subprocess.TimeoutExpired:
            print(f"Timeout moving note: {note_title}")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Failed to move note '{note_title}': {e.stderr}")
            return False
        except Exception as e:
            print(f"Error moving note: {e}")
            return False

    def search_notes(self, query: str) -> List[Dict[str, str]]:
        """Fuzzy search notes"""
        success, output = self.run_command(["notes", "-s"])
        # Interactive search - returns notes matching query
        return []


class PKMLogger:
    """Logging utilities for PKM actions"""

    @staticmethod
    def log(action: str, details: str, confidence: Optional[int] = None):
        """
        Log an action to the activity log

        Args:
            action: Action type (CAPTURE, SORT, MOVE, etc.)
            details: Description of what happened
            confidence: Optional confidence score (0-100)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"**{timestamp}** | `{action}`"
        if confidence is not None:
            log_entry += f" | Confidence: {confidence}%"
        log_entry += f" | {details}\n"

        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)

    @staticmethod
    def get_recent_logs(limit: int = 20) -> str:
        """Get recent log entries"""
        if not LOG_FILE.exists():
            return "No logs yet."

        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        # Get last N lines (excluding header)
        recent = lines[-limit:] if len(lines) > limit else lines[2:]
        return ''.join(recent)


def setup_folders():
    """Create PKM folder structure in Apple Notes"""
    memo = MemoWrapper()
    existing_folders = memo.list_folders()

    print("📂 Setting up PKM folder structure...\n")

    for folder in PKM_FOLDERS:
        if folder in existing_folders:
            print(f"✓ {folder} (already exists)")
        else:
            print(f"Creating: {folder}")

            # Use AppleScript to create folder
            applescript = f'''
tell application "Notes"
    make new folder with properties {{name:"{folder}"}}
end tell
'''

            try:
                subprocess.run(
                    ["osascript", "-e", applescript],
                    check=True,
                    capture_output=True,
                    text=True
                )
                PKMLogger.log("SETUP", f"Created folder: {folder}")
                print(f"  ✅ Created {folder}")
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️  Failed: {e.stderr}")
                print(f"     You may need to create '{folder}' manually")

    print("\n✅ Folder setup complete!")
    print(f"📝 Logs: {LOG_FILE}")


if __name__ == "__main__":
    # Test utilities
    setup_folders()

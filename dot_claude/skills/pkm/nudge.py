#!/usr/bin/env python3
"""
PKM Nudge - Daily priority generator (Building Block 7: Tap on the Shoulder)

Implements Principles:
- #6: Small, Frequent, Actionable Outputs
- #7: Use Next Action as Execution Unit
"""

import sys
from pathlib import Path
from datetime import datetime

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from utils import MemoWrapper, PKMLogger
from ai_client import get_ai_client


def generate_nudge():
    """
    Generate top 3 priorities from active projects

    Implements Principle #6: Small, Frequent, Actionable Outputs
    """
    memo = MemoWrapper()

    print("📋 Analyzing active projects...")
    project_notes = memo.list_notes("Projects")

    if not project_notes:
        print("No active projects found.")
        print("💡 Tip: Move project notes to 'Projects' folder")
        return

    # Get project titles
    project_titles = [note['title'] for note in project_notes[:10]]

    # Try Apple Intelligence
    ai_client = get_ai_client()

    if ai_client.available:
        try:
            response = ai_client.prioritize(project_titles)

            print(f"\n🎯 Today's Top 3 Priorities ({datetime.now().strftime('%Y-%m-%d')}) [AI]:\n")
            print(response)
            print("\n---")

            PKMLogger.log("NUDGE", f"AI generated daily priorities ({len(project_notes)} projects analyzed)")
            return

        except Exception as e:
            print(f"⚠️  AI nudge failed: {e}")

    # Fallback: just list projects
    print(f"\n🎯 Active Projects ({datetime.now().strftime('%Y-%m-%d')}) [FALLBACK]:\n")
    for i, note in enumerate(project_notes[:3], 1):
        print(f"{i}. {note['title']}")
    print("\n---")

    PKMLogger.log("NUDGE_FALLBACK", f"Listed {len(project_notes)} active projects (AI unavailable)")


def main():
    """CLI entry point"""
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: pkm nudge")
        print("\nGenerate top 3 priorities from active projects")
        print("Runs daily to keep you focused on what matters")
        sys.exit(0)

    generate_nudge()


if __name__ == "__main__":
    main()

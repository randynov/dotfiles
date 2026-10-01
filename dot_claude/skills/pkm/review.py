#!/usr/bin/env python3
"""
PKM Review - Manual correction interface (Building Block 8: Fix Button)

Implements Principle #10: Design for Restart, Not Perfection
"""

import sys
from pathlib import Path

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from utils import MemoWrapper, PKMLogger, LOG_FILE


def show_review_queue():
    """
    Show items that need manual review
    """
    print("📋 Review Queue\n")

    # Read recent logs to find items needing review
    if not LOG_FILE.exists():
        print("No items need review!")
        return

    with open(LOG_FILE, 'r') as f:
        logs = f.readlines()

    # Find NEEDS_REVIEW entries
    review_items = []
    for line in logs:
        if "NEEDS_REVIEW" in line:
            review_items.append(line.strip())

    if not review_items:
        print("✅ No items need review!")
        return

    print(f"Found {len(review_items)} items needing review:\n")
    for i, item in enumerate(review_items[-10:], 1):  # Show last 10
        print(f"{i}. {item}")

    print("\n💡 Next steps:")
    print("   1. Open Apple Notes")
    print("   2. Search for items above")
    print("   3. Manually move to correct folder")
    print("   4. Remove #needs-review tag")


def show_recent_activity():
    """
    Show recent PKM activity from logs
    """
    print("📊 Recent PKM Activity\n")

    if not LOG_FILE.exists():
        print("No activity yet!")
        return

    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()

    # Show last 20 entries
    recent = lines[-20:] if len(lines) > 20 else lines[2:]  # Skip header

    for line in recent:
        print(line.rstrip())


def main():
    """CLI entry point"""
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage:")
        print("  pkm review         Show items needing manual review")
        print("  pkm review --all   Show all recent activity")
        sys.exit(0)

    if "--all" in sys.argv:
        show_recent_activity()
    else:
        show_review_queue()


if __name__ == "__main__":
    main()

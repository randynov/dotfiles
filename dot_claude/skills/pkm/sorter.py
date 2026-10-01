#!/usr/bin/env python3
"""
PKM Sorter - AI classification and routing (Building Block 2: Sorter)

Implements Principles:
- #2: Separate Memory, Compute, Interface
- #3: Treat Prompts Like APIs
- #8: Prefer Routing Over Organizing
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from utils import MemoWrapper, PKMLogger, strip_html
from ai_client import get_ai_client

# Classification categories (Principle #9: Keep Categories Painfully Small)
CATEGORIES = {
    "PROJECT": "Projects",
    "TODO": "Processing",
    "IDEA": "Processing",
    "MEETING": "Processing",
    "WAITING": "Processing",
    "RESOURCE": "Resources",
    "SOMEDAY": "Archives",
    "ARCHIVE": "Archives"
}

# Confidence threshold (Principle #5: Default to Safe Behavior)
CONFIDENCE_THRESHOLD = 75


def classify_note(title: str, content: str) -> Dict[str, any]:
    """
    Classify a note using Apple Intelligence AI

    Implements Principle #3: Treat Prompts Like APIs

    Args:
        title: Note title
        content: Note content

    Returns:
        {
            'category': str,
            'confidence': int (0-100),
            'reason': str,
            'method': str ('AI' or 'FALLBACK')
        }
    """
    # Try Apple Intelligence first
    ai_client = get_ai_client()

    if ai_client.available:
        try:
            result = ai_client.classify(title, content)
            result['method'] = 'AI'
            return result
        except Exception as e:
            print(f"⚠️  AI classification failed: {e}")

    # Fallback to keyword heuristics
    result = classify_fallback(title, content)
    result['method'] = 'FALLBACK'
    return result


def classify_fallback(title: str, content: str) -> Dict[str, any]:
    """
    Fallback classification using simple heuristics

    Implements Principle #10: Design for Restart, Not Perfection
    """
    title_lower = title.lower()
    content_lower = content.lower()

    # Simple keyword matching
    if any(word in content_lower for word in ['meeting', 'discussed', 'agenda']):
        return {'category': 'MEETING', 'confidence': 60, 'reason': 'Contains meeting keywords'}

    if any(word in content_lower for word in ['todo', 'task', 'must', 'need to']):
        return {'category': 'TODO', 'confidence': 60, 'reason': 'Contains task keywords'}

    if any(word in content_lower for word in ['http', 'www', 'article', 'read']):
        return {'category': 'RESOURCE', 'confidence': 60, 'reason': 'Contains link/reference'}

    if any(word in content_lower for word in ['idea', 'what if', 'could', 'maybe']):
        return {'category': 'IDEA', 'confidence': 60, 'reason': 'Contains ideation keywords'}

    # Default to TODO for low confidence
    return {'category': 'TODO', 'confidence': 40, 'reason': 'Default classification'}


def sort_inbox():
    """
    Process all notes in Inbox folder

    Implements Building Block 6: The Bouncer (confidence filtering)
    """
    memo = MemoWrapper()

    print("📥 Fetching Inbox notes...")
    inbox_notes = memo.list_notes("Inbox")

    if not inbox_notes:
        print("✅ Inbox is empty!")
        return

    print(f"Found {len(inbox_notes)} notes to process\n")

    low_confidence_count = 0

    for note in inbox_notes:
        title = note['title']
        print(f"Processing: {title[:50]}...")

        # Get full note content for better classification
        content_html = memo.get_note_content(title, "Inbox")
        content = strip_html(content_html)
        result = classify_note(title, content)

        category = result['category']
        confidence = result['confidence']
        reason = result['reason']
        method = result.get('method', 'UNKNOWN')

        # Building Block 6: Bouncer (confidence filter)
        if confidence < CONFIDENCE_THRESHOLD:
            print(f"  ⚠️  Low confidence ({confidence}%) [{method}] - needs manual review")
            PKMLogger.log(
                "NEEDS_REVIEW",
                f"{title[:50]} → {category} ({confidence}%) [{method}] - {reason}",
                confidence
            )
            low_confidence_count += 1
            continue

        # Route to appropriate folder (fallback to Processing for unknown categories)
        target_folder = CATEGORIES.get(category, "Processing")
        if category not in CATEGORIES:
            print(f"  ⚠️  Unknown category '{category}', using Processing")
        print(f"  ✅ {category} ({confidence}%) [{method}] → {target_folder}")

        # Move the note
        if memo.move_note(title, "Inbox", target_folder):
            PKMLogger.log(
                "SORTED",
                f"{title[:50]} → {target_folder} ({confidence}%) [{method}]",
                confidence
            )
        else:
            print(f"  ⚠️  Failed to move note")
            PKMLogger.log(
                "MOVE_FAILED",
                f"{title[:50]} → {target_folder} (move failed)",
                confidence
            )

    print(f"\n📊 Summary:")
    print(f"   Processed: {len(inbox_notes)}")
    print(f"   Needs review: {low_confidence_count}")
    print(f"   Auto-sorted: {len(inbox_notes) - low_confidence_count}")
    print(f"\n📝 Logs: ~/.pkm/log.md")


def main():
    """CLI entry point"""
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: pkm sort")
        print("\nProcess all notes in Inbox folder:")
        print("- AI classifies each note")
        print("- High confidence (≥75%): Auto-route to correct folder")
        print("- Low confidence (<75%): Flag for manual review")
        sys.exit(0)

    sort_inbox()


if __name__ == "__main__":
    main()

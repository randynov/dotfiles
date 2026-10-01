#!/usr/bin/env python3
"""
PKM Templates - Note templates (Building Block 3: The Form)

Implements Principle #3: Treat Prompts Like APIs
"""

import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Add skill directory to path
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from utils import PKMLogger


TEMPLATES = {
    "project": """#project
Status: Active
Goal: [One sentence outcome]
Due: [YYYY-MM-DD]
Next Action: [Specific, physical action]

## Milestones
- [ ] Milestone 1
- [ ] Milestone 2

## Notes
[Project details and context]

---
Created: {timestamp}
""",
    "meeting": """#meeting
Date: {timestamp}
Attendees: [Names]
Topic: [Meeting topic]

## Agenda
1. [Item 1]
2. [Item 2]

## Notes
[Discussion notes]

## Action Items
- [ ] [Action 1] - [Owner]
- [ ] [Action 2] - [Owner]

## Next Steps
[Follow-up actions]
""",
    "idea": """#idea
Category: [Technology/Business/Personal/Other]
Confidence: [1-10]

## Core Idea
[Describe the idea in 2-3 sentences]

## Why This Matters
[Why is this worth exploring?]

## Next Steps
[What's the first action to validate/explore this?]

---
Captured: {timestamp}
""",
    "resource": """#resource
Source: [URL or citation]
Type: [Article/Book/Video/Course/Other]
Tags: [Keywords]

## Summary
[3-5 bullet point summary]

## Key Takeaways
- [Takeaway 1]
- [Takeaway 2]

## Related Notes
[Links to related notes]

---
Saved: {timestamp}
"""
}


def create_from_template(template_name: str, title: str, folder: str = "_System"):
    """
    Create a note from template

    Args:
        template_name: Template to use (project/meeting/idea/resource)
        title: Note title
        folder: Destination folder (default: _System)
    """
    if template_name not in TEMPLATES:
        print(f"❌ Unknown template: {template_name}")
        print(f"   Available: {', '.join(TEMPLATES.keys())}")
        return False

    # Get template content
    template = TEMPLATES[template_name]
    content = template.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Create note via AppleScript
    applescript = f'''
tell application "Notes"
    tell folder "{folder}"
        make new note with properties {{name:"{title}", body:"{content}"}}
    end tell
end tell
'''

    try:
        subprocess.run(
            ["osascript", "-e", applescript],
            check=True,
            capture_output=True
        )

        PKMLogger.log("TEMPLATE", f"Created {template_name}: {title}")
        print(f"✅ Created {template_name} note: {title}")
        print(f"   Location: {folder}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create note: {e}")
        return False


def list_templates():
    """Show available templates"""
    print("📝 Available Templates:\n")
    for name in TEMPLATES.keys():
        print(f"  • {name}")

    print("\nUsage:")
    print('  pkm template <type> "Note Title" [folder]')
    print("\nExamples:")
    print('  pkm template project "Build PKM Skill" Projects')
    print('  pkm template meeting "Q1 Planning" Processing')


def main():
    """CLI entry point"""
    if len(sys.argv) < 2 or "--help" in sys.argv or "-h" in sys.argv:
        list_templates()
        sys.exit(0 if "--help" in sys.argv else 1)

    template_name = sys.argv[1]

    if len(sys.argv) < 3:
        print(f"❌ Missing note title")
        print(f'   Usage: pkm template {template_name} "Note Title" [folder]')
        sys.exit(1)

    title = sys.argv[2]
    folder = sys.argv[3] if len(sys.argv) > 3 else "_System"

    create_from_template(template_name, title, folder)


if __name__ == "__main__":
    main()

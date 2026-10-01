---
name: apple-hig-expert
description: Use when building iOS, iPadOS, macOS, or visionOS interfaces.
  Loads Apple Human Interface Guidelines expertise, including Liquid Glass
  aesthetic, platform-specific spacing, typography, and motion patterns.
  Trigger on any request involving SwiftUI, UIKit, or native Apple UI.
---
# Apple HIG Expert
## When to use this skill
- Building a new native screen or flow for any Apple platform
- Reviewing an existing UI for HIG compliance
- Making platform-specific adaptation decisions
## Core references
- references/liquid-glass.md - current visual language (iOS 26+)
- references/spacing-and-typography.md - SF Symbols, type ramp, hit targets
- references/motion-patterns.md - spring animations, interruption handling
- references/platform-adaptation.md - when to diverge iPhone/iPad/Mac
## Gotchas
- Do not default to Material Design spacing (8pt grid on Apple, not 4pt/8dp)
- SF Pro is the default; fall back to system font, never to Inter or Roboto
- Sheets have three detents on iOS 16+; do not hardcode heights
- `.hoverEffect` only applies on iPadOS and visionOS - gate it properly
- Symbol weights must match surrounding text weight, not accent color

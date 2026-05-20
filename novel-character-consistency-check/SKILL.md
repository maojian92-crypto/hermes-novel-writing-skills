---
name: novel-character-consistency-check
description: Systematic character logic and state consistency checking for long-form Chinese novels. Cross-references character status tracking documents against latest chapters to detect and fix contradictions.
trigger: When user asks to "核实人物逻辑", "检查人物一致性", "review character logic", or when completing a batch of novel chapters that may have character state changes.
---

# 小说人物逻辑一致性检查 Skill

## Purpose
For long-running Chinese web novels (50+ chapters), character states evolve continuously — injuries, ability awakenings, equipment changes, relationships. This skill provides a systematic workflow to detect and fix contradictions between the "official" character status tracking document and the actual chapter text.

## Prerequisites
- A character status tracking document (e.g., `02-团队成员状态跟踪.md`)
- A character outline document (e.g., `00-角色与大纲梳理.md`)
- The latest chapter files to review

## Workflow

### Phase 1: Load Character Status Documents
Read both documents to extract the current canonical state of every character:
- **Physical state**: injuries, disabilities, equipment condition
- **Ability state**: current level, skills available/unavailable
- **Mental state**: consciousness, consciousness level
- **Resource state**: ammunition, consumables, charges

**Critical**: Pay special attention to the "common logic traps" section if present — these are known recurring issues (e.g., "林月已失明，不能用'眼睛'描述她的视觉").

### Phase 2: Read Latest Chapters
Read the chapters to be reviewed. For each chapter, note every physical action, dialogue cue, and visual description involving tracked characters.

### Phase 3: Cross-Reference Checklist
For each character, verify these categories:

| Check Category | Example Contradiction |
|---|---|
| **Physical capability** | Character with destroyed prosthetic arm described as "waving mechanical arm" |
| **Sensory ability** | Blind character described as "eyes looking at me" |
| **Resource availability** | Character with exhausted ammo described as "shooting arrows" |
| **Vitality state** | Character at death's edge described as "standing and fighting" |
| **Ability availability** | Character mid-breakthrough described as using full power |
| **Name consistency** | Character called "毛子" instead of "墨子" |
| **Equipment condition** | Destroyed item described as functional |

### Phase 4: Document Findings
Create a findings table:
```
| Chapter | Character | Issue | Severity | Fix |
```
Severity: `critical` (breaks canon), `moderate` (needs adjustment), `minor` (typo/wording)

### Phase 5: Batch Fix
Apply fixes using `patch` tool. Prioritize:
1. **Critical**: Physical/sensory/resource contradictions first
2. **Moderate**: Ability state and equipment issues
3. **Minor**: Typos and name errors

**Fix principles**:
- Don't change the scene's narrative intent — adjust the physical description to match the canonical state
- For disabled characters, replace visual verbs with non-visual alternatives ("脸转向" instead of "眼睛看着")
- For resource-depleted characters, describe intent/frustration instead of successful action
- For濒死 characters, emphasize willpower/consciousness over physical action

### Phase 6: Re-verify
Search for any remaining instances of the corrected terms to ensure no residuals.

## Key Lessons Learned
1. **Status tracking docs are living documents** — they should be updated after every major batch of chapters
2. **One fix reveals another** — after fixing "mechanical arm", search for all variants ("机械手臂", "义肢", "prosthetic")
3. **Context matters for transitions** — a character going from "unconscious" to "awake" needs a believable transition scene or medical justification
4. **Team scenes are high-risk** — when multiple characters appear together, the chance of contradicting someone's status increases exponentially
5. **Re-scan is mandatory** — after bulk replacements, always grep for the old terms to catch residuals
6. **Group descriptions hide individual contradictions** — Phrases like "八双眼睛看着我" or "全员站起来战斗" are danger zones. When even one team member is unconscious, blind, or crippled, the group description becomes a lie. Always audit collective nouns against every individual in the group.
7. **Destroyed equipment has many faces** — A broken item can still be described as "手里的枪" or "身上的盔甲", but it must NOT be described as functional ("发出低鸣", "有东西在流动", "进入了战斗状态"). The line between possession and function is where contradictions hide.

## Common Pitfalls
- **Over-correction**: Don't remove all visual descriptions from a blind character's POV — they can still "perceive" through other senses
- **Under-correction**: A single scene with 3 contradictions needs 3 separate fixes, not 1
- **Ignoring minor characters**: Even background characters' equipment states matter if they reappear
- **Forgetting resource tracking**: Ammunition, potions, and special charges are easy to forget between chapters
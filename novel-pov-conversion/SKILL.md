---
name: novel-pov-conversion
description: Convert novel chapters from first-person ("我") to third-person (character name / "他/她") perspective while preserving dialogue integrity.
trigger: When user discovers POV inconsistency in novel chapters, or requests to convert first-person narration to third-person.
---

# 小说人称视角转换 Skill

## Purpose
Convert novel chapters from first-person perspective (第一人称 "我") to third-person perspective (第三人称 "主角名"/"他"), ensuring narrative consistency with existing chapters.

## When to Use
- POV inconsistency detected (e.g., chapter 41-42 suddenly switch to "我" while chapters 1-40 use third-person)
- User explicitly requests POV conversion
- Batch rewrite requires unified perspective

## Prerequisites
- Identify the protagonist's name (e.g., 林辰 / 林夜 / etc.)
- Confirm target chapters to convert
- Verify existing chapters use third-person consistently

## Workflow

### Phase 1: Identify Problem Scope
1. Check sample chapters to confirm the existing POV pattern
2. Identify which chapters deviate from the pattern
3. Count occurrences of "我" in target chapters to estimate scope

### Phase 2: Bulk Replacement (Two-Pass Approach)

**Strategy: Protect dialogue, replace narrative only.** Chinese web novels frequently mix narration and dialogue on the same line, making simple line-based rules insufficient.

#### Pass 1: Pure Narrative Lines (no quotes)
For lines without any quotation marks (`"`, `"`, `"`):
- Replace all pronouns unconditionally:
  - "我" → "{主角名}"
  - "我的" → "{主角名}的"
  - "我们" → "他们"
  - "我们的" → "他们的"

#### Pass 2: Mixed Lines (contain quotes)
For lines with quotation marks, protect dialogue content before replacing:
1. Extract all quoted substrings using regex: `r'"[^"]*"'` and `r'"[^"]*"'`
2. Replace each quoted substring with a unique placeholder (e.g., `__DIALOGUE_0__`)
3. Apply the same replacement rules to the remaining text (now only narrative)
4. Restore placeholders back to original quoted content

**Implementation sketch:**
```python
def protect_dialogue(line):
    placeholders = {}
    counter = [0]
    def make_ph(match):
        ph = f"__DIALOGUE_{counter[0]}__"
        placeholders[ph] = match.group(0)
        counter[0] += 1
        return ph
    protected = re.sub(r'"[^"]*"', make_ph, line)
    protected = re.sub(r'"[^"]*"', make_ph, protected)
    return protected, placeholders

# Then: replace "我"→"{主角名}" etc. on protected line
# Then: restore placeholders
```

### Phase 3: Dialogue Tag Cleanup
Convert dialogue tags from first-person to third-person:
- `"..." 我说` → `"..." 他说` or `"..." {主角名}说`
- `"..." 我问` → `"..." 他问`
- `"..." 我打断他` → `"..." 他打断他`

### Phase 4: Fix Repetitive References
Fix consecutive references to protagonist:
- ❌ `{主角名}没再说话。{主角名}在想观察者。` 
- ✅ `{主角名}没再说话。他在想观察者。`

- ❌ `{主角名}知道，观察者在看。{主角名}也知道`
- ✅ `{主角名}知道，观察者在看。他也知道`

**Note:** For large-scale batch processing (100+ chapters), using only the character name ("{主角名}") rather than alternating with "他" is simpler and less error-prone. A final cleanup pass can alternate names if needed.

### Phase 5: Automated Validation
Build a script to verify no narrative "我" remains:
```python
def find_wo_outside_quotes(line):
    temp = re.sub(r'"[^"]*"', '', line)  # remove English quotes
    temp = re.sub(r'"[^"]*"', '', temp)  # remove Chinese quotes
    return "我" in temp
```
Run this across all converted chapters. **Target: 0 residual "我" outside quotes.**

### Phase 6: Context-Specific Fixes
- `"找我"` in dialogue should remain `"找我"`, not `"找{主角名}"`
- `"我心里有数"` → preserve as dialogue, not `"{主角名}心里有数"`
- References to protagonist in other characters' dialogue stay as "你"

### Phase 7: Manual Spot-Check
Sample-check key chapters (beginning, middle, end of converted range) to verify:
- Narrative flows naturally in third person
- Dialogue still feels authentic
- No accidental replacements in quoted text

## Common Pitfalls

1. **Mixed narration/dialogue lines**: Chinese web novels frequently combine narration and dialogue on the same line (e.g., `我抓紧通讯石，语速飞快："我负责中央区。"`). Simple line-based rules will corrupt dialogue or miss narrative text.
   - **Fix**: Use placeholder protection to isolate quoted content before replacement (see Pass 2 in Phase 2)

2. **Over-replacement in dialogue**: Accidentally converting `"我来了"` to `"{主角名}来乎"` in dialogue
   - **Fix**: Dialogue must preserve character's natural speech

3. **Dialogue tag confusion**: `"你好" 我说` becomes `"你好" {主角名}说` but should be `"你好" 他说`
   - **Fix**: Use "他" for dialogue tags unless emphasizing identity

4. **Third-person reference in dialogue**: `"{主角名}知道"` in dialogue should be `"我知道"`
   - **Fix**: Characters refer to themselves as "我", not by name

5. **Consecutive protagonist references**: Multiple "{主角名}" in close proximity reads awkwardly
   - **Fix**: Alternate between name and pronoun: "{主角名}... 他... 他..."

6. **Ambiguous "他" references**: When multiple male characters present, "他" may be unclear
   - **Fix**: Use "{主角名}" explicitly when context could confuse

7. **Scale-related issues**: With 100+ chapters, manual line-by-line checking is impossible
   - **Fix**: Build automated validation scripts (see Phase 5) to catch residual narrative "我"

## Example Conversion

**Original (First-person):**
```
我站在营地边缘。老刀走到我身边。
"一个人去？"老刀问。
"嗯。"我检查了一下装备栏，"如果我天亮之前没回来，你就是团长。"
我拍了拍他的肩膀，转身走入晨雾中。
```

**Converted (Third-person):**
```
{主角名}站在营地边缘。老刀走到他身边。
"一个人去？"老刀问。
"嗯。"{主角名}检查了一下装备栏，"如果我天亮之前没回来，你就是团长。"
他拍了拍老刀的肩膀，转身走入晨雾中。
```

## Key Lessons Learned

1. **Preserve dialogue at all costs** — Natural speech patterns are harder to fix than narrative
2. **Batch replace then surgical fix** — Broad strokes first, then specific line-by-line corrections
3. **Context-aware pronouns** — "他" vs "{主角名}" choice depends on clarity needs
4. **Multiple passes required** — One replacement pass is never enough; expect 3-5 refinement cycles
5. **Verify dialogue tags separately** — Dialogue tags are easy to miss but crucial for flow
6. **Mixed lines are the hardest** — Lines blending narration and dialogue require placeholder protection technique
7. **Automated validation is essential at scale** — For 100+ chapters, scripts must verify zero narrative residuals
8. **Regex-based quote extraction** — Handle both Chinese ("“"”) and English ("") quotes; they often coexist in web novels
9. **Order of replacement matters** — Replace "我们的" before "我们", and "我们" before "我" to avoid partial matches
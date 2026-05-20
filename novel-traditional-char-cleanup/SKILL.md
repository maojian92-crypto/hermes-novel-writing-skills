---
title: Traditional/Simplified Chinese Novel Text Cleanup
name: novel-traditional-char-cleanup
description: |
  Systematic workflow for scanning and fixing traditional Chinese characters,
  typos, and OCR errors in novel manuscripts. Handles false positives,
  multi-round replacement, and verification.
triggers:
  - cleaning up fanjian (繁简转换) in novel chapters
  - fixing OCR errors in Chinese novel text
  - scanning novel manuscripts for typos
  - batch replacing traditional characters in novels
---

# Traditional/Simplified Chinese Novel Text Cleanup

## Problem
Novel manuscripts (especially those converted from traditional Chinese sources or OCR'd) often contain:
- Traditional characters mixed with simplified text
- OCR errors (wrong characters with similar shapes)
- Voice-input errors (homophone substitutions)
- Encoding artifacts

## Workflow

### Phase 1: Discovery Scan
1. **List all chapter files** and sort them
2. **Build a proper fan→jian mapping table** that ONLY includes characters where simplified and traditional forms are **actually different**:
   - WRONG: `{'去': '去', '的': '的'}` (same character, false positive)
   - RIGHT: `{'隊': '队', '總': '总', '愛': '爱'}`
3. **Scan each chapter** for occurrences
4. **Generate a report** grouped by chapter

### Phase 2: Multi-Round Replacement
For chapters with heavy contamination (like Chapter 34 in the reference case):

**Round 1**: Replace the most common multi-character words first
- `'著': '着'`, `'什麼': '什么'`, `'則': '则'` etc.
- This catches the bulk of issues

**Round 2**: Replace remaining single-character traditional forms
- `'樣': '样'`, `'緩': '缓'`, `'輕': '轻'`, `'鐵': '铁'` etc.
- Must skip characters where 繁体==简体

**Round 3**: Fix specific known typos/errors
- `'人壤': '人员'`, `'力握': '用力握'`, `'大刺': '大幅'` etc.
- These are often OCR/voice-input errors, not simple 繁简 conversion

### Phase 3: Edge Case Handling

#### Substring False Positives
`'力握'` appears inside `'用力握'`. Use context-aware checks:
```python
if '力握' in line and '用力握' not in line:
    # This is a real standalone error
```

#### Uncertain Errors
Some errors cannot be definitively fixed:
- `'稀罕彩盤'` — likely OCR corruption, original text unrecoverable
- `'榴精'` — possibly `'妖精'`, `'榨取'`, or `'流尽'`; mark for author review

**Rule**: When uncertain, flag rather than guess. Log ambiguous items for human confirmation.

## Phase 4: Verification
1. Re-scan all chapters with the same mapping table
2. Confirm zero issues remain (except flagged uncertain items)
3. Read key passages manually to verify fluency

## Extended Error Patterns (Voice / OCR / Context)
Beyond simple traditional→simplified conversion, novel manuscripts often contain these error types:

| Error Type | Examples | Detection Strategy |
|---|---|---|
| 语音输入同音字 | 住高→柱高, 早霞→朝霞, 蛋光→淡光, 弧欢→弧光 | Look for semantically odd homophones in context |
| 形近字误用 | 壹嘴→插嘴, 筂起→皱起, 异冷→冷却 | Characters with similar shapes but wrong meaning |
| 重复/多余字 | 甩用用力握→用力握, 多多缺点→诸多缺点 | Redundant characters breaking fluency |
| 日语借词混入 | 弊害→危害, 何况→何况 | Japanese loanwords in Chinese text |
| OCR断字/上下文裂变 | 频殷→偏弱, 大刺→大幅, 邱市→部分 | Nonsensical character combinations |
| 语义不明无法恢复 | 稀罕彩盤, 榴精 | Flag for author review, do NOT guess |

### Handling Uncertain Errors
When encountering errors whose correct form cannot be determined from context:
- **Flag, don't guess** — Log the item with line number and surrounding context
- **Mark as `[TODO]`** in the text or in a separate review log
- **Examples from real cleanup**:
  - `'稀罕彩盤'` — likely severe OCR corruption, original unrecoverable
  - `'榴精'` — possibly `妖精`, `榨取`, or `流尽`; mark for author confirmation

## Key Pitfalls
1. **Don't over-detect**: `城、墨、淬、混、淹` are valid simplified characters.
2. **Check Unicode**: `消敓`(U+6553) vs `消散`(U+6563) are visually identical in some fonts but different codepoints.
3. **Context matters for metaphors**: A cute squirrel metaphor is fine in slice-of-life, but ruins tension in a climactic scene.
4. **Iterative scanning**: One pass is never enough. Re-scan after fixes to catch residuals and false positives.
5. **Homophone traps**: Voice input often produces valid characters with wrong meanings — always check semantic fit.
6. **Redundant character check**: Read aloud to catch stuttering repetition like `甩用用力握`.
7. **Filenames are NOT safe from replacement** — When doing bulk `str.replace()` across chapter files, **filename strings in code literals can also be corrupted**. Example: if `'渊'`→`'渏'` is in your mapping, a Python string literal `'第101章-深渊而来.md'` will become `'第101章-深渏而来.md'`, breaking file access. **Always** use `os.listdir()` to discover actual filenames dynamically, never hardcode them after running bulk replacement.
8. **read_file tool has filename limitations** — For files with certain Chinese characters in their names, the `read_file` tool may fail to locate them even when the filename appears correct. If `read_file` returns "File not found" for an existing file, use `execute_code` with Python (`os.listdir()` + `open()`) instead.
9. **Verify your mapping table first** — A bad entry like `'歼': '毁'` will corrupt valid simplified text. Filter the map: `fanjian_map = {k: v for k, v in fanjian_map.items() if k != v}`
10. **OCR errors != traditional characters** — Some chapters may have ZERO traditional characters but severe OCR corruption (e.g. `凵犄` for `龟裂`, `柴柴` for `柄柄`). A clean 繁简 scan does NOT mean the text is clean. Always spot-read heavily contaminated chapters.
11. **Visually identical but byte-different characters** — Some characters look nearly identical but have different Unicode codepoints. Example: `渊` (U+6E0A, \xe6\xb8\x8a) vs `渏` (U+6E0F, \xe6\xb8\x8f). Bulk replacement may inadvertently swap these, and the error is invisible in normal reading. If you suspect such corruption, use **byte-level scanning**:
    ```python
    with open(fpath, 'rb') as f:
        content = f.read()
    # Search for the wrong byte sequence
    wrong_bytes = b'\xe6\xb8\x8f'  # 渏
    if wrong_bytes in content:
        # Replace with correct bytes
        content = content.replace(wrong_bytes, b'\xe6\xb8\x8a')  # 渊
    ```
    Always re-verify with a fresh read after byte-level fixes.
- **Do** run multiple rounds — heavy-contamination chapters need 3+ passes

## Reference Mapping (Common Traditional→Simplified)
```python
# Characters that are ACTUALLY different
fanjian_map = {
    '聲音': '声音', '看著': '看着', '住著': '住着', '站著': '站着',
    '走著': '走着', '唱著': '唱着', '等著': '等着', '想著': '想着',
    '睡著': '睡着', '抱著': '抱着', '終於': '终于', '系統': '系统',
    '讓我': '让我', '讓他': '让他', '讓她': '让她', '讓我們': '让我们',
    '情況': '情况', '裝甲': '装甲', '裝備': '装备', '裝套': '装套',
    '裝飾': '装饰', '裝上': '装上', '裝下': '装下', '給予': '给予',
    '給定': '给定', '給他': '给他', '給她': '给她', '給我': '给我',
    '給你': '给你', '給錢': '给钱', '圍攻': '围攻',
    '隱隱': '隐隐', '海參': '海参', '虛弱': '虚弱', '虛偽': '虚伪',
    '虛榮': '虚荣', '虛無': '虚无', '虛幻': '虛幻', '轉身': '转身',
    '轉頭': '转头', '轉向': '转向', '轉動': '转动', '轉移': '转移',
    '轉變': '转变', '轉圈': '转圈', '轉眼': '转眼', '轉達': '转达',
    '轉化': '转化', '轉來': '转来', '轉去': '转去', '轉送': '转送',
    '轉告': '转告', '轉發': '转发', '轉唱': '转唱', '轉折': '转折',
    '轉密': '转密', '轉接': '转接', '轉載': '转载', '轉角': '转角',
    '間隙': '间隙', '間諜': '间谍', '間斷': '间断', '間距': '间距',
    '階段': '阶段', '階梯': '阶梯', '階級': '阶级',
    '對於': '对于', '對抗': '对抗', '對話': '对话', '對決': '对决',
    '對策': '对策', '對稱': '对称', '對面': '对面', '對等': '对等',
    '對立': '对立', '對岸': '对岸', '對象': '对象', '對應': '对应',
    '對比': '对比', '對接': '对接', '對錯': '对错',
    '應該': '应该', '應用': '应用', '應對': '应对',
    '警覺': '警觉', '覺得': '觉得', '覺察': '觉察', '覺醒': '觉醒',
    '打開': '打开', '關係': '关系', '關於': '关于', '關閉': '关闭',
    '議論': '议论', '認為': '认为', '認識': '认识',
    '這麼': '这么', '這樣': '这样', '那鹈': '那么', '怎鹈': '怎么',
    '什鹈': '什么', '為什鹈': '为什么', '因為': '因为', '說話': '说话',
    '問題': '问题', '時候': '时候', '開始': '开始', '開發': '开发',
    '開關': '开关', '開門': '开门', '開槍': '开枪', '開機': '开机',
    '進行': '进行', '進入': '进入', '進攻': '进攻', '進化': '进化',
    '進程': '进程', '發現': '发现', '發生': '发生', '發出': '发出',
    '發動': '发动', '發射': '发射', '發光': '发光', '發育': '发育',
    '發展': '发展', '發言': '发言', '運行': '运行', '運動': '运动',
    '過去': '过去', '過來': '过来', '過了': '过了', '過程': '过程',
    '過時': '过时', '經過': '经过', '通過': '通过', '這種': '这种',
    '那種': '那种', '一種': '一种', '這個': '这个', '那個': '那个',
    '一個': '一个', '這些': '这些', '那麼多': '那么多',
    '給錢眼': '给钱眼', '聲': '声', '著': '着', '轉': '转',
    '終': '终', '於': '于', '統': '统', '讓': '让',
    '況': '况', '裝': '装', '給': '给', '間': '间',
    '隱': '隐', '參': '参', '圍': '围', '虛': '虚',
    '階': '阶', '對': '对', '應': '应', '覺': '觉',
    '這': '这', '裡': '里', '關': '关', '進': '进',
    '發': '发', '運': '运', '過': '过', '變': '变',
    '復': '复', '顯': '显', '殺': '杀', '問': '问',
    '說': '说', '話': '话', '則': '则', '個': '个',
    '兩': '两', '點': '点', '與': '与', '沒': '没',
    '為': '为', '處': '处', '來': '来', '從': '从',
    '將': '将', '開': '开',
}
```

## Tools
- Use `search_files` for targeted grep-style checks
- Use `execute_code` with Python for bulk replacement
- Use `read_file` to spot-check key passages after replacement
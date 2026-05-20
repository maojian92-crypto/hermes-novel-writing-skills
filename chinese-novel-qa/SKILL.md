---
name: chinese-novel-qa
description: Systematic QA and editing workflow for Chinese web novels. Detects traditional characters, AI artifacts, typos, and inconsistencies in bulk markdown chapter files.
trigger: When reviewing, editing, or cleaning up Chinese novel chapters written by AI or humans. Especially useful for 100+ chapter novels in markdown format.
---

# Chinese Novel QA & Editing Skill

## Purpose
Bulk-review Chinese web novel chapters for common errors: traditional characters, AI-generated artifacts, typos, awkward phrasing, and encoding issues.

## Workflow

### Phase 1: File Inventory
```python
novel_dir = os.path.expanduser("~/writing/novels/<NOVEL_NAME>")
# 或使用 novel-config.yaml 自动查找项目路径
# project_path = find_config()  # 从 config-reader.py
# novel_dir = os.path.join(project_path, "chapters")
files = sorted([f for f in os.listdir(novel_dir) if f.endswith(".md")])
```

### Phase 2: Traditional Character Detection
1. Build a true traditional-character set that differs from simplified forms.
2. **Critical pitfall**: Do NOT include characters like `城、墨、墟、舍、壮、舌、壤、廉` — these are valid simplified Chinese characters.
3. True traditional-only characters include: `們異這團選聽氣難計頭鬆進個會幾將種發線傷動後傳備優儲靈殺滅毀與並兩單雙萬億餘長東書車門話讀寫錢買賣價貨產決沒災獲積稅稱變處類態層級員場機條組織結構標準務過經問間開關運裡裏從當無設點擊戰鬥體義現見說對來為時後幾聽風飛鳥魚龍鳳羅興謹議韓陽雲應邊廣資賢貴質賭賞賜賠賴賺賽讚贈贏離電霧靜響頂項順須頒頌預頑頓頗領頻顆題額顏願類顧顯飯飲飽餓館馬駐駕駿騎騦驅驗鬥鬰鳴鶴鷹麥麵黃黨齊齒齡龜`
4. Iterate all files and flag matches.

### Phase 3: Manual Mapping & Bulk Replace
If `opencc` is unavailable (common in restricted environments), create a `t2s_map` dict with all detected traditional characters mapped to simplified equivalents. Then:
```python
for trad, simp in t2s_map.items():
    text = text.replace(trad, simp)
```

### Phase 4: Confused Character / Typo Detection
Scan for commonly confused character pairs (同音字、形近字、误用词). **Critical**: Broad word-lists generate massive false positives — every flagged match must be manually verified in context.

High-confidence error patterns to check:

| Wrong | Correct | Context Check |
|---|---|---|
| 残炬 | 残烛 | 常见比喻错误 |
| 视察 | 窥视/洞察 | 与抽象概念搭配时不当 |
| 隶蔽 | 隐蔽 | 形近错字 |
| 翠然 | 悚然/骤然 | 语义错误，非规范用词 |
| 精神恢复剩 | 精神恢复剂 | "剩"是"剂"的形近错字 |
| 堪比不下去 | 维持不下去 | 搭配不当 |
| 大到即使是 | 即使是 | 句式冗余 |
| 做为 | 作为 | 介词用法 |
| 再这里 | 在这里 | 方位词 |
| 在来 | 再来 | 副词 |
| 以经 | 已经 | 时态词 |
| 必竟 | 毕竟 | 副词 |
| 练化 | 炼化 | 动词 |
| 震憾 | 震撼 | 形近错误 |
| 震摄 | 震慑 | 形近错误 |
| 决对 | 绝对 | 副词 |
| 振救 | 拯救 | 动词 |
| 震奋 | 振奋 | 动词 |
| 坐阵 | 坐镇 | 军事术语 |
| 坐无虚席 | 座无虚席 | 成语 |
| 走头无路 | 走投无路 | 成语 |
| 座落 | 坐落 | 动词 |

**新增：转换/识别乱码类错误**

当文本经历过繁简转换、OCR识别、或跨格式复制时，可能出现整词被替换成无关字的情况：

| 乱码形式 | 原词推测 | 判断方法 |
|---|---|---|
| 稀罕彩盘 | 破绽/细微破绽 | 结合上下文动词"看破"推断 |
| 郣一点点 | 的/地 |  Unicode异常字，直接替换 |
| 幫/點數/戰術 | 帮/点数/战术 | 繁体残留，整段批量转简体 |

判断方法：如果某个四字词在上下文中完全不通，且与相邻动词（如"看破""发现"）应有搭配关系，则极可能是转换乱码。根据语义推断原词后替换。

**False-positive examples to exclude**:
- "人才" is correct in modern Chinese (not "人材")
- "建议" in system prompts like `【建议...】` is correct
- "尝试" is correct simplified form
- "废弃" is correct
- "毁灭" is correct
- "当然" is correct
- "当时" is correct
- "即使" is correct (not "既使")

Workflow:
1. Run a Python script to scan all chapter files for each confusion pair
2. For each match, read the surrounding context (±3 lines)
3. Determine if it's a real error or correct usage
4. Fix only confirmed errors with `patch` tool
5. Re-scan after fixes to catch any missed occurrences

### Phase 4b: User Review Loop (Optional but Recommended)

For novels where the user is sensitive to textual quality (as indicated by user preference), after the automated scan:

1. Present a shortlist of **uncertain matches** — items where the context makes it ambiguous whether it's an error
2. Let the user decide: "以下这几处我不确定，你来定"
3. Only apply fixes the user explicitly approves

This is especially valuable for:
- Idiomatic expressions the user may have invented intentionally
- Character-specific speech patterns
- Genre-specific terminology

### Phase 5: AI Artifact Scanning
Scan for these known AI generation error patterns:

| Pattern | Example | Fix |
|---|---|---|
| 乱码合体字 | `混沨` | `混沌` |
| 不存在的字 | `裄缆` | `裂缝` |
| 形近错字 | `谁异` → `诡异`, `犹淬` → `幽暗` | Context-dependent |
| 语病 | `一些就不会变暗` | `一些永远不会变暗` |
| 不恰当比喻 | `松鼠跳下树枝` (in tense scene) | `野兽露出獠牙` |
| 异体字 | `消敓`(U+6553) | `消散` (U+6563) |
| 错别字 | `被吉力出来` | `被嵌进去` |
| 乱码插入 | `��` in middle of sentence | Remove/replace |

### Phase 6: Re-scan & Verify
After fixes, run the scanner again. **Common pitfall**: Some characters like `混、淬、淹` are valid simplified characters — the scanner may false-positive on them if the detection set is too broad.

### Phase 6: Content Consistency Checks
- Character name consistency (e.g., `林晨` vs `林辰`, `陈霖` vs `陈雨`)
- Rank/level system consistency
- Duplicate paragraph detection
- Chapter-to-chapter continuity at volume boundaries

**Critical: Character Name Conflict Detection**
When reviewing chapters written by subagents or multiple authors, check for accidental character name reuse. A new character might be given a name that's already used for an existing character in earlier chapters. This is especially common with:
- Common Chinese names (e.g., 玉后, 小伟)
- Descriptive names (e.g., 血爪, 铁娘)
- Names similar to existing characters (e.g., 陈霖 vs 陈雨, 叶知秋 vs 陈霖)

**Workflow for name conflict detection**:
1. When a new character appears, search the entire project for that name
2. If the name already exists in earlier chapters, verify it's the same character
3. If it's a different character with the same name, rename one of them immediately
4. Use `search_files` with the name pattern to find all occurrences

**Example fix**:
```
# Chapter 172 incorrectly reused "叶知秋" (existing character from ch162-169)
# Should have been "陈霖" (new character)
# Fix: Replace all 21 occurrences in chapter 172
search_files(pattern="叶知秋", path="{项目路径}/chapters/")
# Then use Python to rename: content.replace("叶知秋", "陈霖")
```

## Key Lessons Learned
1. **Don't over-detect**: `城、墨、淬、混、淹` are valid simplified characters.
2. **Check Unicode**: `消敓`(U+6553) vs `消散`(U+6563) are visually identical in some fonts but different codepoints.
3. **Context matters for metaphors**: A cute squirrel metaphor is fine in slice-of-life, but ruins tension in a climactic scene.
4. **Iterative scanning**: One pass is never enough. Re-scan after fixes to catch residuals and false positives.
5. **Beware broad word-list false positives**: Scanning with a large "common error" dictionary will flag thousands of correct usages (e.g., "建议" in system prompts, "尝试" as correct simplified, "废弃" as correct). Always verify context before fixing.
6. **Conversion artifacts are whole-word replacements**: Unlike single-character typos, format conversion can replace an entire word with unrelated characters (e.g., "破绽" → "稀罕彩盘"). Look for semantic disconnect as the signal.
7. **Fictional character errors have variant forms**: When a non-existent character name (e.g., "胖胖") leaks into the text, search for not just the exact name but also hybrid forms where the name is fused with descriptors (e.g., "胖胖蓝白" instead of "血管青白"). These hybrid forms often appear in physical descriptions and are easy to miss.
8. **Patch tools can introduce new typos**: When doing find-and-replace on Chinese text, the fuzzy matcher may "correct" nearby valid characters. Example: replacing "胖胖蓝白" with "青白的色泽" caused "脖颈" to become "脘颈". Always re-verify surrounding context after bulk fixes — scan ±2 lines for new anomalies.
9. **Cross-platform task sync**: If the user switches between platforms (e.g., WeCom ↔ QQ), create shared state files (`任务进度跟踪.md`, `执行日志.md`) in the project directory so progress is visible regardless of which platform they use.
10. **Unicode codepoint inspection is essential for tricky replacements**: When dealing with simplified/traditional mix-ups or visually similar characters, standard string replacement often fails because the input system auto-converts characters. Example: "喷"(U+55B7) vs "噼"(U+568E), "啮"(U+556E) vs "啪"(U+556A). The only reliable method is to use Python with explicit `chr(0xXXXX)` to build replacement strings.
    ```python
    old_str = '\u55b7\u91cc\u556e\u556e\u4f5c\u54cd'  # 喷里啮啮作响
    new_str = chr(0x5288) + '\u91cc' + chr(0x556A) + chr(0x556A) + '\u4f5c\u54cd'  # 劈里啪啦作响
    ```
    Always verify with `ord(ch)` to confirm the actual codepoints in the file before replacing.
    
11. **Byte-level replacement when patch/sed fail**: When characters look visually identical in your terminal but have different Unicode codepoints (e.g., 眩 U+7729 vs 睁 U+7741), the `patch` tool and `sed` may fail because your input system auto-corrects to the wrong character. Use Python with explicit UTF-8 byte sequences:
    ```python
    # Read file in binary mode to preserve exact bytes
    with open('file.md', 'rb') as f:
        content = f.read()
    
    # Replace using explicit byte sequences
    # 眩 (U+7729) = E7 9C A9, 睁 (U+7741) = E7 9D 81
    old_bytes = b'\xe7\x9c\xa9\xe5\xbc\x80'  # 眩开
    new_bytes = b'\xe7\x9d\x81\xe5\xbc\x80'  # 睁开
    
    if old_bytes in content:
        content = content.replace(old_bytes, new_bytes)
        with open('file.md', 'wb') as f:
            f.write(content)
    ```
    This bypasses any input method auto-correction and ensures you're replacing exactly the bytes present in the file.
11. **Filter normal repeated characters**: Chinese has many legitimate doubled-character words (缓缓, 微微, 紧紧, 慢慢, 淡淡). When scanning for repeated characters, maintain a whitelist of normal duplicates to avoid false positives. Only flag unusual repetitions like "的 的", "在 在", or "是 是" with whitespace separation.
12. **Use specific multi-character patterns, not single-character detection**: Searching for single characters like "报" or "幸" will flag thousands of correct usages (报告, 报答, 幸运, 幸好). Always check specific combinations like "报走"→"抱走", "幸一起"→"一起". This dramatically reduces false positives.
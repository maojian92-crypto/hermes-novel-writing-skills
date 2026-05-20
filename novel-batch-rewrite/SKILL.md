---
name: novel-batch-rewrite
description: >
  Batch rewrite novel chapters using parallel subagents. Handles Chinese text,
  dual workspace sync (Hermes/OpenClaw), UTF-8 encoding preservation, word count
  validation, and quality verification.
trigger:
  - "rewrite novel chapters"
  - "batch rewrite"
  - "rewrite chapters"
  - "novel rewriting"
  - "重写小说"
  - "重写章节"
  - "batch writing"
---

# 小说批量重写工作流

## 前提条件
- 项目已配置 `novel-config.yaml`
- 原始章节存在于项目目录中
- 需要创作指导文档、大纲、人物档案等参考资料
- 目标字数从 `novel-config.yaml` 的 `word_count.min` 读取（默认3000字）

## 适用场景

**场景A：重写现有章节**
- 原始章节已存在，需要扩充/改写
- 保留原有剧情框架，增加细节描写

**场景B：创作全新章节**
- 基于大纲创作之前未写过的章节
- 需要提供更详细的每章大纲和前一章结尾内容
- 子代理负担更重，建议每组3-4章（比重写的5章更少）

## 步骤1：检查工作空间和当前状态

**工作空间说明：**
- 技能通过 `novel-config.yaml` 自动识别项目路径
- 主工作区从 `workspace.primary` 读取
- 备用工作区从 `workspace.secondary` 读取（如配置了OpenClaw）

**检查流程：**
1. 读取 `novel-config.yaml` 获取项目配置
2. 检查主工作区是否已有部分完成的章节
3. 如果配置了备用工作区，检查原始文件状态
4. 确认哪个是最新版本（以字数和时间戳判断）

```bash
# 读取项目配置
# 技能会自动查找 novel-config.yaml

# 检查章节状态
ls -la {项目路径}/{chapters_dir}/第*章*.md 2>/dev/null

# 如果配置了双工作区，检查备用工作区
ls -la {备用工作区}/{chapters_dir}/第*章*.md 2>/dev/null
```

**双工作区同步（如配置了 secondary）：**
```bash
# 创建主工作空间（如果不存在）
mkdir -p {主工作区}/{chapters_dir}

# 如果备用工作区有原始文件，复制参考资料
cp {备用工作区}/00-* {主工作区}/ 2>/dev/null || true
cp {备用工作区}/01-* {主工作区}/ 2>/dev/null || true
cp {备用工作区}/synopsis.md {主工作区}/ 2>/dev/null || true
cp {备用工作区}/novel-config.yaml {主工作区}/ 2>/dev/null || true
```

## 步骤2：分组委派子代理

**建议批次大小：**
- 重写现有章节：每组5章
- 创作全新章节：每组3-4章（需要更多大纲细节，子代理负担更重）

**跨批次衔接：**
如果分多批执行，每一新批开始前：
1. 读取上一批最后一章的结尾内容（最后20-50行）
2. 将这部分内容放入子代理的 context 中，确保章节衔接自然
3. 更新角色状态（等级、技能、剧情进展）

**context 必须包含：**

对于**重写**现有章节：
1. 原始章节文件路径
2. 参考资料路径
3. 写作规范和体验要求
4. 输出路径（Hermes工作区）

对于**创作**全新章节（无原文可参考）：
1. 详细的每章大纲（每章的剧情节点、关键事件、角色发展）
2. 上一组章节的结尾内容（确保衔接）
3. 角色当前状态（等级、技能、装备、关系）
4. 参考资料路径
5. 输出路径

**示例子代理配置：**
```
goal: 重写小说第18-22章，每章不低于{word_count.min}字
context: |
  作品名：{project.name}
  原始章节路径：{项目路径}/{chapters_dir}/
  参考资料：{项目路径}/{outline}, {项目路径}/{truth_files.core}, synopsis.md
  输出路径：{项目路径}/{chapters_dir}/
  
  重写规范：
  1. 保持原有剧情框架和人设
  2. 增加细节描写，丰富人物内心戏
  3. 保持作品特色（参考 synopsis.md）
  4. 每章不低于{word_count.min}字
  5. 使用write_file工具写入，确保UTF-8编码
```

**关键配置：**
- `toolsets: ["file"]` — 子代理需要读写文件
- `max_iterations: 50` — 充足的轮次

## 步骤3：字数验证

子代理完成后，用Python脚本验证字数：

```python
import os, re, sys
from pathlib import Path

# 自动查找 novel-config.yaml
def find_config(start_path="."):
    current = Path(start_path).resolve()
    while current != current.parent:
        if (current / "novel-config.yaml").exists():
            return str(current)
        current = current.parent
    return None

# 读取配置
try:
    import yaml
    project_path = find_config()
    with open(os.path.join(project_path, "novel-config.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    word_count_min = config.get('word_count', {}).get('min', 3000)
except:
    word_count_min = 3000

def count_words(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    chinese = len(re.findall(r'[\u4e00-\u9fff]', content))
    eng = len(re.findall(r'[a-zA-Z]+', content))
    num = len(re.findall(r'\d+', content))
    return chinese + eng + num

# 验证时与配置的字数标准对比
# 标准：每章 >= word_count_min
```

**计数规则：**
- 中文字符数 + 英文单词数 + 数字串数 = 总估算字数
- 标准：每章 >= config.word_count.min（默认3000）
- **建议子代理目标 >= config.word_count.target_min（默认3500）** — 留出缓冲，避免刚刚过线的章节在验证时因统计差异而不达标

## 步骤4：修复未达标章节

如果有章节未达标：
1. 读取现有内容
2. 判断是扩充描写还是重新写
3. 使用write_file覆盖写入（确保UTF-8）
4. 重新验证

## 步骤5：同步回用户工作区

如果配置了双工作区（`workspace.secondary`），所有章节验证通过后，复制回备用工作区：

```bash
# 从主工作区同步到备用工作区
cp {主工作区}/{chapters_dir}/第{XXX..YYY}章*.md {备用工作区}/{chapters_dir}/
```

如果只有一个工作区，跳过此步骤。

## 步骤6：最终验证

在目标工作空间重新跑一遍字数检查，确认所有文件正确写入。

## 常见问题与解决

| 问题 | 原因 | 解决 |
|------|------|------|
| 字数不达标 | 子代理输出不足 | 扩充描写，增加场景、对话、心理描写 |
| 编码乱码 | 写入时未指定UTF-8 | 确保write_file使用UTF-8编码，读取时也用UTF-8 |
| 找不到 novel-config.yaml | 项目未初始化配置 | 按 novel-startup-template 创建配置文件 |
| 验证时发现两个工作空间同名文件字数不同 | 子代理写入后可能被覆盖或写到了不同位置 | 以主工作区为准，确认是最新版后再同步 |
| 章节风格不统一 | 子代理理解不一致 | 在context中提供详细的体验要求和示例文本 |
| 上下文压缩导致任务中断 | 长会话触发压缩 | 使用todo保持任务状态，在compact后检查并恢复 |
| 任务范围扩展 | 用户要求增加更多章节 | 保持已完成章节不变，用同样流程继续创作新批次 |

## 经验法则

1. **总是先检查 novel-config.yaml** — 确认项目配置正确
2. **总是在子代理context中明确输出路径** — 避免写到错误位置
3. **总是验证后再同步** — 避免将未达标的章节覆盖用户文件
4. **中文文本字数计算** — 用中文字符+英文单词+数字，而不是简单的字节数
5. **分多批时注意章节衔接** — 每新批开始前读取上一批最后章节的结尾
6. **保持任务状态可恢复** — 使用todo管理批次，避免上下文丢失后清单消失

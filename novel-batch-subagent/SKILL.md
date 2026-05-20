---
name: novel-batch-subagent
description: |
  长篇小说批量创作工作流——通过 spawn 子代理（delegate_task）并行创作多批章节，适合20+章以上的长篇小说。核心优势是在保持剧情连贯性的同时大幅提升创作效率。
  当用户要求创作大量章节（如"写到第80章"、"继续创作20章"等）时使用。
metadata:
  trigger: 批量创作小说章节、长篇小说批量生成、通过子代理创作小说
  source: 基于实战经验总结
---

# 长篇小说子代理批量创作流

## 适用场景

- 用户要求一次性创作 10+ 章内容
- 已有现有小说底座，需要"继续"创作后续章节
- 每章要求 3000-6000 字，总量超过 5 万字

## 核心原则

**4-5 章一批次**：每个子代理负责 4-5 章，过多会导致上下文过载，过少则效率低下。

**先读结尾，再做规划**：每批开始前必须读取上一批最后一章的结尾，确保剧情严丝合缝。

**上下文要"自包含"**：子代理是独立会话，无法访问主会话的历史记录。必须在 prompt 中提供足够的背景信息。

## 工作流程

### 第一步：建立跟踪

使用 `todo` 工具创建跟踪列表，每批一个项目：

```
- [第一批] 第061-065章（XX剧情线）
- [第二批] 第066-070章（XX剧情线）
- [第三批] 第071-075章（XX剧情线）
- [第四批] 第076-080章（XX剧情线）
- [字数检查]
```

### 第二步：准备上下文模板

对每个子代理，在 `context` 字段中提供以下必备信息：

#### 1. 小说基本信息
- 小说名称、当前卷/章节进度
- 世界观设定（简洁版，100-200字）

#### 2. 角色状态快照
清单式列出主要角色的当前状态：
```
- 主角XXX：等级、技能、关键道具、当前目标
- 队友A：等级、状态、关键信息
- 队友B：...
- 反派XXX：等级、势力、与主角的关系
```

**必须同时列出"不在场的角色"**：子代理在孤立会话中无法判断哪些角色最近没出场，容易错误地重新引入（如很久没出现的盟友或已被排斥的反派）。明确写清楚：
```
**不在场的角色**：
- 墨子：留在观测站，不在团队
- 何为：第110章被排斥后离开，不应出现
- 韩天霸：已死亡
```

#### 3. 上一批最后一章的精确结尾
复制粘贴最后一章的结尾 300-500 字，确保子代理知道当前剧情状态。

#### 4. 每章详细大纲
为每一章写一个简短大纲（5-10点），包括：
- 本章核心事件
- 关键场景
- 角色互动
- 章末钩子

#### 5. 写作要求
- 字数范围（3000-6000）
- 视角（第一/第三人称）
- 风格特点
- 系统流/元素使用规范

#### 6. 文件输出路径
明确每章的写入路径，如：
```
{项目路径}/{chapters_dir}/第XXX章-标题.md
```

**路径从 novel-config.yaml 自动读取**：
- 技能会自动查找当前目录的 `novel-config.yaml`
- `chapters_dir` 从配置读取
- 不再硬编码 `~/.hermes/workspace/novels/万界求生/`

**多项目示例**：
```bash
# 万界求生项目路径：~/.hermes/workspace/novels/万界求生/
# 章节路径：~/.hermes/workspace/novels/万界求生/第XXX章-标题.md
# （chapters_dir 配置为 "."，章节在根目录）

# 无尽进化项目路径：~/writing/novels/endless-evolution/
# 章节路径：~/writing/novels/endless-evolution/Chapters/第XXX章-标题.md
# （chapters_dir 配置为 "Chapters"）
```

### 第三步：启动子代理

使用 `delegate_task` 启动子代理，建议配置：
- `toolsets`: `["terminal", "file"]` — 子代理需要写文件
- `goal`: 简洁明确
- `context`: 上述全部信息

**重要**：每次可启动 **1-3 个** 子代理并行（一批 4-5 章/代理）。系统上限为 3 个并发子代理，超过会报错。建议：
- 普通批次：启动 3 个并行，大幅提升效率
- 关键批次（剧情高潮、角色死亡等）：启动 1 个，便于精细控制

如果超出并发限制报错：`Too many tasks: X provided, but max_concurrent_children is 3`，将任务拆分为多次 `delegate_task` 调用。

### 上下文最佳实践（来自实战验证）

**先写大纲，再存盘**：在启动子代理之前，将完整的大纲写入一个持久文件（如 `00-第X卷大纲.md`）。子代理是孤立会话，主会话的内存不会保留到下一批。持久文件可以让你在下一批启动前快速回顾上一批的规划，也方便在子代理失败时重新委托。

**每章大纲要具体**：不要只写"本章主角遇到敌人"，而要列出 5-8 个具体情节点，例如：
```
- 主角用【规则触碰】改写局部规则创造安全区，消耗极大
- 发现刻有"XXX——第七锚点"的石碑
- 石碑周围有前人遗骸和壁画，描绘编织者收割灵魂
- 结尾钩子：荒漠中心传来心跳般的震动
```

**角色状态要"增量更新"**：每批开始时，必须基于上一批的结局更新角色状态。例如：
```
- 铁娘：黄银3星→燃烧全部生命力濒死，苏小小勉强维持生命
- 老刀：机械义肢彻底报废
- 冷箭：弹药耗尽
```

**关键高潮章节标注字数**：如果某章是情感高潮或战斗高潮（如队友牺牲、Boss战），在大纲中额外标注"本章要求接近6000字上限"，避免高潮章节篇幅不足。

### 第四步：验证与衔接

子代理完成后：

1. **用脚本验证字数**：必须在主会话中用正则匹配 `[\u4e00-\u9fff]` 重新统计中文字符数，不要仅凭子代理报告判断是否达标
2. **修复字数不足的章节**：如果存在字数略缺章节，读取该章找到适合扩充的位置（环境描写、内心独白、战斗细节等），用`patch`工具局部补充
3. **准备下一批上下文**：读取本批最后一章的实际内容（至少300-500字），而不是大纲，确保下一批子代理有精确的衔接点
4. **更新 `todo` 状态**＜/当前批次状态

**两批衔接最佳实践**：
当分两批创作（如10章=5+5）时，第二批的上下文必须包含第一批最后一章的**实际精确结尾**（不是大纲）。实战中，第一批用了50次tool call（达上限），第二批仅用17次就完成，差距在于第二批有了第一批最后一章的实际内容作为衔接点，而不是大纲描述。

### 第五步：循环直至完成

重复步骤 2-4，直到所有批次完成。

### 第六步：全局检查

所有批次完成后：

1. 用脚本统计所有章节的中文字符数，确认每章均在3000-6000字范围内
2. 对关键角色进行一致性抽查（如失明、断肢、离开等）
3. 向用户汇报总字数和各章分布

**中文字符数统计脚本**（动态读取项目配置）：

```python
import os, re, sys

# 自动查找 novel-config.yaml
from pathlib import Path

def find_config(start_path="."):
    current = Path(start_path).resolve()
    while current != current.parent:
        if (current / "novel-config.yaml").exists():
            return str(current)
        current = current.parent
    return None

# 查找配置
project_path = find_config()
if not project_path:
    print("错误：未找到 novel-config.yaml，请在项目目录内运行")
    sys.exit(1)

# 读取配置（需要 PyYAML）
try:
    import yaml
    with open(os.path.join(project_path, "novel-config.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    chapters_dir = config.get('files', {}).get('chapters_dir', 'chapters')
    word_count_min = config.get('word_count', {}).get('min', 3000)
except:
    # 回退到默认
    chapters_dir = 'chapters'
    word_count_min = 3000

# 构建完整路径
novel_dir = os.path.join(project_path, chapters_dir)
if not os.path.exists(novel_dir):
    novel_dir = project_path  # 章节可能在根目录

chapters = sorted([f for f in os.listdir(novel_dir) if f.startswith('第') and f.endswith('.md')])

total = 0
for ch in chapters:
    fpath = os.path.join(novel_dir, ch)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
    total += cn_chars
    status = "✅" if cn_chars >= word_count_min else "❌"
    print(f"{ch} | {cn_chars:>5} 字 | {status}")

print(f"\n合计: {total} 字 | 均每章: {total//len(chapters)} 字 | 标准: ≥{word_count_min}字")
```

## 实战陷阱

### OCR 冷门字符：深渏者 vs 深渏者

在简繁体替换过程中，可能产生冷门的形近字错误：
- `渏` (\xe6\xb8\x8f) —— 错误，应为 `渏` (\xe6\xb8\x8a)
- `渏` 和 `渏` 看似相同，实则不同，普通字符替换无效
- 必须使用 **字节级替换**：

```python
with open(fpath, 'rb') as f:
    content = f.read()
content = content.replace(b'\xe6\xb8\x8f', b'\xe6\xb8\x8a')  # 渏→渏
with open(fpath, 'wb') as f:
    f.write(content)
```

建议在每批创作完成后，对整体用 `rg '渏'` 或 `rg '渏'` 扫描一次，确保无残留。

### 角色状态一致性检查（动态配置版）

创作完成后，必须运行一致性检查脚本，避免子代理在孤立会话中遗忘角色状态。

**脚本现在从 `novel-config.yaml` 动态读取角色和检查规则**：

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
    if not project_path:
        print("错误：未找到 novel-config.yaml")
        sys.exit(1)
    
    with open(os.path.join(project_path, "novel-config.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    
    # 从配置读取项目信息
    chapters_dir = config.get('files', {}).get('chapters_dir', '')
    novel_dir = os.path.join(project_path, chapters_dir) if chapters_dir else project_path
    
    # 从配置读取角色检查规则
    characters = config.get('characters', {})
    protagonist = characters.get('protagonist', {})
    team = characters.get('team', [])
    absent_chars = characters.get('absent', [])
    allowed_english = config.get('terminology', {}).get('allowed_english', [])
    
except Exception as e:
    print(f"读取配置失败: {e}")
    sys.exit(1)

# 构建角色检查规则
checks = []

# 1. 已死亡/离开角色检查
absent_names = [a['name'] for a in absent_chars if 'name' in a]
for name in absent_names:
    checks.append({
        'type': 'absent',
        'name': name,
        'description': f'已死亡/离开角色不应出现'
    })

# 2. 角色特殊状态检查（失明、断肢等）
for member in team:
    name = member.get('name', '')
    for check in member.get('checks', []):
        checks.append({
            'type': check.get('type', 'unknown'),
            'name': name,
            'description': check.get('description', ''),
            'forbidden_verbs': check.get('forbidden_verbs', []),
            'forbidden_actions': check.get('forbidden_actions', []),
            'limb': check.get('limb', ''),
            'exclude_patterns': check.get('exclude_patterns', [])
        })

# 3. 主角检查
if protagonist:
    name = protagonist.get('name', '')
    for check in protagonist.get('checks', []):
        checks.append({
            'type': check.get('type', 'unknown'),
            'name': name,
            'description': check.get('description', ''),
            'forbidden_verbs': check.get('forbidden_verbs', []),
            'forbidden_actions': check.get('forbidden_actions', []),
            'limb': check.get('limb', ''),
            'exclude_patterns': check.get('exclude_patterns', [])
        })

# 运行检查
chapters = [f for f in os.listdir(novel_dir) if f.startswith('第') and f.endswith('.md')]

for ch in sorted(chapters):
    fpath = os.path.join(novel_dir, ch)
    with open(fpath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        # 检查已死亡/离开角色
        for check in checks:
            if check['type'] == 'absent':
                if check['name'] in line:
                    print(f"❌ {ch} 第{i+1}行: 发现不应出现的角色'{check['name']}' -> {line.strip()}")
            
            elif check['type'] == 'vision':
                # 失明角色视觉检查
                if check['name'] in line:
                    for verb in check.get('forbidden_verbs', []):
                        if verb in line:
                            # 检查排除模式
                            excluded = False
                            for pattern in check.get('exclude_patterns', []):
                                if re.search(pattern, line):
                                    excluded = True
                                    break
                            if not excluded:
                                print(f"⚠️ {ch} 第{i+1}行: {check['name']}相关视觉词'{verb}' -> {line.strip()}")
            
            elif check['type'] == 'limb':
                # 肢体报废检查
                if check['name'] in line and check.get('limb', '') in line:
                    has_action = any(a in line for a in check.get('forbidden_actions', []))
                    if has_action:
                        # 检查排除模式
                        excluded = False
                        for pattern in check.get('exclude_patterns', []):
                            if re.search(pattern, line):
                                excluded = True
                                break
                        if not excluded:
                            print(f"⚠️ {ch} 第{i+1}行: {check['name']}{check.get('limb', '')}动作 -> {line.strip()}")
        
        # 英文单词混入检查
        english_words = re.findall(r'[a-zA-Z]{3,}', line)
        for word in english_words:
            if word not in allowed_english:
                print(f"⚠️ {ch} 第{i+1}行: 发现英文单词'{word}' -> {line.strip()}")
        
        # 繁体字检查
        fanjian_map = {'聲': '声', '著': '着', '轉': '转', '終': '终', '於': '于', '統': '统'}
        for trad, simp in fanjian_map.items():
            if trad in line:
                print(f"⚠️ {ch} 第{i+1}行: 发现繁体字'{trad}' -> {line.strip()}")

print(f"\n检查完成，共检查 {len(chapters)} 章")
```

**配置驱动说明**：
- 角色检查规则完全从 `novel-config.yaml` 的 `characters` 段读取
- 每个角色可以有多个 `checks`，类型包括 `vision`（失明）、`limb`（肢体报废）等
- `forbidden_verbs`/`forbidden_actions` 定义禁止的动作词
- `exclude_patterns` 定义排除模式（如他人视角、姿态描写），支持正则
- `allowed_english` 从 `terminology` 段读取，定义合法英文专有名词
- 新增角色或状态变更时，只需修改 `novel-config.yaml`，无需修改脚本

**旧版硬编码脚本已废弃**，请使用此动态配置版本。

### 角色名混淆陷阱（高优先级）

子代理在孤立会话中**极易混淆已有角色和新角色名**，这是一个非常常见且影响严重的错误。

**典型场景**：
- 已有角色"叶知秋"（第162-169章出现，十七岁女孩，来自另一世界）
- 新角色需要是新世界的异化觉醒者（男性）
- 子代理在无明确约束时，可能将新角色也命名为"叶知秋"，造成角色身份冲突

**预防措施**：
1. **明确禁用已有角色名**：在任务指令中用加粗或引号强调——`角色名必须用"陈霖"和"陈雨"，绝不能用"叶知秋"`
2. **提供完整角色清单**：列出所有已有角色名（特别是近期出场过的），并标注`禁止使用`
3. **命名时提供首字母提示**：如果新角色名尚未确定，在上下文中给出首字母或命名方向，避免子代理随意选择

**修复方法**：
如果发现角色名混淆（如已有角色名被错误用于新角色），使用脚本全局替换：

```python
with open(fpath, 'r', encoding='utf-8') as f:
    content = f.read()

# 将误用的已有角色名替换为正确的新角色名
content = content.replace('错误名', '正确名')

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)
```

**修复后必须验证**：搜索原文确认替换彻底，且没有破坏其他语境（如对话中提到"叶知秋"是合法引用）。

### 子代理命中 max_iterations 的信号

如果子代理命中了 `max_iterations` 上限（50 次 tool call），通常不是因为子代理"太慢"，而是因为**上下文不足**导致它反复修改。最常见的原因：

1. **上一章结尾不够精确**：没有提供足够长的原文引用（300-500 字），子代理对当前情节状态判断不准，写偏后又要重写。
2. **角色状态模糊**：缺少关键约束（如失明、断肢、已离开的角色），导致子代理写出矛盾后反复 patch。
3. **大纲缺少关键情节点**：子代理在缺乏具体指引时自由发挥，写完后发现与预期不符。

**对策**：如果批次 A 命中了上限而批次 B 正常完成，对比两者的上下文，找出差异点并下一批修复。实战中，提供精确的上一章结尾原文（300-500 字）是降低工具调用次数的最有效手段。

### 字数偏少问题

子代理创作时，有时会出现章节字数低于要求的情况（如 2500-2900 字，要求 3000+）。这通常发生在以下情况：
- 子代理为了节省上下文，在情节完整的情况下提前结束
- 章节以"动作流"为主，缺少情感、氛围、角色心理描写
- 对话过于简略，缺少细节展示
- **子代理计数方式与主会话不同**：子代理可能使用含标点的字符数或混合计数，导致其报告"达标"但实际中文字符数不足

**解决方法**：
1. **大纲中明确标注字数**：在章节大纲中明确写"本章要求 XXXX 字"、"本章为情感高潮，需要详细描写氛围"等提示
2. **主会话独立验证**：子代理完成后，务必在主会话中用脚本重新统计中文字符数（`[\u4e00-\u9fff]`），不要仅凭子代理报告判断。第一批5章中曾出现子代理报告全部达标、但实际第152章仅3001字的情况。
3. **用patch工具局部扩充**：对于字数略缺的章节（差300-800字），在主会话中读取文件，找到合适的插入点（如环境描写、心理活动、对话扩展），用`patch`工具直接扩充，比重写整章更高效
4. **重新委托**：如果内容也不完整，给子代理发送更详细的补充大纲，要求扩充具体场景或对话
5. **接受微少偏差**：如果内容质量高、情节紧凑，2600-2900 字也可以接受（特别是对于"过渡章"或"休整章"）

每批完成后必须验证每章字数（动态读取配置）：

```python
import os, sys
from pathlib import Path

# 自动查找 novel-config.yaml
def find_config(start_path="."):
    current = Path(start_path).resolve()
    while current != current.parent:
        if (current / "novel-config.yaml").exists():
            return str(current)
        current = current.parent
    return None

project_path = find_config()
if not project_path:
    print("错误：未找到 novel-config.yaml")
    sys.exit(1)

try:
    import yaml
    with open(os.path.join(project_path, "novel-config.yaml"), 'r') as f:
        config = yaml.safe_load(f)
    chapters_dir = config.get('files', {}).get('chapters_dir', '')
    word_count_min = config.get('word_count', {}).get('min', 3000)
except:
    chapters_dir = ''
    word_count_min = 3000

novel_dir = os.path.join(project_path, chapters_dir) if chapters_dir else project_path

for prefix in ['第106', '第107', ...]:  # 替换为实际章节前缀
    fpath = os.path.join(novel_dir, f"{prefix}...")
    with open(fpath, 'r') as f:
        content = f.read()
    cn_chars = sum(1 for c in content if '\u4e00' <= c <= '\u9fff')
    assert cn_chars >= word_count_min, f"{prefix} 仅 {cn_chars} 字，不达标（标准：≥{word_count_min}）"
```

### 检查脚本的误报处理

自动检查脚本往往会误报以下情况，需要人工复核：
- **回忆性描述**：角色回忆过去的能力或状态，与当前状态无关
- **本质解析**：作者解释某能力的本质（如"狂化是消灭其他可能性"），不是角色正在使用该能力
- **第三视角**：角色A描述角色B的状态，比如"{角色A}看到{角色B}的命运丝线在闪烁"——这是{角色A}的视角，不是{角色B}自己看到
- **对话中的提及**：角色在对话中提及某人的能力，不等于该能力正在发动

检查时先看行号和上下文，判断是否真的存在矛盾，避免无意义修改。

### 剧情偏离处理

如果子代理创作的内容与预期有偏离（如多了新角色、改变了设定），在下一批的上下文中明确纠正，确保一致性。

### 效率优化

- 如果某批子代理失败或返回结果不满意，可以重新调整大纲后再次委托
- 对于重要的战斗/高潮场景，可以在大纲中特别标注，让子代理重点着墨

## 与其他技能的关系

- 本技能专注于"批量生产流程"，不替代 `chinese-novelist` 的创作质量控制流程
- 建议与 `chinese-novelist` 结合使用：用 `chinese-novelist` 确定风格、人物、大纲，用本技能实际批量生成
- 也可与 `novel-architect` 结合使用，先用架构师做章节架构，再用本技能批量生成

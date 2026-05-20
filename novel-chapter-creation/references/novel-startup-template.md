---
name: novel-startup-template
purpose: 新书启动脚手架 — 快速初始化小说项目结构
---

# 新书启动脚手架

> 主服务: 快速初始化小说项目
> 内容层级: 项目基础设施

---

## 适用场景

- 启动全新小说项目
- 为现有小说补充缺失的基础设施（novel-config.yaml）
- 规范化已有项目的文件结构

---

## 目录结构模板

```
{项目根目录}/
├── novel-config.yaml              # 项目配置文件（核心！所有技能读取此文件）
├── 00-大纲.md                     # 卷/章大纲
├── 01-核心设定与角色.md            # 核心设定
├── 02-团队成员状态跟踪.md           # 角色状态
├── 03-任务进度跟踪.md              # 任务进度
├── 04-已揭示谜团与伏笔.md           # 谜团与伏笔
├── 05-世界观与规则文档.md           # 世界观
├── references/                    # 参考文档
│   ├── anti-ai-patterns.md       # AI味检测
│   ├── cool-points-guide.md      # 爽点设计
│   ├── core-constraints.md       # 核心约束
│   ├── strand-weave.md           # 三线节奏
│   ├── review-checklist.md       # 审查清单
│   ├── truth-files-guide.md      # 一致性管理
│   ├── 33-dimension-audit.md     # 质量审计
│   └── config-reader.py          # 配置读取工具
├── chapters/                      # 章节正文
│   ├── 第001章-标题.md
│   └── ...
└── archive/                       # 归档
    └── old-drafts/
```

---

## 初始化命令

```bash
# 1. 创建目录结构
mkdir -p {项目路径}/{references,chapters,archive}

# 2. 创建 Truth Files 模板
touch {项目路径}/01-核心设定与角色.md
touch {项目路径}/02-团队成员状态跟踪.md
touch {项目路径}/03-任务进度跟踪.md
touch {项目路径}/04-已揭示谜团与伏笔.md
touch {项目路径}/05-世界观与规则文档.md

# 3. 复制配置读取工具
cp ~/.hermes/skills/creative/novel-chapter-creation/references/config-reader.py \
   {项目路径}/references/

# 4. 创建 novel-config.yaml（使用模板，见下方）
# 5. 复制参考文档（可选）
cp ~/.hermes/skills/creative/novel-chapter-creation/references/*.md \
   {项目路径}/references/ 2>/dev/null || true
```

---

## novel-config.yaml 模板

每个项目必须有一个 `novel-config.yaml`，位于项目根目录。所有写作技能都通过此文件获取项目特定的配置。

**创建方式**：复制标准模板后，根据项目实际情况填写。

标准模板位置：
`~/.hermes/skills/creative/novel-chapter-creation/references/novel-config.yaml`

**关键字段说明**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `project.name` | 是 | 项目中文名 |
| `project.id` | 是 | 项目英文ID，用于目录名 |
| `files.outlines` | 是 | 大纲文件列表 |
| `files.truth_files` | 是 | 5个Truth Files的文件名 |
| `files.chapters_dir` | 是 | 章节存放目录 |
| `characters.protagonist` | 是 | 主角信息 |
| `characters.team` | 是 | 团队成员列表 |
| `characters.absent` | 否 | 已死亡/离开的角色 |
| `narrative.pov` | 是 | 叙述人称 |
| `word_count.min` | 是 | 最低字数要求 |

---

## Truth Files 初始模板

### 01-核心设定与角色.md
```markdown
# 核心设定与角色

## 世界观核心
- [核心规则1]
- [核心规则2]

## 主要角色

### [角色名]
- **身份**: [身份]
- **能力**: [能力列表]
- **目标**: [目标]
- **关系**: [与其他角色关系]

## 关键物品
- [物品名]: [描述]

## 重要地点
- [地点名]: [描述]
```

### 02-团队成员状态跟踪.md
```markdown
# 团队成员状态跟踪

## [角色名]
- **当前状态**: [状态]
- **持有物品**: [物品列表]
- **能力等级**: [等级]
- **情感状态**: [情感]
- **最后更新**: 第XXX章
```

### 03-任务进度跟踪.md
```markdown
# 任务进度跟踪

## 当前任务
- [ ] [任务名]: [描述] (第XXX章开始)

## 已完成任务
- [x] [任务名]: [描述] (第XXX章完成)

## 待触发任务
- [ ] [任务名]: [触发条件]
```

### 04-已揭示谜团与伏笔.md
```markdown
# 已揭示谜团与伏笔

## 已揭示信息
- [信息内容] (第XXX章揭示)

## 未解谜团
- [谜团]: [当前线索]

## 已埋伏笔
- [伏笔内容] → 预计回收: [卷/章]
```

### 05-世界观与规则文档.md
```markdown
# 世界观与规则文档

## 世界规则
- [规则1]: [详细描述]

## 地点描述
### [地点名]
- [描述]

## 势力分布
- [势力名]: [描述]
```

---

## 启动检查清单

- [ ] 目录结构创建完成
- [ ] novel-config.yaml 创建并填写完成
- [ ] Truth Files 模板创建完成
- [ ] 大纲文件创建完成
- [ ] 参考文档复制完成（config-reader.py 必须复制）
- [ ] 首章文件创建完成
- [ ] 项目路径记录到记忆

---

## 已有项目补全流程

若项目已存在但缺少基础设施：

1. **检查缺失文件**：对比上述清单
2. **创建 novel-config.yaml**：最重要！没有此文件，技能无法识别项目
3. **创建缺失文件**：使用模板
4. **反向填充**：从已有章节提取信息填充Truth Files
5. **验证一致性**：确保提取信息无矛盾

### 已有项目快速补全 novel-config.yaml

对于已有项目（如《万界求生》），按以下步骤补全：

```bash
# 1. 进入项目目录
cd {项目路径}

# 2. 复制配置模板
cp ~/.hermes/skills/creative/novel-chapter-creation/references/novel-config.yaml .

# 3. 根据实际情况编辑：
#    - project.name / project.id
#    - files.outlines（实际大纲文件名）
#    - files.truth_files（实际Truth Files文件名）
#    - files.chapters_dir（章节实际存放位置）
#    - characters（所有角色信息）
#    - narrative.pov（叙述人称）
#    - word_count（字数标准）

# 4. 复制 config-reader.py
mkdir -p references
cp ~/.hermes/skills/creative/novel-chapter-creation/references/config-reader.py references/
```

---

## 多项目共存说明

所有写作技能现在都通过 `novel-config.yaml` 自动识别项目：

- 技能会在当前目录及上级目录查找 `novel-config.yaml`
- 找到后自动读取项目配置，不再依赖硬编码路径
- 你可以在任意项目目录下运行技能，技能会自动适配当前项目

**示例**：
```bash
# 在万界求生目录下
cd ~/.hermes/workspace/novels/万界求生
# 运行技能 → 自动读取万界求生的配置

# 在无尽进化目录下
cd ~/writing/novels/endless-evolution
# 运行技能 → 自动读取无尽进化的配置
```
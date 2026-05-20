# Hermes 小说写作技能集

通用小说写作技能，支持多项目配置，通过 `novel-config.yaml` 自动适配任意小说项目。

## 仓库地址

https://github.com/maojian92-crypto/hermes-novel-writing-skills

## 包含技能

### 核心创作技能

| 技能 | 说明 |
|------|------|
| **novel-chapter-creation** | 单章创作流程，整合防幻觉体系与 Anti-AI 工程 |
| **novel-batch-subagent** | 批量章节创作（20+章），子代理并行 |
| **novel-batch-rewrite** | 批量重写/改写现有章节 |
| **novel-pov-conversion** | 人称视角转换（第一人称 ↔ 第三人称） |
| **novel-character-consistency-check** | 角色一致性检查 |
| **novel-traditional-char-cleanup** | 繁体字清理 |
| **chinese-novel-qa** | 质量审计与错误检测 |

### 参考文档（novel-chapter-creation/references/）

| 文件 | 说明 |
|------|------|
| **novel-config.yaml** | 项目配置文件标准模板 |
| **config-reader.py** | 配置读取工具 |
| **core-constraints.md** | 核心约束（三大定律） |
| **truth-files-guide.md** | Truth Files 管理指南 |
| **strand-weave.md** | 三线节奏控制 |
| **cool-points-guide.md** | 爽点设计参考 |
| **anti-ai-patterns.md** | AI味检测清单 |
| **review-checklist.md** | 六维审查清单 |
| **33-dimension-audit.md** | 33维质量审计 |
| **novel-startup-template.md** | 项目脚手架 |

## 核心特性

- **多项目支持**：通过 `novel-config.yaml` 自动适配任意小说项目
- **动态配置**：角色、路径、字数标准、叙述人称均从配置读取
- **防幻觉体系**：Truth Files + 三大定律 + 自动检查脚本
- **Anti-AI 工程**：33维质量审计 + 句式模板检测
- **批量创作**：子代理并行，支持 20+ 章批量生成

## 快速开始

1. 复制 `novel-config.yaml` 模板到项目根目录
2. 填写项目信息（名称、角色、路径等）
3. 在项目目录下运行技能，自动读取配置

## 配置示例

```yaml
project:
  name: "无尽进化"
  id: "endless-evolution"

files:
  outlines: ["00-大纲.md"]
  chapters_dir: "chapters"

characters:
  protagonist:
    name: "林夜"
  team:
    - name: "苏雨晴"
    - name: "陈锋"

narrative:
  pov: "third_person"
```

## 使用方式

```bash
# 进入项目目录
cd ~/writing/novels/endless-evolution

# 运行技能（自动读取 novel-config.yaml）
# 技能会自动识别当前项目配置
```

## 更新日志

### v3.0 (2026-05-20)
- 新增 novel-config.yaml 配置体系
- 所有技能改为项目无关，支持多项目
- 新增 config-reader.py 配置读取工具
- 角色检查脚本动态化
- 移除所有硬编码路径和角色名

## License

MIT

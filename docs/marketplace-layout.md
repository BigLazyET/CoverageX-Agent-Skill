# Marketplace 与插件目录说明

本仓库同时支持 Codex 和 Cursor。两个平台使用不同的 Marketplace 与插件清单，但最终都加载同一个插件目录和同一份 canonical Agent Skill。

## 两层结构

配置分为两个层级：

1. **Marketplace 清单**描述仓库中有哪些可安装插件，以及每个插件位于哪里。
2. **Plugin 清单**描述某个插件的名称、版本、作者、展示信息和可发现组件。

整体关系如下：

```text
CoverageX-Agent-Skill/
├── .agents/plugins/marketplace.json
├── .cursor-plugin/marketplace.json
└── plugins/
    └── coveragex-agent-skill/
        ├── .codex-plugin/plugin.json
        ├── .cursor-plugin/plugin.json
        └── skills/
            └── coveragex-incremental-report/
                ├── SKILL.md
                ├── references/
                └── scripts/
```

## Codex 配置

### `.agents/plugins/marketplace.json`

这是 Codex 的仓库级 Marketplace 清单。它声明 Marketplace 名称、可安装插件、安装策略和插件相对路径：

```text
./plugins/coveragex-agent-skill
```

Codex 先读取该清单找到插件，再进入插件目录读取具体插件清单。

### `plugins/coveragex-agent-skill/.codex-plugin/plugin.json`

这是 Codex 的插件级清单。它保存插件名称、版本、作者、许可证、界面信息和默认提示，并通过：

```json
"skills": "./skills/"
```

让 Codex 发现插件目录中的 Agent Skill。

因此 Codex 同样具有 Marketplace 清单和 Plugin 清单，只是两者使用不同的目录命名：

```text
仓库级：.agents/plugins/marketplace.json
插件级：plugins/coveragex-agent-skill/.codex-plugin/plugin.json
```

## Cursor 配置

### `.cursor-plugin/marketplace.json`

这是 Cursor 的仓库级 Marketplace 清单，也是 **Add Marketplace from GitHub Repository** 首先使用的入口。它声明 Marketplace 元数据，并将 `coveragex-agent-skill` 指向：

```text
plugins/coveragex-agent-skill
```

### `plugins/coveragex-agent-skill/.cursor-plugin/plugin.json`

这是 Cursor 的插件级清单。它描述具体插件的名称、版本、作者、许可证和仓库地址。Cursor 随后在该插件目录内按约定发现 `skills/`。

## 为什么 Cursor 有两个 `.cursor-plugin`

它们并不重复，而是位于不同层级：

```text
.cursor-plugin/marketplace.json
└── 描述整个仓库中的插件目录

plugins/coveragex-agent-skill/.cursor-plugin/plugin.json
└── 描述 coveragex-agent-skill 这个具体插件
```

可以把它们理解为：

```text
Marketplace 清单 = 应用商店目录
Plugin 清单      = 某个应用的详情和加载配置
```

## 单一 Skill 来源

Codex 和 Cursor 的清单最终都指向：

```text
plugins/coveragex-agent-skill/
```

该目录只包含一份 canonical Skill：

```text
plugins/coveragex-agent-skill/skills/coveragex-incremental-report/
```

平台差异仅存在于薄清单中。修改 Skill 行为时只需更新这一份 canonical Skill，不需要分别维护 Codex 和 Cursor 版本。

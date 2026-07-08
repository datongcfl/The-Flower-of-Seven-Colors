# datongcfl-repository

> 个人 / 团队的 **Agent 知识库与参考仓库** —— 沉淀 AI Agent 方法论、垂直行业 Agent 设计模板，以及本地开源项目参考镜像。

本仓库是一个面向「AI Agent 设计 / 调优 / 调研能力增强」的知识库，所有文档对外发布时**不含本地绝对路径、服务器地址与内部代号**（脱敏基线）。

## 📚 目录结构

```
datongcfl-repository/
├── README.md                      # 本文件：仓库说明与结构
├── VERSION                        # 仓库大版本号（语义化版本）
├── CHANGELOG.md                   # 版本变更史
├── CONTRIBUTING.md                # 如何新增 / 修订 agent 文档的规范
├── LICENSE                        # 许可（CC0-1.0，知识库文档通用）
├── .gitignore                     # 排除 references/、日志、二进制噪声
│
├── AGENT_METHOD_REFERENCE.md           # 外部权威方法论整合参考
├── AGENT_TUNING_ASSISTANT_ROLE.md      # Agent 调优助手角色定义
├── AGENT_SEARCH_RESEARCH_ENHANCEMENT.md# 搜索 / 调研能力增强方案
│
├── agents/                        # Agent 定义与模板
│   └── 互联网产品/
│       ├── INTERNET_PRODUCT_AGENT_TEMPLATE.md
│       └── 云枢_AGENT.md
│
├── scripts/                       # 正式脚本（克隆 / 修复 / 探针），*.log 被忽略
│
├── audits/                        # 第三方系统审计报告（markdown）
│
└── references/                    # 本地开源参考镜像（git 忽略，不进版本控制）
```

## 🗂 内容说明

| 文件 / 目录 | 作用 |
|---|---|
| `AGENT_METHOD_REFERENCE.md` | 整合 Anthropic / OpenAI 等权威 Agent 设计模式（路由、编排者-工作者、评估者-优化器…） |
| `AGENT_TUNING_ASSISTANT_ROLE.md` | 「Agent 调优助手」角色定义（scope、边界、能力） |
| `AGENT_SEARCH_RESEARCH_ENHANCEMENT.md` | 让 Agent 获得语义搜索 + 干净抓取的增强方案 |
| `agents/` | 垂直行业 Agent 模板与具体实例（互联网产品方向起步） |
| `scripts/` | 克隆开源仓库、修复、截图等运维脚本 |
| `audits/` | 对第三方开源系统的审计记录 |
| `references/` | 拉取的开源仓库镜像，**仅本地参考，不进 git**（各带自身 LICENSE） |

## 🔖 版本管理

- 仓库大版本见 `VERSION`（如 `0.1.0`），变更记录在 `CHANGELOG.md`。
- 单篇文档在 frontmatter / 文件头带 `version` + `updated` + `status` 字段，便于迭代：
  ```yaml
  version: 0.1
  updated: 2026-07-08
  status: active
  ```
- 里程碑用 `git tag vX.Y` 标记。

## 🤝 贡献规范

见 [CONTRIBUTING.md](./CONTRIBUTING.md)：新增 / 修订文档的命名、版本头、脱敏要求。

## 📄 许可证

文档内容以 **CC0-1.0** 发布（见 [LICENSE](./LICENSE)）。
`references/` 下的第三方仓库保留各自原始许可证，本仓库不重新分发其内容。

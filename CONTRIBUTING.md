# 贡献规范（CONTRIBUTING）

本仓库是 **Agent 知识库**，用于沉淀 AI Agent 方法论、模板与参考。
以下规则保证仓库「干净、可追溯、对外可发布」。

## 1. 文档命名

- Agent 门面文档（根目录）：`AGENT_<主题>.md`
- 垂直行业模板：`agents/<行业>/<行业>_AGENT_TEMPLATE.md`
- 具体 Agent 实例：`agents/<行业>/<实例名>_AGENT.md`
- 审计报告：`audits/PMS_AUDIT_<主题>.md`

## 2. 版本头（必填）

每篇文档**必须**带版本字段，便于迭代：

- 根目录 markdown：文件头加 YAML frontmatter
  ```yaml
  ---
  title: <文档标题>
  version: 0.1
  updated: 2026-07-08
  status: active   # active | draft | deprecated
  ---
  ```
- 已有 frontmatter 的文档：在其内追加 `version` / `updated` / `status` 三个字段。

版本号规则：

- 小修（错别字、表述优化）→ 仅更新 `updated`
- 内容新增 / 结构调整 → 升 `version` 次版本（0.1 → 0.2）
- 仓库级里程碑 → 同步升 `VERSION` 并记一笔 `CHANGELOG.md`

## 3. 脱敏基线（硬性，因仓库为 public）

对外文档**禁止出现**：

- 本地绝对路径（如 `D:\...`、`/opt/...`）
- 服务器地址 / IP / 端口
- 内部人员代号、内部系统代号

替代写法：用「本地知识库根目录（路径脱敏）」「生产服务器」「编排 / 执行 / 审查 / 运维 Agent」等泛化表述。

## 4. 目录归属

| 内容类型 | 放哪 |
|---|---|
| Agent 知识文档 | 根目录 `AGENT_*.md` 或 `agents/` |
| 正式脚本 | `scripts/`（运行日志 `*.log` 自动忽略） |
| 审计报告 | `audits/` |
| 第三方开源镜像 | `references/`（**默认不进 git**，见 `.gitignore`） |

**不要**把克隆的开源仓库、日志、截图直接堆在根目录。

## 5. 提交约定

- 提交信息格式：`docs(<模块>): <动作> <简述>`
  例：`docs(agent-search): v0.2 add Exa MCP config steps`
- 里程碑打 tag：`git tag v0.2` 后 `git push --tags`
- 改完跑一次 `git status` 确认无 untracked 噪声再推送。

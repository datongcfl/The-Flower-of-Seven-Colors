# 变更日志

本知识库采用语义化版本，与根目录 `VERSION` 文件保持一致。各 Agent 文档内部另以 frontmatter 的 `version` 字段标记自身版本（首次纳入版本管理为 `0.1`）。

## [0.1.0] - 2026-07-08

### 新增（版本化管理起步）
- 为全部 5 份 Agent 文档加版本头（`version: 0.1` / `updated: 2026-07-08` / `status: active`），纳入版本迭代管理：
  - `AGENT_METHOD_REFERENCE.md` — AI Agent 方法论外部权威参考（整合版）
  - `AGENT_TUNING_ASSISTANT_ROLE.md` — Agent 调优助手角色 spec
  - `AGENT_SEARCH_RESEARCH_ENHANCEMENT.md` — 搜索 / 调研能力增强方案
  - `agents/互联网产品/INTERNET_PRODUCT_AGENT_TEMPLATE.md` — 互联网产品 Agent 行业模板
  - `agents/互联网产品/云枢_AGENT.md` — 云枢 Agent 实例化定义（已脱敏）
- 建立仓库级 `VERSION` 与 `CHANGELOG.md`，统一管理知识库版本。

### 修复（脱敏，因仓库为 public）
- `AGENT_METHOD_REFERENCE.md`：移除本地绝对路径与内部 Agent 代号，统一泛化为「执行 / 审查 / 运维 / 编排 Agent」。
- `AGENT_TUNING_ASSISTANT_ROLE.md`：移除本地知识库绝对路径，改为脱敏描述。
- `agents/互联网产品/云枢_AGENT.md`：历史已脱敏（见提交 `522e5ba`）。

### 说明
- 版本号规则：文档首次纳入管理记为 `0.1`；后续实质更新递增小版本；仓库整体发布以 `VERSION` 大版本为准。
- 所有对外文档遵循脱敏口径：不出现本地绝对路径、生产服务器路径、内部人员代号、内部文件名。

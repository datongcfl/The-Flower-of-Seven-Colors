---
title: AI Agent 方法论外部权威参考（整合版）
version: 0.1
updated: 2026-07-08
status: active
---

# AI Agent 方法论外部权威参考（整合版）

> 用途：优化团队多 Agent 体系的工作效率与方法。
> 对应本地文档：`reconciliation/docs/MULTI_AGENT_WORKFLOW.md`、`reconciliation/AGENT_PROTOCOL.md`。
> 整理时间：2026-07-08

## 来源清单

| # | 标题 | 来源 | URL | 核心贡献 |
|---|------|------|-----|---------|
| 1 | Building Effective Agents | Anthropic (Erik S., Barry Zhang, 2024-12) | https://www.anthropic.com/research/building-effective-agents | 工作流 vs 自主 Agent 决策框架 + 5 种编排模式 |
| 2 | Effective Context Engineering for AI Agents | Anthropic Applied AI (2025-09) | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | 上下文工程四术：写/选/压/隔 |
| 3 | AGENTS.md 开放规范 | Agentic AI Foundation (Linux Foundation) | https://agents.md | 给 Agent 看的 README 格式与就近加载机制 |
| 4 | Create Custom Subagents | Claude Code Docs (Anthropic) | https://code.claude.com/docs/en/sub-agents | 子代理文件格式、工具/模型隔离、并行化 |

---

## 一、何时用工作流 / 何时用自主 Agent（来源 1）

**总原则**：先找最简单方案，只在简单方案不够时才加复杂度。Agent 系统用「延迟+成本」换「任务性能」。

- **工作流（Workflow）**：预定义代码路径编排 LLM/工具。适合**定义良好、可预测**的任务。
- **自主 Agent**：LLM 动态决定流程与工具。适合**开放性问题**（步骤数无法硬编码），需信任模型决策。
- **警告**：许多应用只靠「单次 LLM 调用 + 检索 + 示例」就够，别盲目上复杂架构。

### 五种核心编排模式（直接可对照你们的多 Agent 设计）

| 模式 | 机制 | 你们的对应场景 |
|------|------|---------------|
| **提示链 Prompt chaining** | 顺序步骤，中间可加程序化门控 | 对账流程：上传→配置→跑对账→看结果（已是固定链路） |
| **路由 Routing** | 输入分类导向专用处理 | 把任务按业务域分到 执行/辅助/运维 Agent（你们靠人肉派单，可改为自动路由） |
| **并行化 Parallelization** | 子任务并行 + 程序化聚合 | 多个子代理同时扫不同文件域 / 多视角代码审查 |
| **编排者-工作者 Orchestrator-workers** | 中央动态拆任务、派 worker、综合 | 编排 Agent + 执行/审查/运维 Agent 的现成拓扑 |
| **评估者-优化器 Evaluator-optimizer** | 一模型生成、一模型评估反馈循环 | 审查 Agent 对 执行 Agent 的审查-返工闭环 |

> 关键区别：并行化子任务**预定义**；编排者-工作者子任务**由编排者按输入动态决定**（编码中改几个文件依赖具体任务，无法预定义）。

---

## 二、上下文工程四术：写 / 选 / 压 / 隔（来源 2）

上下文窗口有限，存在「上下文腐烂」——token 越多召回与推理精度下降。把上下文当**稀缺资源**。

1. **写 Write**：系统提示从最小必要集起步，用 XML/Markdown 分节；工具自包含、容错、无歧义；用**典型 canonical 示例**而非穷举边缘规则（一图胜千言）。
2. **选 Select**：保持「信息丰富但紧凑」，剔除冗余；**精简工具集**避免重叠；即时检索（just-in-time）——`CLAUDE.md` 放基础，其余用 glob/grep 按需加载，别预载全量。
3. **压 Compress**：窗口将满时用模型高保真总结历史（保留架构决策、未解 bug、实现细节），丢弃冗余工具输出；最轻量是「工具结果清除」。
4. **隔 Isolate**：子代理在**独立干净上下文**里做深度探索，消耗数万 token 但只返回 1k–2k 浓缩摘要。主代理只综合结果。

**对你们的落地启示**：
- `AGENTS.md` / `AGENT_PROTOCOL.md` 别越写越长塞全量规则 → 改为「最小必要 + 按需检索」。
- 大范围代码搜索（你们用 code-explorer 子代理）正是「隔离」实践：细节留在子代理，主对话只拿摘要。
- 长周期任务用结构化笔记（`NOTES.md`/entry-packet）跨会话延续状态——对应 `MULTI_AGENT_WORKFLOW.md` 的 entry-packets。

---

## 三、AGENTS.md 规范（来源 3）

- 本质：**给 Agent 看的 README**，标准 Markdown，放仓库根或子包，无强制 schema。
- **就近优先**：编辑文件时，距离最近的 `AGENTS.md` 生效；冲突时最近者胜出；显式用户指令优先级最高。
- **Monorepo 嵌套**：子包内可放独立 `AGENTS.md`（OpenAI 主仓有 88 个），就近覆盖。
- **可执行检查**：列出 build/test 命令，Agent 会尝试执行并在完成前修复失败。
- **推荐章节**：项目概览 / 构建测试命令 / 代码风格 / 测试指令 / 安全注意 / PR 规范。

**对你们的落地启示**：
- 你们已有 `AGENTS.md`（对账系统）+ `AGENT_PROTOCOL.md`（协作）。建议保留 `AGENTS.md` 作「给 Agent 的事实/SOP」，把跨 Agent 协作锁规则留在 `AGENT_PROTOCOL.md`。
- `hotel-pms` 目前**不是 git 仓库且无 AGENTS.md** → 这是风险点，建议初始化 git 并补 `AGENTS.md`（见下）。

---

## 四、子代理配置与并行化（来源 4）

子代理 = 带 YAML frontmatter 的 Markdown 文件，frontmatter 配置元数据，正文作系统提示。

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---
You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

**frontmatter 关键字段**：`name`(唯一,小写连字符) / `description`(触发场景,可加 "use proactively" 鼓励自动委派) / `tools`(允许列表,最小权限) / `model`(可路由 haiku 降本)。

**作用域优先级**：托管 `.claude/agents/` > `--agents` 参数 > 项目 `.claude/agents/`(建议入版本控制) > `~/.claude/agents/` > 插件。

**并行化与隔离最佳实践**：
- 子代理在**独立上下文窗口**运行，主会话只看摘要 → 适合「跑测试/抓文档/处理日志」等重输出任务。
- `isolation: worktree` 给子代理独立 git 副本，不影响主 checkout。
- 并行研究：对独立调查同时派生多子代理，再综合（例：「并行研究 auth/db/api 模块」）。
- 最小权限：审查代理禁 `Edit`/`Write`；简单任务路由 `haiku`。

**对你们的落地启示**：
- 把 审查 Agent 做成 `tools: Read,Grep,Glob`(禁写) 的审查子代理；运维 Agent 用 `isolation: worktree` 避免脏主仓。
- 这与 `AGENT_PROTOCOL.md` 的「文件锁/最小权限」原则一致，但工程化成了配置而非口头约定。

---

## 五、可立即执行的优化清单（映射到你们现状）

| 痛点（来自 MULTI_AGENT_WORKFLOW） | 借鉴的方法 | 具体动作 |
|----------------------------------|-----------|---------|
| 派单靠人肉 | 来源1 路由模式 + 来源3 自动加载 | 把任务按业务域自动路由到对应 Agent，entry-packet 标准化 brief |
| 接单靠自觉 | 来源4 子代理 description "use proactively" | 在子代理描述里声明触发条件，让编排者自动委派 |
| 状态不透明 | 来源2 结构化笔记 | 用 `events.jsonl` + `NOTES.md` 做单一事件流与跨会话状态 |
| 串行慢 | 来源1 并行化 + 来源4 并行子代理 | 独立调查/审查并行派生；大搜索用隔离子代理 |
| 上下文膨胀 | 来源2 选/压/隔 | AGENTS 保持最小必要集，按需检索；子代理隔离细节 |
| 跨平台鸿沟 | 来源3 AGENTS.md 通用格式 | 各仓库统一 `AGENTS.md`，Codex/Claude/CodeBuddy 都能读 |

---

## 六、下一步建议（待董事长拍板）

1. 将 `本地任务队列目录（路径脱敏）` 任务队列真正落地（tasks/assignments/claims/events.jsonl + entry-packets）。
2. 把 审查/运维 Agent 等角色固化为子代理配置文件（.claude/agents/ 或等效），最小权限 + 自动委派。
3. 精简 `AGENTS.md`/`AGENT_PROTOCOL.md` 为「最小必要集 + 按需检索」，缓解上下文腐烂。
4. 给 `hotel-pms` 初始化 git 并补 `AGENTS.md`（当前无版本控制、无 Agent 上下文，是风险点）。

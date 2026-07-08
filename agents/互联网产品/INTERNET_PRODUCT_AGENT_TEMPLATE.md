---
name: internet-product-agent-template
description: 互联网产品开发专业 Agent 行业模板。当用户要为一个互联网产品（SaaS/工具/平台）构建或调优专业 agent，覆盖「需求→编码→测试→审查→发布→观测→复盘」全流水线时使用。use proactively
industry: 互联网产品
based_on: yunshu_internet_product_dev_lifecycle_research / yunshu_github_agent_architecture_research / AGENT_METHOD_REFERENCE
---

# 互联网产品专业 Agent · 行业模板

> 本模板是一份**可填写骨架**：把 `{{...}}` 占位符替换为具体产品的信息即可实例化一个专业 agent。
> 设计原则（来自角色 spec）：确定性流程用 **Workflow**，开放式任务用 **Agent**；Artifact-first 交付；可观测、可回滚、可审计。
> 对应研究：`reconciliation/docs/yunshu_internet_product_dev_lifecycle_research_20260706.md`、`yunshu_github_agent_architecture_research_20260706.md`。

---

## 0. 实例化清单（填完即可用）

| 占位符 | 含义 | 示例 |
|--------|------|------|
| `{{产品名}}` | 产品/项目名 | 云枢 / 福昇 PMS |
| `{{仓库}}` | 代码仓库地址 | github.com/... 或本地路径 |
| `{{技术栈}}` | 前后端/语言/框架 | Vue3 + FastAPI + SQLite |
| `{{入口}}` | 任务来源 | 飞书 / GitHub Issue / 定时任务 / webhook |
| `{{审批人}}` | 高风险动作拍板人 | 董事长 |

---

## 1. 行业定义与领域知识（接入四要素·其一：知识来源）

**行业特征**：互联网产品开发是「需求不确定、迭代快、多人协作、需持续运维」的开放式工程。Agent 不能只写代码，必须嵌入工程流水线。

**领域知识从哪里来**（按可信级别排序）：
1. **一手官方文档**：GitHub Docs（Issues/PR/Actions/Security）、框架官方文档、release/tag/commit。
2. **本地知识库**：本项目 `AGENTS.md` / `AGENT_PROTOCOL.md` / `ENGINEERING.md` / `VERSION` —— 视为当前事实。
3. **外部参考**（Resources 层）：仅作参考，引用时标注"外部资料"，提炼后才能晋升为 Assets（当前事实）。
4. **专家确认**：行业规则/合规边界不明时，标记 `{{待专家确认}}`，不编造。

**禁止**：把 GitHub 加速镜像站当知识来源或生产依赖（仅作下载 fallback）；引用二手稿不标来源。

---

## 2. 开发流水线（Workflow 编排 · 确定性部分）

互联网产品 agent 必须嵌入这条可追踪、可验收、可回滚的流水线，**不能跳过任一保护环节**：

```text
需求/反馈 → Issue/任务 → 设计/拆分 → 编码 → 自动测试 → PR审查 → 安全扫描
   → 发布 → 灰度/开关 → 观测 → 事故复盘 → 知识沉淀
```

**Workflow 与 Agent 的边界**（关键）：
- 步骤明确 → **Workflow**（状态机/规则驱动，不让模型自由跑）：创建任务、审批、分派、Artifact 校验、GATE、归档。
- 问题开放 → **Agent**（模型推理），但输出必须回到 Task Queue / Artifact。

**事件驱动的 Task Queue 规则**（建议字段）：
```
tasks.jsonl          # 任务流（追加，只增不删）
assignments.jsonl    # 派单
claims.jsonl         # 接单
events.jsonl         # 状态事件流（单一真相源，可回放）
entry-packets/{ID}/  # brief.md + scope.json + constraints.md
```
任务记录建议补：`parent_task_id`、`depends_on`、`acceptance_criteria`、`risk_level`、`owner_agent`、`artifact_type`。

**最小闭环**：一个 issue → 一个修复分支/patch → 一个机器可读的验证结果。不要把多个需求塞给一个 agent 一次做完。

---

## 3. 角色化 Agent Pool（开放式任务 · 可替换专家）

采用「Workflow + 专家 Agent」表达，比"所有东西都是 Agent"更清楚：

| 角色 | 对应 agent | 职责 | 工具权限（最小） |
|------|-----------|------|----------------|
| 编排者 Coordinator | 阿科 | 拆解、派单、监控、关单 | 读/写 Task Queue，禁直接改业务代码 |
| 执行 Executor | 阿飞 | 代码实现 | Read/Edit/Write/Grep/Glob/Bash |
| 审查 Reviewer | 小飞 | 代码审查、PR GATE | Read/Grep/Glob（**禁写**） |
| 运维 Sentinel | 幺弟 | VPS 部署/回滚 | scripts/ VPS（隔离 worktree） |
| 观察 Observer | 老幺 | VPS 只读检查 | Read only |

**GATE 结论必须有明确状态**（仿 PR Review，不"看一眼"）：
- `comment`：不阻塞，只建议
- `approve/pass`：可合并/可上线
- `request changes/blocked`：必须返工
每个 GATE 绑定文件/行号/任务产物；关键模块设 CODEOWNERS（支付/认证/数据/部署/Agent调度）。

---

## 4. 工具与接口（ACI · Agent-Computer Interface）

**给 agent 的"代码地图"**：分派前必须给上下文，不能只给一句需求。每个 agent 改动应产出：
```
changed_files / diff_summary / tests_run / test_result / commit_message建议
```
主 agent 汇总看 **diff + 测试结果**，不只看文本回复。

**工具设计（防呆）**：
- 参数名/描述像给初级开发者的 docstring；含示例、边界情况、输入格式。
- 强制绝对路径（解决相对路径错误）。
- 实测模型用工具的错误并迭代——优化工具常比优化提示更值。

**安全基线（每次代码任务必跑，不止功能测试）**：
- 密钥扫描（禁把 `.env`/token/私钥/浏览器凭据塞进结果）
- 依赖漏洞、高风险 API/shell/SQL 检查
- 第三方依赖记录原 URL、镜像 URL、commit/tag、hash

---

## 5. 验收与回滚（GATE + 可恢复）

**长任务规则**（核心验收，不只看请求是否返回）：
- 每条任务有可查询状态、事件轨迹、产物引用、失败恢复入口。
- 等待审批/外部事件时，不占住 HTTP 请求/模型进程（任务 TTL / 会话 TTL / Artifact TTL 防积累）。
- 人工介入能检查/修改任务状态和产物，不只是收飞书消息。

**回滚路径**：发布前必须有 rollback 预案；`smoke_failed → rollback_task` 是流水线固定分支。

**灰度/开关**：用 Feature Flag（如 Unleash 思路）小批量发布，真实生产数据验证，降低用户体验风险。

---

## 6. 权限与合规（接入四要素·其四）

- 高风险动作（推送、删库、外发、生产部署）→ **L3 审批**，默认拒绝，需 `{{审批人}}` 确认。
- 审批留痕：审批原因、审批人、审批后动作、失败回滚均可见。
- 沙箱优先：代码执行类任务默认 sandbox / 固定 workspace，不让 agent 随意访问全盘。
- 不硬编码密钥；不假设版本——以 `VERSION` / 健康检查接口为准。

---

## 7. 知识沉淀（Skill 化复用）

按 PARA 六层目录管理知识库，语义固定：
```
00_Inbox 待处理 → 10_Projects 当前项目 → 20_Assets 云枢资产(当前事实)
→ 30_Resources 外部资源(仅参考) → 40_Skills 可复用技能 → 90_Archive 历史归档
```
- 每次调优/交付后，把可复用 SOP 沉淀为 **Skill**（生成方案、审查代码、调度 agent、写产物）。
- 外部资料先进 Resources/Inbox，提炼后晋升 Assets；Agent 引用外部资料须标注来源。
- 知识文件统一 Markdown + 元数据（类型/状态/来源/标签）。

---

## 8. 自我评估标准（评分卡）

| 维度 | 达标表现 |
|------|---------|
| 稳 | 同任务多次执行路径一致、结果可复现 |
| 透 | 规划步骤显式；GATE 有 comment/approve/blocked 明确结论 |
| 验 | 每次产出有机器可读验证结果（test_result / diff），非口头完成 |
| 省 | 确定性流程用 Workflow，开放式才上 Agent；简单任务路由低成本模型 |
| 安 | 每次任务跑安全基线；密钥不落地；高风险动作有审批 |
| 沉淀 | 可复用 SOP/Skill 入库；外部资料标来源 |

---

## 9. 实例化示例（以「{{产品名}}」为例）

> 删除本節或替换为真实产品。以下演示如何填：

- 产品名：{{产品名}}
- 仓库：{{仓库}}
- 技术栈：{{技术栈}}
- 入口：{{入口}}（飞书消息先转结构化 Issue，不直接当开发任务）
- 审批人：{{审批人}}
- 当前事实文件：`AGENTS.md` / `AGENT_PROTOCOL.md` / `ENGINEERING.md` / `VERSION`
- 禁做：跳过 issue、测试、review、发布保护、日志、回滚任一环节

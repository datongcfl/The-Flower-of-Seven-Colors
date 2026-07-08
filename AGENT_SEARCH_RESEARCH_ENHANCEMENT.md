---
title: 搜索 / 调研能力增强方案（Agent 调用大模型提效）
version: 0.1
updated: 2026-07-08
status: active
---

# 搜索 / 调研能力增强方案（Agent 调用大模型提效）

> 目标：找到能**提高 agent 搜索能力与调研能力**的开源方案，并明确如何用它们增强当前 agent。
> 结论先行：增强 agent 能力有两条路线——**工具层（API 基础设施）** 与 **应用层（完整自主研究应用）**，二者不是替代关系，最优是组合。
> 适用：配合 `AGENT_METHOD_REFERENCE.md`（上下文工程四术 + 编排模式）与 `AGENT_TUNING_ASSISTANT_ROLE.md`（调优助手角色）一起使用。

---

## 0. 一句话结论

- **想让"当前的我（agent）"直接变强** → 用 **Firecrawl + Exa**（工具层，接成 MCP 即可调用）。
- **想要一个开箱即用的自主研究产品** → 用 **GPT Researcher / MindSearch / STORM / Perplexica**（应用层，单独部署）。
- **最优选** → **Firecrawl + Exa 作底层引擎**，喂给 **GPT Researcher / MindSearch** 这类编排框架当 retriever。

---

## 1. 项目速查表（6 个候选）

| 项目 | 地址 | Stars/版本 | 许可证 | 类别 | 增强的能力 |
|------|------|-----------|--------|------|-----------|
| **Firecrawl** | https://github.com/mendableai/firecrawl | v2.11.0 (2026-06) | AGPL-3.0（SDK MIT） | 工具层 API | 抓取/提取（把网页变干净 Markdown） |
| **Exa** | https://exa.ai （docs: exa.ai/docs） | 2026-06 更新 | 商业 API（有免费额度） | 工具层 API | 语义/神经搜索（按含义召回） |
| **MindSearch** | https://github.com/InternLM/MindSearch | v0.1.0 (2024-11) | Apache-2.0 | 应用层 框架 | 多智能体并发搜索 |
| **GPT Researcher** | https://github.com/assafelovic/gpt-researcher | v3.5.1 (2026-06) | MIT | 应用层 Agent | 深度自主研究写长报告 |
| **STORM / Co-STORM** | https://github.com/stanford-oval/storm | v1.1.0 (2025-01) | MIT | 应用层 系统 | 多视角知识综合（维基级） |
| **Perplexica** | https://github.com/Perplexica/Perplexica | — | — | 应用层 引擎 | 开源 AI 搜索引擎（Perplexity 平替） |

---

## 2. 工具层（直接增强"我"的能力）

### 2.1 Firecrawl —— "取得净"
- **定位**：用于大规模搜索、抓取、与网络交互的 API；把任意网站转成干净 **Markdown / 结构化 JSON**，供 agent 直接消费。
- **核心端点**：
  - `scrape`：URL → markdown / HTML / 截图 / 结构化 JSON
  - `crawl`：整站抓取（支持 limit）
  - `extract`（已演进为 `agent` 端点）：描述需求即可自动搜索+导航+抽取，支持 Pydantic/JSON Schema 输出
  - `map`：发现网站全部 URL，可按相关性过滤
  - `search`：搜网获全文
- **为什么增强调研能力**：
  - 自动处理代理轮换、编排、速率限制、JS 阻塞内容，**覆盖 96% 网页（含 JS 重页），P95 延迟 3.4s**
  - LLM-ready 干净输出，**直接降低 token 成本**
  - 可作为 **MCP Server** 接入任意 agent（Claude Code / OpenCode 等）
- **注意**：它是基础设施，不替 agent 做决策规划，只负责"看"和"取"。

### 2.2 Exa —— "找得准"
- **定位**：为 AI 量身定制的自定义搜索引擎；API 是**面向 agent 的搜索基础设施**。
- **核心能力**：
  - **搜索类型（延迟-质量剖面）**：`auto`(~1s) / `instant`(~250ms) / `fast`(~450ms) / `deep-lite`(4s) / `deep`(4-15s) / `deep-reasoning`(12-40s)
  - **内容效率**：`highlights` 仅提取相关 token 的 **10x 高效摘要**；`full text` 全文本
  - **结构化输出**：`output_schema` 直接出 JSON；`Grounded answers` 可靠抽取
  - **分类索引**：company(50M+) / people(1B+) / research paper(100M+) / news / financial report
  - SDK：`exa-py`、`exa-js`
- **为什么增强搜索能力**：
  - 训练的模型把全文浓缩成 LLM 所需密集信息（语义/神经搜索，按含义而非关键词召回）
  - 深度模式（`deep`/`deep-reasoning`）为复杂研究做跨源综合与多步推理
  - 高亮内容大幅压缩输入 token，提升推理速度与经济性
- **注意**：商业 API，有免费额度，需 API Key，是外部依赖。

### 2.3 工具层如何补"我"的短板
当前 agent 用内置 `web_fetch`，有两个真实短板：
1. **关键词匹配弱** → Exa 的语义/神经搜索补上
2. **动态页抓不到 / 抓回噪音 HTML** → Firecrawl 的 JS 渲染 + 干净 Markdown 补上

组合：**Exa 负责"找得准"，Firecrawl 负责"取得净"**。

---

## 3. 应用层（独立运行的自主研究系统）

### 3.1 MindSearch（InternLM，Apache-2.0）
- 多智能体 Web 搜索框架（类 Perplexity Pro / SearchGPT）。
- 架构：基于 Lagent v0.5，异步多 agent 并发多查询搜索；`model_format`（推理）与 `search_engine`（检索）角色解耦。
- 支持搜索引擎：DuckDuckGo / Bing / Brave / Google / Tencent。
- 提升：模仿人类思维拆解问题分头检索，消除单查询信息盲区。

### 3.2 GPT Researcher（MIT，v3.5.1）
- "首个开放式的深度研究代理"：用任意 LLM 对任意数据做深度研究。
- 架构：**规划器（planner）+ 执行器（execution）** 分工；爬虫 agent 并行抓取 >20 源，出版 agent 过滤聚合。
- 能力：生成 >2000 词带引用报告；Deep Research 树状递归；MCP 客户端（混合 web + GitHub/DB）；支持 LangGraph/AG2 多代理；本地文档研究（PDF/CSV/Excel）。
- 提升：并行化 + 多源聚合降低幻觉与偏见；分段总结突破 token 限制。

### 3.3 STORM / Co-STORM（斯坦福 OVAL，MIT，29.9k stars）
- 基于检索与多视角提问，自动生成维基级长文（带引用）。
- 机制：视角引导提问 + 模拟"维基作者×领域专家"对话。
- 工程：基于 **DSPy** 模块化，兼容 **LiteLLM** 所有模型；检索模块支持 Tavily/Bing/Brave/DuckDuckGo/Google 等。
- 提升：知识综合与研究深度，适合前期调研与知识整理。

### 3.4 Perplexica（开源 AI 搜索引擎）
- Perplexity 的开源平替，支持多种搜索 API，提供搜索问答界面。
- 定位：应用层搜索入口，可与上式框架组合。

---

## 4. 对比与选型

| 维度 | Firecrawl + Exa（工具层） | MindSearch/GPT Researcher/STORM/Perplexica（应用层） |
|------|--------------------------|------------------------------------------------------|
| 类别 | 基础设施 API（工具层） | 端到端 agent 应用（产品层） |
| 增强对象 | 当前 agent 的"搜索/抓取"能力本身 | 一个独立运行的系统 |
| 集成方式 | 作为 MCP / SDK 接入 agent，直接调用 | 单独部署成服务，agent 再调用或人工看结果 |
| 与内置 web_fetch 关系 | 替代/增强 web_fetch | 平行存在的另一系统 |
| 成本 | 有免费额度，超出按量（外部依赖） | 开源自托管，只付 LLM API 费 |
| 可控性 | 依赖第三方服务 + 密钥 | 全栈自己掌控 |

**选型建议**：
- 目标=让当前 agent 变强 → **Firecrawl + Exa**（即插即用增强工具）。
- 目标=开箱自主研究产品 → **GPT Researcher / MindSearch**。
- 目标=最优选 → 组合：Firecrawl + Exa 作引擎，GPT Researcher / MindSearch 作编排。

---

## 5. 落地到"提高我"：MCP 接入步骤

要让当前 agent 真正获得 Exa / Firecrawl 能力，需：

1. **申请 Key**（均有免费额度）：
   - Firecrawl：firecrawl.dev 注册拿 `fc-...` Key
   - Exa：exa.ai 注册拿 `exa-...` Key
2. **配置 MCP Server（本仓库已内置配置）**：
   - 仓库根 `.mcp.json` 已声明 `exa` 与 `firecrawl` 两个 MCP Server，使用环境变量占位：
     - `EXA_API_KEY` → Exa MCP（`exa-mcp-server`）
     - `FIRECRAWL_API_KEY` → Firecrawl MCP（`firecrawl-mcp`）
   - 把 `<YOUR_EXA_API_KEY>` / `<YOUR_FIRECRAWL_API_KEY>` 替换为真实 Key（或设置同名环境变量后由支持变量展开的客户端注入 `${EXA_API_KEY}`）。
   - 详细步骤见 `mcp/README.md`；改完配置后部分客户端需重启以加载新 MCP Server。
   - 另有托管远程免 npx 方式：Exa `https://mcp.exa.ai/mcp`；Firecrawl 参考官方 MCP 章节。
3. **接入后行为变化**：
   - 搜索 → 走 Exa（语义召回 + 高效高亮）
   - 抓取 → 走 Firecrawl（JS 页、干净 Markdown、结构化 JSON）
   - 调研质量与 token 效率明显提升。

> ⚠️ 配置涉及外部网络请求与密钥，需在用户明确批准后操作；密钥不入库、不硬编码。

---

## 6. 与现有 agent 体系映射

| 现有资产 | 本方案如何衔接 |
|----------|---------------|
| `AGENT_METHOD_REFERENCE.md` 四术（写/选/压/隔） | Exa 高效高亮 = "选/压"；Firecrawl 干净输出 = "压" |
| `AGENT_TUNING_ASSISTANT_ROLE.md` 模型路由降本 | Exa/Firecrawl 的 `instant/fast` 档 = 简单任务走廉价路径 |
| `agents/互联网产品/云枢_AGENT.md` 工具防呆 + 安全基线 | Exa/Firecrawl 作为新工具需纳入 ACI 防呆与密钥扫描 |
| LiteLLM（见 `AGENT_LLM_OPTIMIZATION.md`） | 用 LiteLLM 统一路由 Exa/Firecrawl + 多 LLM，做成本追踪 |

---

## 7. 参考链接

- Firecrawl：https://github.com/mendableai/firecrawl
- Exa：https://exa.ai · https://exa.ai/docs
- MindSearch：https://github.com/InternLM/MindSearch
- GPT Researcher：https://github.com/assafelovic/gpt-researcher
- STORM：https://github.com/stanford-oval/storm
- Perplexica：https://github.com/Perplexica/Perplexica

> 注：本文档基于 2026-07-08 各仓库公开页面抓取整理；版本号/特性以各仓库最新为准。API 类（Exa/Firecrawl 云服务）可能调整计费与免费额度，使用前请查官方最新说明。

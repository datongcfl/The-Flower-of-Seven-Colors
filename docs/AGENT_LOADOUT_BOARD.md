# Agent 装备台（Loadout Board）概念与设计草案

> 状态：**草案 / 调研阶段**。核心概念已定，交互细节与实现待打磨。
> 关联：`AGENT_SEARCH_RESEARCH_ENHANCEMENT.md`（工具层方法论）、`云枢_AGENT.md`（Agent Pool 编排）、`scripts/research_report.py`（已落地的"侦察兵"装备套装）。

---

## 1. 一句话定义

**装备台是一个独立于 Agent 之外的「元工具」**：每新装一个 Agent，运行一次它来给 Agent 上"装备"（写入工具 / MCP 配置）；需求变了再跑一次做增删。它不进 Agent 本体，只管 Agent 的"装备栏"。

---

## 2. 核心比喻：Agent 即游戏新建人物

大模型是"脑子"，但脑子本身不能动手——Agent 能做什么，由它**装备了什么工具**决定（武士还是射手，看武器不是看脑子）。

| 游戏 | Agent 架构 | 说明 |
|------|-----------|------|
| 新建人物（空白壳） | Agent 实例 | 刚出生啥都不会 |
| 脑子 | 大模型（推理 + 语言核心） | CPU + 语言中枢，**本身不能动手**，必须靠装备作用于世界 |
| 武器 / 防具（装备） | 工具 / MCP / SDK | "手和脚"，决定近战还是远程 |
| 武士 / 射手 | 职能专精 | 由**装备组合**决定，不是脑子决定 |
| 职业背景故事 | 系统提示词 / 角色指令 | 决定性格、准则、说话方式 |
| 经验书 / 已学技能 | 长期记忆 / 知识库（RAG） | 角色积累的认知 |
| 视野 / 短期记忆 | 上下文窗口 | 当前能"看到"多少 |
| 连招 macro | 编排工作流 | 多个装备的组合技 |
| 装备解锁 / 使用限制 | 权限 / 安全基线 | 某些武器要授权才能用（密钥 = 使用许可）|

---

## 3. 装备台的产品定位

- **独立性**：它是外部程序，不是 Agent 的功能模块。类比——Agent 是角色存档，装备台是外部配装器，只改存档里的"装备栏"，不碰角色本体代码。
- **生命周期管理**：`install`（首次上装）→ `update`（需求变动增删）。一次运行 = 应用一套装备方案。
- **状态可视化**：读 Agent 当前配置 ↔ 对比"可用装备目录"，实时标出每个格子的状态：
  - `空槽`（未装备）
  - `已装未连`
  - `已连`（绿，可用）
  - `缺密钥`（黄，需填使用许可才能激活）

### 交互形态（草案）
- 新建 Agent → 周围环绕一圈**装备格**（按职能分栏：侦察类 / 工程类 / 数据类 / 通知类）。
- 用户按需点选装配；可重跑变动。
- 形式建议：**CLI + 终端格子视图**（最易分发、零 GUI 依赖、别人 clone 即用），后续可升级 TUI / Web。

### 它"动"什么
- **装备目录** `loadout_catalog.toml`：描述所有可用装备（每件 = 一个 MCP server 的 url/命令 + 分类 + 是否需密钥），即"武器架清单"。
- **Agent 配置**：每个 Agent 自己的配置文件（记录当前装了哪些）。
- **状态灯来源**：程序读 Agent 配置对比装备目录 → 标出已装 / 未装 / 缺密钥。

---

## 4. 市场竞品扫描（调研日期 2026-07-08，工具 Exa + Firecrawl）

结论前置：**市场有四类"零件"，但没有"你要的完整东西"**——本地·独立·可分发·轻量·格子视图·状态提示·可重跑·零 SaaS 依赖·密钥不入库 这个精确组合是空白。

### ① MCP 服务器目录 / 市场 —— 做了"装备目录 + 一键安装"
| 产品 | 形态 | 接近点 | 缺口 |
|------|------|--------|------|
| [mcp.so](https://mcp.so/) | 纯目录，19,700+ 服务器 | 最大"武器架" | 只列不装，要自己改 JSON |
| [Smithery](https://smithery.ai/servers) | registry + CLI 安装器 | `npx @smithery/cli install` 自动写进 Claude/Cursor 配置，**最接近"配装"** | 绑死特定客户端，依赖远程 registry |
| PulseMCP / Glama / MarketNow | 同类目录 | 浏览 / 分类 | 无安装器 |

参考：[MCP marketplaces compared (DEV)](https://dev.to/edison_flores_6d2cd381b13/mcp-server-marketplaces-compared-smithery-vs-glama-vs-pulsemcp-vs-marketnow-2e83)、[MCP Registry Guide 2026](https://dibi8.com/resources/llm-frameworks/mcp-server-registry-comprehensive-guide-2026/)

### ② 低代码 Agent 平台 —— 做了"可视化装工具"
- [Coze/扣子](https://www.coze.cn/)（字节）：拖拽式、插件市场、多 Agent 协作、零代码 → **最像"装备台 UI"**
- [Dify](https://dify.ai/)：最接近 Coze 的开源竞品；FastGPT / 腾讯元器 / 文心智能体同列

参考：CSDN《国内外与扣子智能体类似的软件》、火山引擎《Coze、Dify、n8n 怎么选》
- 缺口：是**重平台**（含大模型编排、发布、托管），不是轻量独立伴随工具。

### ③ Agent 工具集成层 —— 做了"装备库 + 使用许可(密钥)管理"
- [Composio](https://composio.dev/)（[GitHub](https://github.com/ComposioHQ/composio)）：1000+ toolkits，托管 OAuth，SDK-first，可自托管
- [Toolhouse](https://toolhouse.ai/)：1000+ MCP 集成，自然语言建 Agent
- Arcade：MCP-native runtime，scope-pinned token（合规向）

参考：[Composio vs Toolhouse](https://www.respan.ai/market-map/compare/composio-vs-toolhouse)、[Composio vs Arcade vs Pipedream](https://www.pkgpulse.com/guides/composio-vs-arcade-vs-pipedream-connect-ai-agent-tools-2026)
- 缺口：是**托管 SaaS / 云服务**，不是本地独立 CLI，密钥在它那边。

### ④ IDE 内置 MCP 面板 —— 做了"状态显示"
- Claude Desktop / Cursor / VS Code / CodeBuddy 的 MCP 设置页：列表式，可编辑/删，显示 available tools
- 用户痛点：**[跨客户端同步 MCP 配置很痛，每加一个要改多个 JSON](https://www.reddit.com/r/ClaudeAI/comments/1qlu977/managing_mcp_servers_across_cursor_claude_desktop/)** —— 正是独立配装器要解决的

参考：[Cursor MCP 管理建议](https://forum.cursor.com/t/mcp-install-config-and-management-suggestions/49283)
- 缺口：绑死 IDE、列表式非格子、改配置痛苦。

---

## 5. 差异化空白（为什么值得做）

把四类的"装备目录 / 可视化装配 / 密钥管理 / 状态显示"拆开，每个都有人做；但本仓库要做的**精确组合**——

> **本地 · 独立 · 可分发 · 轻量(CLI/TUI) · 格子视图 · 显示已装/未装/需密钥 · 可重跑变动 · 零 SaaS 依赖 · 密钥不入库**

——市场无对齐者：
- Smithery 的 CLI 安装器思路最近，但锁客户端 + 依赖远程 registry；
- Coze/Dify 有格子 UI，但是重平台；
- Composio/Toolhouse 管密钥，但是云服务；
- IDE 面板有状态，但绑 IDE 且列表式。

本方案契合仓库已有"可分发"理念，且与 `scripts/research_report.py`（同款独立 Python 脚本、零重依赖、密钥不入库）风格一致。

---

## 6. 实现落点（计划）

| 文件 | 作用 | 状态 |
|------|------|------|
| `docs/AGENT_LOADOUT_BOARD.md` | 本概念文档 + 竞品依据 | ✅ 草案 |
| `scripts/agent_loadout.py` | 独立 CLI/TUI 装备台（列格、选装、写配置、显状态） | ⬜ 待细节打磨后实现 |
| `scripts/loadout_catalog.example.toml` | 装备目录样例（无密钥，可分发） | ⬜ 待实现 |
| `scripts/loadout_catalog.toml` | 本地真实目录（含密钥，gitignore） | ⬜ 待实现 |

### 待打磨的细节（TODO）
- 一件"装备"在目录里要描述哪些字段（name / type / url-or-command / category / requires_key / deps）
- Agent 配置真实存在哪、格式如何（需先勘察仓库 agent 定义文件）
- 装/卸时是改 MCP 配置还是别的层
- 格子视图的终端渲染方式
- 是否提供"职业预设"（侦察兵 = Exa+Firecrawl 等）一键套用

---

## 7. 参考来源
- MCP 市场：mcp.so、Smithery、[DEV 对比](https://dev.to/edison_flores_6d2cd381b13/mcp-server-marketplaces-compared-smithery-vs-glama-vs-pulsemcp-vs-marketnow-2e83)、[dibi8 Registry Guide](https://dibi8.com/resources/llm-frameworks/mcp-server-registry-comprehensive-guide-2026/)
- 低代码平台：Coze、Dify、FastGPT、腾讯元器
- 工具集成层：Composio、Toolhouse、Arcade（[Respan](https://www.respan.ai/market-map/compare/composio-vs-toolhouse)、[PkgPulse](https://www.pkgpulse.com/guides/composio-vs-arcade-vs-pipedream-connect-ai-agent-tools-2026)）
- IDE 面板：Cursor / Claude Desktop / CodeBuddy MCP 设置页、[Reddit 痛点帖](https://www.reddit.com/r/ClaudeAI/comments/1qlu977/managing_mcp_servers_across_cursor_claude_desktop/)

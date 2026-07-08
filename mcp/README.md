# MCP Server 启用说明（Exa + Firecrawl）

> 让 Agent 获得**语义搜索（Exa）+ 干净抓取（Firecrawl）**能力。
> 配套配置见仓库根 `.mcp.json`（已用环境变量占位，未含真实密钥）。

## 前置

- 已安装 Node.js（能跑 `npx`）。
- 申请 Key（均有免费额度）：
  - Exa：`exa.ai` 注册 → `exa-...`
  - Firecrawl：`firecrawl.dev` 注册 → `fc-...`

## 方式一：本地 npx（使用仓库 `.mcp.json`）

`.mcp.json` 已声明两个 Server：

```json
{
  "mcpServers": {
    "exa":      { "command": "npx", "args": ["-y", "exa-mcp-server"], "env": { "EXA_API_KEY": "<YOUR_EXA_API_KEY>" } },
    "firecrawl":{ "command": "npx", "args": ["-y", "firecrawl-mcp"],   "env": { "FIRECRAWL_API_KEY": "<YOUR_FIRECRAWL_API_KEY>" } }
  }
}
```

填入 Key 的两种方式（任选）：

1. **直接替换占位符**：把 `<YOUR_EXA_API_KEY>` / `<YOUR_FIRECRAWL_API_KEY>` 改成真实 Key。
   - ⚠️ 仅限本地使用；**不要把这个含真实 Key 的版本提交/推送**（仓库为 public）。
2. **用环境变量注入**（推荐，保持 `.mcp.json` 干净）：
   - 在 shell / 客户端环境设置 `EXA_API_KEY` 与 `FIRECRAWL_API_KEY`，并把 `.mcp.json` 里的值改为 `${EXA_API_KEY}` / `${FIRECRAWL_API_KEY}`（支持环境变量展开的客户端会读取）。

客户端加载：把 `.mcp.json` 放到仓库根（已就位），或合并进客户端的 `mcpServers` 配置块（如 `~/.cursor/mcp.json`、Claude 的 `claude_desktop_config.json`、VS Code 的 MCP 设置）。**改完配置需重启客户端**以加载新 Server。

## 方式二：托管远程（免 npx）

- Exa 托管远程 MCP：`https://mcp.exa.ai/mcp`
  - 可追加工具过滤：`?tools=web_search_exa,web_search_advanced_exa,web_fetch_exa`
- Firecrawl 托管 / 官方 MCP：参考 `firecrawl/firecrawl` 仓库 "Power your agent" 章节。

## 验证

重启客户端后，确认 Agent 侧出现以下工具即成功：

- Exa：`web_search_exa`、`web_fetch_exa`（默认）；`web_search_advanced_exa`（按需开启）
- Firecrawl：搜索 / 抓取 / 爬取 / 提取等工具

## 安全基线

- 真实 Key **绝不入库、绝不硬编码**；`.mcp.json` 只保留占位或环境变量引用。
- 配置涉及外部网络请求，需用户明确批准后再启用。
- 工具接入后纳入 Agent 的防呆与密钥扫描范围（见 `AGENT_SEARCH_RESEARCH_ENHANCEMENT.md` 第 6 节）。

## 参考

- Exa MCP：github.com/exa-labs/exa-mcp-server
- Firecrawl MCP：`firecrawl-mcp`（npm）；Firecrawl 官方仓库 github.com/mendableai/firecrawl
- 选型与能力说明：`AGENT_SEARCH_RESEARCH_ENHANCEMENT.md`

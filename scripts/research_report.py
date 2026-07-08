#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
research_report.py — 自包含调研报告生成器（编排/综合层）

把 Exa（语义搜索）与 Firecrawl（净提取）两个 MCP 工具编排起来：
  多路查询 -> 并发检索 -> 去重合并 -> 带引用来源 -> 输出 Markdown 报告

设计目标（见 AGENT_SEARCH_RESEARCH_ENHANCEMENT.md §0/§3）：
  Firecrawl + Exa 作底层引擎，本脚本作轻量编排层，自动产出带引用的调研报告。

零重依赖：仅需要 httpx（pip install httpx）。不引入 mcp SDK，便于他人下载即用。
MCP 调用走 streamable-HTTP（SSE）协议，直接连配置里的 server URL，
因此 Exa 免 key、Firecrawl 用 URL 内嵌 key —— 与 Codex/CodeBuddy 的 MCP 配置完全一致。

用法：
  python scripts/research_report.py --topic "中小酒店 PMS 竞品对比" --limit 5
  python scripts/research_report.py --topic "..." --queries "q1;q2;q3" --output out.md
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

import httpx

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG = SCRIPT_DIR / "research_config.toml"
EXAMPLE_CONFIG = SCRIPT_DIR / "research_config.example.toml"


# ─────────────────────────────────────────────────────────────
# 最小 MCP-HTTP 客户端（streamable HTTP / SSE）
# ─────────────────────────────────────────────────────────────
class MCPHTTPClient:
    """极简 MCP streamable-HTTP 客户端，仅覆盖 initialize / tools/call。"""

    def __init__(self, url: str):
        self.url = url
        self.session_id: str | None = None
        self._id = 0
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "MCPHTTPClient":
        self.client = httpx.AsyncClient(timeout=60.0)
        await self.initialize()
        return self

    async def __aexit__(self, *exc) -> None:
        if self.client is not None:
            await self.client.aclose()

    async def _post(self, payload: dict) -> dict | None:
        assert self.client is not None
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        resp = await self.client.post(self.url, headers=headers, json=payload)
        sid = resp.headers.get("mcp-session-id") or resp.headers.get("Mcp-Session-Id")
        if sid:
            self.session_id = sid
        if resp.status_code == 202 or not resp.text.strip():
            return None
        ctype = resp.headers.get("content-type", "")
        if "text/event-stream" in ctype:
            msgs: list[dict] = []
            for line in resp.text.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    chunk = line[5:].strip()
                    if chunk:
                        try:
                            msgs.append(json.loads(chunk))
                        except json.JSONDecodeError:
                            pass
            rid = payload.get("id")
            for m in msgs:
                if m.get("id") == rid:
                    return m
            return msgs[-1] if msgs else None
        try:
            return resp.json()
        except json.JSONDecodeError:
            return None

    async def initialize(self) -> dict | None:
        self._id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "research-report", "version": "0.1"},
            },
        }
        result = await self._post(msg)
        # 初始化完成通知（部分服务端要求）
        await self._post(
            {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
        )
        return result

    async def call_tool(self, name: str, arguments: dict) -> str:
        self._id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        resp = await self._post(msg)
        if not resp:
            return ""
        result = resp.get("result", {})
        if result.get("isError"):
            text = "".join(c.get("text", "") for c in result.get("content", []))
            raise RuntimeError(f"tool {name} error: {text[:300]}")
        return "\n".join(
            c.get("text", "") for c in result.get("content", []) if c.get("type") == "text"
        )


# ─────────────────────────────────────────────────────────────
# 结果解析
# ─────────────────────────────────────────────────────────────
def parse_exa(text: str) -> list[dict]:
    items: list[dict] = []
    parts = re.split(r"(?m)^Title:\s*", text)
    for p in parts[1:]:
        lines = p.splitlines()
        title = lines[0].strip()
        url = None
        snippet: list[str] = []
        for ln in lines[1:]:
            if ln.startswith("URL:"):
                url = ln[4:].strip()
            elif ln.startswith(("Highlights:", "Published:", "Author:")):
                continue
            else:
                snippet.append(ln.strip())
        if url:
            items.append({"title": title, "url": url, "snippet": " ".join(snippet).strip()})
    return items


def parse_firecrawl(text: str) -> list[dict]:
    items: list[dict] = []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return items
    web = data.get("data", {}).get("web", []) if isinstance(data.get("data"), dict) else []
    for it in web:
        items.append(
            {
                "title": it.get("title", ""),
                "url": it.get("url", ""),
                "snippet": it.get("description", ""),
            }
        )
    return items


async def search_one(client: MCPHTTPClient, tool: str, query: str, limit: int) -> list[dict]:
    if tool == "exa":
        raw = await client.call_tool("web_search_exa", {"query": query, "numResults": limit})
        return parse_exa(raw)
    raw = await client.call_tool(
        "firecrawl_search",
        {"query": query, "limit": limit, "lang": "zh", "country": "cn",
         "sources": [{"type": "web"}]},
    )
    return parse_firecrawl(raw)


# ─────────────────────────────────────────────────────────────
# 大模型综合层（可选）
# ─────────────────────────────────────────────────────────────
async def synthesize_with_llm(llm: dict, topic: str, findings: str) -> str:
    prompt = (
        f"你是一名调研分析师。基于以下检索素材，撰写一份关于「{topic}」的结构化调研报告。\n"
        "要求：\n"
        "1. 使用 [n] 形式的来源引用编号穿插在正文里；\n"
        "2. 文末用「## 来源」列出编号-标题-URL 清单；\n"
        "3. 客观、带对比视角，不要编造素材中没有的信息。\n\n"
        f"检索素材：\n{findings}"
    )
    async with httpx.AsyncClient(timeout=180.0) as c:
        r = await c.post(
            llm["base_url"].rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {llm['api_key']}",
                     "Content-Type": "application/json"},
            json={"model": llm["model"],
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.3},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


# ─────────────────────────────────────────────────────────────
# 编排主流程
# ─────────────────────────────────────────────────────────────
def default_queries(topic: str) -> list[str]:
    dims = ["", " 功能对比", " 定价模式", " 2026 最新动态", " 竞品分析", " 渠道对接能力"]
    return [topic + d for d in dims]


def build_sources(results: dict) -> list[dict]:
    sources: list[dict] = []
    url2idx: dict[str, int] = {}
    for q, tools in results.items():
        for tool in ("exa", "firecrawl"):
            for it in tools[tool]:
                u = it["url"]
                if not u:
                    continue
                if u not in url2idx:
                    idx = len(sources) + 1
                    sources.append({"idx": idx, "title": it["title"], "url": u, "from": set()})
                    url2idx[u] = idx
                sources[url2idx[u] - 1]["from"].add(tool)
    return sources


def cite_md(item: dict, sources: list[dict]) -> str:
    for s in sources:
        if s["url"] == item["url"]:
            return f"[[{s['idx']}]]({s['url']})"
    return ""


def render_markdown(topic, queries, results, sources, narrative, cfg) -> str:
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    exa_url = cfg.get("exa", {}).get("url", "")
    fc_url = cfg.get("firecrawl", {}).get("url", "")
    # 掩码显示，避免泄露 key
    fc_masked = re.sub(r"/(fc-[0-9a-f]+)/", "/fc-****/", fc_url) if fc_url else ""

    md = [f"# 调研报告：{topic}\n"]
    md.append(f"- 生成时间：{today}")
    md.append(f"- 检索工具：Exa（语义搜索）+ Firecrawl（净提取）")
    md.append(f"- Exa 端点：`{exa_url}`")
    md.append(f"- Firecrawl 端点：`{fc_masked}`")
    md.append(f"- 查询数：{len(queries)} ｜ 去重来源数：{len(sources)}")
    md.append(f"- 综合层：{'大模型（{0}）'.format(cfg['llm']['model']) if cfg.get('llm') else '未启用（结构化简报）'}\n")

    if narrative:
        md.append("## 综合综述\n")
        md.append(narrative + "\n")

    md.append("## 分查询检索结果\n")
    for q in queries:
        tools = results.get(q, {"exa": [], "firecrawl": []})
        if not tools["exa"] and not tools["firecrawl"]:
            continue
        md.append(f"### 查询：{q}\n")
        for tool, label in (("exa", "Exa"), ("firecrawl", "Firecrawl")):
            items = tools[tool]
            if not items:
                continue
            md.append(f"**{label}**\n")
            for it in items:
                cite = cite_md(it, sources)
                title = it["title"] or "(无标题)"
                snip = (it.get("snippet") or "")[:200]
                md.append(f"- {cite} {title} — {it['url']}")
                if snip:
                    md.append(f"  - {snip}")
        md.append("")

    md.append("## 来源清单\n")
    for s in sources:
        md.append(f"{s['idx']}. [{s['title'] or '来源'}]({s['url']})  _(来自：{', '.join(sorted(s['from']))})_")
    md.append("")
    return "\n".join(md)


async def research(topic, queries, limit, cfg, use_llm: bool) -> str:
    results: dict[str, dict] = {}
    exa_url = cfg["exa"]["url"]
    fc_url = cfg["firecrawl"]["url"]

    async with MCPHTTPClient(exa_url) as exa, MCPHTTPClient(fc_url) as fc:
        tasks = []
        meta = []
        for q in queries:
            tasks.append(search_one(exa, "exa", q, limit))
            meta.append(("exa", q))
            tasks.append(search_one(fc, "firecrawl", q, limit))
            meta.append(("firecrawl", q))
        done = await asyncio.gather(*tasks, return_exceptions=True)
        for (tool, q), res in zip(meta, done):
            results.setdefault(q, {"exa": [], "firecrawl": []})
            if isinstance(res, Exception):
                print(f"[warn] {tool} 查询 {q!r} 失败：{res}", file=sys.stderr)
                results[q][tool] = []
            else:
                results[q][tool] = res

    sources = build_sources(results)
    narrative = ""
    if use_llm and cfg.get("llm"):
        findings = render_markdown(topic, queries, results, sources, "", cfg)
        try:
            narrative = await synthesize_with_llm(cfg["llm"], topic, findings)
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 大模型综合失败，回退到结构化简报：{e}", file=sys.stderr)

    return render_markdown(topic, queries, results, sources, narrative, cfg)


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────
def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(
            f"找不到配置文件 {path}\n"
            f"请复制 {EXAMPLE_CONFIG.name} 为 research_config.toml 并填入你的端点。\n"
            f"（research_config.toml 已被 .gitignore 忽略，不会进版本库）"
        )
    with open(path, "rb") as f:
        return tomllib.load(f)


def main() -> None:
    ap = argparse.ArgumentParser(description="Exa + Firecrawl 调研报告生成器")
    ap.add_argument("--topic", required=True, help="调研主题")
    ap.add_argument("--queries", help="自定义查询，用分号分隔；不填则按主题自动派生多维度查询")
    ap.add_argument("--limit", type=int, default=5, help="每个查询每工具返回条数")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG), help="配置文件路径")
    ap.add_argument("--output", help="输出 Markdown 路径（默认写到 docs/）")
    ap.add_argument("--no-llm", action="store_true", help="即便配置了 [llm] 也强制不使用大模型")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    if "exa" not in cfg or "firecrawl" not in cfg:
        sys.exit("配置缺少 [exa] 或 [firecrawl] 的 url")
    use_llm = (not args.no_llm) and bool(cfg.get("llm"))

    if args.queries:
        queries = [q.strip() for q in args.queries.split(";") if q.strip()]
    else:
        queries = default_queries(args.topic)

    print(f"[info] 主题：{args.topic}｜查询 {len(queries)} 条｜每工具上限 {args.limit}｜LLM：{'开' if use_llm else '关'}")
    report = asyncio.run(research(args.topic, queries, args.limit, cfg, use_llm))

    if args.output:
        out = Path(args.output)
    else:
        out_dir = REPO_ROOT / cfg.get("report", {}).get("output_dir", "docs")
        out_dir.mkdir(exist_ok=True)
        slug = re.sub(r"[^\w一-龥]+", "_", args.topic)[:40]
        stamp = datetime.now().strftime("%Y%m%d")
        out = out_dir / f"research_{slug}_{stamp}.md"
    out.write_text(report, encoding="utf-8")
    print(f"[done] 报告已写出：{out}（{len(report)} 字符）")


if __name__ == "__main__":
    main()

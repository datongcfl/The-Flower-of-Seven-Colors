#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 装备台 (Loadout Board) —— 独立、可分发、零重依赖。

给任意 Agent 上"装备"（MCP server）：每新装一个 Agent 跑一次 `init`，
按需 `equip`/`unequip`，`apply` 生成标准 mcp.json。`list` 用格子视图显示
已装/未装/缺密钥状态。

设计（详见 docs/AGENT_LOADOUT_BOARD.md）：
- 武器架 = loadout_catalog.toml（全局可用装备；样例见 .example.toml）
- 装备栏 = agent_loadouts/<agent>.loadout.toml（每个 Agent 选装了哪些）
- 密钥   = loadout_secrets.toml（本地真实，不入库）
- 产物   = agent_loadouts/<agent>.mcp.json（标准 MCP 配置，交给任意 MCP 客户端）

仅依赖 Python 标准库（tomllib 读；toml 写为手写，避免引入第三方）。
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
CATALOG = SCRIPTS / "loadout_catalog.toml"
CATALOG_EXAMPLE = SCRIPTS / "loadout_catalog.example.toml"
SECRETS = SCRIPTS / "loadout_secrets.toml"
LOADOUT_DIR = SCRIPTS / "agent_loadouts"

GREEN = "\033[32m"
YELLOW = "\033[33m"
DIM = "\033[2m"
RESET = "\033[0m"


def _c(text, color):
    return f"{color}{text}{RESET}"


def load_catalog():
    p = CATALOG if CATALOG.exists() else CATALOG_EXAMPLE
    if not p.exists():
        print("找不到装备目录 loadout_catalog.toml / .example.toml", file=sys.stderr)
        sys.exit(1)
    with open(p, "rb") as f:
        return tomllib.load(f)


def load_secrets():
    if SECRETS.exists():
        with open(SECRETS, "rb") as f:
            return tomllib.load(f)
    return {}


def loadout_path(agent):
    return LOADOUT_DIR / f"{agent}.loadout.toml"


def load_loadout(agent):
    p = loadout_path(agent)
    if p.exists():
        with open(p, "rb") as f:
            return tomllib.load(f)
    return {"agent": agent, "equip": []}


def save_loadout(agent, data):
    LOADOUT_DIR.mkdir(parents=True, exist_ok=True)
    p = loadout_path(agent)
    lines = [f'agent = "{data.get("agent", agent)}"', "equip = ["]
    for e in data.get("equip", []):
        lines.append(f'  "{e}",')
    lines.append("]")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def equipped_set(agent):
    return set(load_loadout(agent).get("equip", []))


def state_of(catalog, secrets, cid, equipped):
    c = catalog.get(cid, {})
    if cid not in equipped:
        return "未装", DIM
    if c.get("requires_key") and not secrets.get(cid, {}).get("key"):
        return "需密钥", YELLOW
    return "已连", GREEN


def cmd_init(agent):
    p = save_loadout(agent, {"agent": agent, "equip": []})
    print(f"已初始化装备栏: {p}")


def cmd_list(agent):
    cat = load_catalog()
    sec = load_secrets()
    eq = equipped_set(agent)
    groups = {}
    for cid, c in cat.items():
        groups.setdefault(c.get("category", "其他"), []).append(cid)
    print(f"\n装备台 · Agent = {agent}  (已装 {len(eq)}/{len(cat)})")
    for cat_name in sorted(groups):
        print(f"\n{DIM}== {cat_name} =={RESET}")
        for cid in sorted(groups[cat_name]):
            c = cat[cid]
            state, color = state_of(cat, sec, cid, eq)
            mark = "[x]" if cid in eq else "[ ]"
            label = f"{mark} {cid:<12} {c.get('name',''):<18} [{_c(state, color)}]"
            print("  " + label)
            if c.get("desc"):
                print(f"      {DIM}{c['desc']}{RESET}")
    missing = eq - set(cat)
    if missing:
        print(f"\n{DIM}注意：装备栏引用了目录中不存在的 id: {missing}{RESET}")


def cmd_equip(agent, ids):
    cat = load_catalog()
    eq = equipped_set(agent)
    for i in ids:
        if i not in cat:
            print(f"! 未知装备，跳过: {i}")
            continue
        eq.add(i)
    data = load_loadout(agent)
    data["equip"] = sorted(eq)
    p = save_loadout(agent, data)
    print(f"已更新 {agent} 装备栏: {data['equip']}  ({p})")


def cmd_unequip(agent, ids):
    eq = equipped_set(agent)
    eq -= set(ids)
    data = load_loadout(agent)
    data["equip"] = sorted(eq)
    p = save_loadout(agent, data)
    print(f"已卸下 {ids}，当前 {agent} 装备栏: {data['equip']}  ({p})")


def cmd_apply(agent):
    cat = load_catalog()
    sec = load_secrets()
    lo = load_loadout(agent)
    servers = {}
    skipped = []
    for cid in lo.get("equip", []):
        c = cat.get(cid)
        if not c:
            skipped.append(cid)
            continue
        url = c.get("url", "")
        if c.get("requires_key"):
            key = sec.get(cid, {}).get("key")
            if not key:
                skipped.append(f"{cid}(缺密钥)")
                continue
            url = url.replace(c.get("key_placeholder", "{KEY}"), key)
        servers[cid] = {"type": c.get("type", "http"), "url": url}
    out = {"mcpServers": servers}
    LOADOUT_DIR.mkdir(parents=True, exist_ok=True)
    p = LOADOUT_DIR / f"{agent}.mcp.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 {p}  ({len(servers)} 个 server；跳过 {skipped or '无'})")
    print("把它交给任意 MCP 客户端（如 CodeBuddy 的 mcp.json）即可生效。")


def main():
    ap = argparse.ArgumentParser(description="Agent 装备台 (Loadout Board)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("init", help="初始化 Agent 空装备栏").add_argument("agent")
    sub.add_parser("list", help="格子视图显示装备状态").add_argument("agent")
    pe = sub.add_parser("equip", help="给 Agent 装装备")
    pe.add_argument("agent")
    pe.add_argument("ids", nargs="+")
    pu = sub.add_parser("unequip", help="卸下 Agent 装备")
    pu.add_argument("agent")
    pu.add_argument("ids", nargs="+")
    sub.add_parser("apply", help="根据装备栏生成标准 mcp.json").add_argument("agent")
    args = ap.parse_args()
    if args.cmd == "init":
        cmd_init(args.agent)
    elif args.cmd == "list":
        cmd_list(args.agent)
    elif args.cmd == "equip":
        cmd_equip(args.agent, args.ids)
    elif args.cmd == "unequip":
        cmd_unequip(args.agent, args.ids)
    elif args.cmd == "apply":
        cmd_apply(args.agent)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()

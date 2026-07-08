---
title: Agent LLM 优化（LiteLLM + DSPy + OpenAI Cookbook）
version: 0.1
updated: 2026-07-08
status: active
---

# Agent LLM 优化（LiteLLM + DSPy + OpenAI Cookbook）

> 让 Agent 更稳、更省、更聪明：三层能力组合。
> 本文档脱敏，不含本地路径 / 服务器地址 / 内部代号。

Agent 的「提效」不只是接个搜索。模型层本身有三件常被忽略的事：

1. **接得稳、接得省** —— 多模型统一接入、故障转移、成本控制（LiteLLM）
2. **提示能自优化** —— 把脆弱的提示词变成可由算法调优的对象（DSPy）
3. **有现成范例** —— 不重复造轮子，先抄对的（OpenAI Cookbook）

三者串起来是一条可落地的流水线：**Cookbook 验证任务 → LiteLLM 统一接入与保活 → DSPy 自动优化提示**。

---

## 1. LiteLLM —— 统一 AI 网关

- **是什么**：开源 AI 网关（v1.91.0），为 100+ LLM 提供商提供**单一 OpenAI 格式接口**。
  既能当 Python SDK 内嵌，也能部署成团队级 Proxy Server。
- **许可证**：开源版 + 商业版（企业特性）。

### 关键能力

| 能力 | 说明 | Agent 收益 |
|---|---|---|
| 统一 API | 一个接口调 100+ 模型，OpenAI 格式 drop-in 替换 | 供应商无关，不绑定单一厂商 |
| Router 回退 (Fallback) | 跨部署重试 / 转移（如 Azure↔OpenAI） | 限流 / 故障时自动切换，保活 |
| 负载均衡 | 应用层 / 网关层开箱即用 | 高并发稳吞吐 |
| 成本追踪 | 虚拟密钥、按项目/用户 spend tracking | 限制额度，防意外开销 |
| 缓存 | 相同 prompt 命中缓存 | 多轮对话 / 工具调用加速 |
| MCP 桥接 | `/mcp/` 端点把 MCP 工具桥接到任意 LLM | Agent 工具可插拔扩展 |
| A2A | 注册/调用分布式 Agent（LangGraph 等） | 多 Agent 编排 |

### 安装与最小用法

```bash
# Python SDK
uv add litellm
# 代理（团队网关）
uv tool install 'litellm[proxy]'
litellm --model gpt-4o
```

```python
import openai
client = openai.OpenAI(api_key="anything", base_url="http://0.0.0.0:4000")
resp = client.chat.completions.create(
    model="gpt-4o", messages=[{"role": "user", "content": "Hello!"}]
)
```

### 在 Agent 中的实践要点

- 代码用 OpenAI 格式，底层透明切 GPT-4o / Claude / Gemini。
- 给关键 Agent 路径配 Router fallback + 预算上限（虚拟密钥）。
- 重复检索 / 多轮工具调用开启缓存，显著降延迟与成本。
- 通过 MCP 网关把外部工具（GitHub 等）暴露给 Agent。

---

## 2. DSPy —— 编程，而非提示

- **是什么**：Stanford NLP 出品的框架（v3.2.1），理念是 **Programming—not prompting**（声明式自改进 Python）。
- **许可证**：开源（详见仓库）。

### 核心概念

| 概念 | 作用 |
|---|---|
| **Signature（签名）** | 声明「输入→输出」的期望，不写死提示词 |
| **Module（模块）** | 可组合的代码块，拼成管线 / Agent loop |
| **Teleprompter / Optimizer（优化器）** | 自动调指令与示范（如 BootstrapFewShot、GEPA 反射式进化） |
| **Metric（指标）** | 定义「什么叫好」，驱动优化方向 |

### 为什么能优化提示

- 手工提示词脆弱（brittle）；DSPy 用组合式 Python 取代，把提示变成**可优化对象**。
- 通过优化器把声明式 LM 调用**编译为自改进管线**，自动调指令与示范。
- 明确支持 **Agent loops**，避免硬编码提示。

### 安装与最小用法

```bash
pip install dspy
```

```python
import dspy

# 1) 声明签名：不写提示词，只声明输入输出
class QA(dspy.Signature):
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

# 2) 用模块 + 优化器（teleprompter）自动调优
qa = dspy.Predict(QA)
# dspy.BootstrapFewShot(metric=...) 在带标注数据上优化
```

---

## 3. OpenAI Cookbook —— 范例驱动

- **是什么**：OpenAI 官方的示例与指南仓库（MIT），"Example code and guides for accomplishing common tasks with the OpenAI API."
- 内容以 Python Notebook 为主（约 93%），概念可迁移到任意语言。

### 价值

- 提示工程、微调、批量调用（降成本）、评测循环等**即用范例**。
- 把「某任务怎么做」从零摸索变成「先抄对的」。
- 与 LiteLLM / DSPy 互补：

```
Cookbook（原型验证：这个任务怎么做）
   ↓ 用 OpenAI 兼容接口转发
LiteLLM（多模型统一接入 + 保活 + 控本）
   ↓ 把提示词结构化
DSPy（自动优化提示 / 权重）
```

---

## 4. 三者组合流水线（推荐落地顺序）

1. **先用 Cookbook 验证任务可行性**：找最接近示例，跑通最小可用链路。
2. **用 LiteLLM 统一接入 + 保活**：把底层模型换成可切换 / 可回退的统一接口，加预算与缓存。
3. **用 DSPy 程序化优化**：把定好的 Signature/Module 交给优化器，用指标驱动自动调提示。
4. **闭环**：评测结果回流为 DSPy 的 metric / 训练数据，持续自改进。

> 经验法则：Cookbook 解决「能不能做」，LiteLLM 解决「稳不稳/贵不贵」，DSPy 解决「好不好」。

---

## 5. 脱敏与合规

- 本文档不出现本地路径 / 服务器地址 / 内部代号。
- 第三方工具各自带 LICENSE；引用时保留出处，不重新分发其源码。
- API Key 一律走环境变量（`EXA_API_KEY`、`FIRECRAWL_API_KEY` 等），不落库。

## 参考

- LiteLLM: github.com/BerriAI/litellm
- DSPy: github.com/stanfordnlp/dspy
- OpenAI Cookbook: github.com/openai/openai-cookbook
- 搜索 / 抓取增强（含 MCP 配置）: 见 `AGENT_SEARCH_RESEARCH_ENHANCEMENT.md` 与仓库根 `.mcp.json`

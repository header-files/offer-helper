# Agent / LLM 文档

## 规划技术

- LangChain：模型与工具抽象
- LangGraph：多轮对话与工作流编排（业务 Graph 后续阶段）
- ChatDeepSeek：DeepSeek 官方客户端（保留 `reasoning_content`）
- ChatOpenAI：其他 OpenAI 兼容模型客户端

## 多模型配置（配置与代码分离）

在 `config/*.yaml` 的 `llm.models` 下声明任意数量模型；**新增模型只需改 YAML + 环境变量，无需改代码**。

```yaml
llm:
  default: chat
  models:
    chat:
      model: deepseek-v4-flash
      base_url: https://api.deepseek.com
      provider: deepseek   # auto | openai | deepseek；默认 auto
      temperature: 0.7
      timeout: 60
      max_retries: 2
      extra_body:
        thinking:
          type: disabled
    openai_chat:
      model: gpt-4o-mini
      base_url: https://api.openai.com/v1
      provider: openai
      temperature: 0.7
      timeout: 60
```

客户端选择规则：

- `provider: deepseek` → `ChatDeepSeek`
- `provider: openai` → `ChatOpenAI`
- `provider: auto`（默认）→ `model` 或 `base_url` 含 `deepseek` 则用 `ChatDeepSeek`，否则 `ChatOpenAI`

`model` / `base_url` / `provider` 为基础设施字段；其余键会原样传给对应客户端构造函数。

密钥与可选覆盖（`.env`，勿提交真实 Secret）：

```bash
LLM_CHAT_API_KEY=sk-xxx
LLM_REASONER_API_KEY=sk-yyy
# 可选覆盖 YAML 中的 base_url
# LLM_CHAT_BASE_URL=https://custom.example.com/v1
```

命名约定：模型名 `my-model` → `LLM_MY_MODEL_API_KEY` / `LLM_MY_MODEL_BASE_URL`。

## 代码用法

```python
from app.infrastructure.llm import get_chat_model, list_llm_models

list_llm_models()          # ['chat', 'reasoner', ...]
llm = get_chat_model()     # 默认模型
llm = get_chat_model("reasoner")

msg = llm.invoke("你是谁")
print(msg.content)
print(msg.additional_kwargs.get("reasoning_content"))  # DeepSeek 推理内容
```

禁止业务代码直接 `ChatOpenAI(...)` / `ChatDeepSeek(...)` 或 `os.getenv("LLM_...")`。

## 目录

```text
app/infrastructure/llm/   # 聊天模型工厂
app/agents/               # Graph / Node / Tool（后续）
```

# Agent 文档（Phase 0）

## 规划技术

- LangChain：模型与工具抽象
- LangGraph：多轮对话与工作流编排

## 目录

```text
app/agents/     # Graph / Node / Tool 定义（后续）
```

## 规范摘要

- Secret 只来自 Settings
- Agent 不直接拼接裸 SQL
- 必须绑定用户与会话作用域
- 输出可测试

## Phase 0

仅保留包结构与依赖声明，**不实现**任何 Agent / Graph / LLM 调用业务。

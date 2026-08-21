# Memory 文档（Phase 0）

## 目标（后续阶段）

- 长期用户画像
- Markdown Memory
- 与多轮对话、职业规划联动

## 目录

```text
app/memory/
```

## 规范摘要

- 读写必须带 `user_id`
- 记录来源会话与时间戳
- 与 Agent 状态分离存储边界清晰

## Phase 0

仅保留包结构，**不实现** Memory 存储或检索。

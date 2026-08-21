# Memory 文档

**当前阶段：Phase 2**（Memory 业务实现待指令明确）。

## 目标

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

## 现状

Phase 0–1 仅保留包结构，**尚未实现** Memory 存储或检索。Phase 2 起按开发指令落地。

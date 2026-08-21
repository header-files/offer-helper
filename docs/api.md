# API 文档

Base URL（本地 / Compose）：`http://localhost:8000`

**当前阶段：Phase 2**。业务路由将在 `api_prefix`（默认 `/api/v1`）下扩展。

## GET /health

存活探测（Phase 0 起提供，持续保留）。

### Response `200`

```json
{
  "status": "ok"
}
```

### 说明

- 无鉴权
- 不依赖数据库 / Redis（轻量探针）
- 用于 Docker healthcheck 与编排探针

## 后续（Phase 2+）

业务 API（用户、会话、简历、面试等）在接到明确指令后于 `/api/v1` 下增加；须遵守 `user_id` 隔离与分层规范。

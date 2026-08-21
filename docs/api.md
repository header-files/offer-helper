# API 文档（Phase 0）

Base URL（本地 / Compose）：`http://localhost:8000`

## GET /health

存活探测。

### Response `200`

```json
{
  "status": "ok"
}
```

### 说明

- 无鉴权
- 不依赖数据库 / Redis（Phase 0）
- 用于 Docker healthcheck 与编排探针

后续阶段将在 `api_prefix`（默认 `/api/v1`）下扩展业务路由。

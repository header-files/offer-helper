# 架构文档（Phase 0）

## 目标

`offer-helper` 是多用户 AI 求职助手后端。Phase 0 只建立可运行、可测试、可部署的工程骨架。

## 逻辑分层

```text
api/routers          HTTP 路由与依赖注入入口
services             业务用例（后续）
repositories         数据访问（后续）
models / schemas     持久化模型与 API Schema
agents / memory      Agent 与 Memory（后续）
infrastructure       database / redis / llm / storage
core                 config / logging / security / exceptions
```

## 运行时拓扑

```text
Client → app(FastAPI) → postgres / redis
                     ↘ LLM Provider（后续，经 Settings）
```

Docker Compose 中应用通过服务名访问基础设施：

- PostgreSQL：`postgres:5432`
- Redis：`redis:6379`

## 配置流

1. 读取 `APP_ENV`
2. 合并 `config/base.yaml` + `config/{env}.yaml`
3. 用环境变量注入 Secret
4. 经 `get_settings()` 提供给全应用

## Phase 0 已交付

- FastAPI 应用工厂 `create_app()`
- `GET /health` → `{"status":"ok"}`
- Settings / YAML / `.env.example`
- Docker 三件套与 healthcheck
- pytest / ruff / mypy 基线

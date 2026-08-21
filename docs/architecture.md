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

## Phase 1（进行中）：Redis + Logging + PostgreSQL

`app/infrastructure/redis` 提供统一客户端：

- 连接池（`ConnectionPool` / Sentinel pool / Cluster per-node pool）
- 单机：`redis://` / `rediss://`
- Sentinel：`sentinel://[:password@]mymaster?sentinels=host:26379,...`
- Cluster：`cluster://[:password@]host:6379?nodes=host2:6379,...`
- 并发限制（Semaphore）与命令超时（`asyncio.wait_for`）
- 应用启动时 `init_redis()`，关闭时 `shutdown_redis()`
- 业务代码通过 `get_redis_client()` 访问，禁止自行 `Redis.from_url()`

`app/core/logging` + `TraceIdMiddleware`：

- 每条 HTTP 请求绑定 `trace_id`（可透传 `X-Trace-Id` / `X-Request-Id`）
- 响应回写 `X-Trace-Id`
- 日志格式包含 `trace_id`，贯穿整条处理链路
- YAML 可开关控制台 / 本地文件；文件使用 `RotatingFileHandler`（`max_bytes` + `backup_count`）

`app/infrastructure/database`：

- SQLAlchemy 2.x `AsyncEngine` + 连接池（`pool_size` / `max_overflow` / `pool_pre_ping`）
- `AsyncSession` 工厂、`session_scope()`、FastAPI 依赖 `get_db_session`
- 开发默认连接本机 PostgreSQL（`localhost:5432`）；Compose 内使用服务名 `postgres`
- 应用启动 `init_db()`，关闭 `shutdown_db()`

`app/infrastructure/llm`：

- 多模型工厂 `get_chat_model(name)`：DeepSeek → `ChatDeepSeek`，其他 → `ChatOpenAI`
- 模型清单在 YAML `llm.models`；密钥按 `LLM_<NAME>_API_KEY` 注入
- 新增大模型只需改配置 / 环境变量，不改代码

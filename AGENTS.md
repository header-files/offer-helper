# AGENTS.md — offer-helper 协作与工程规范

本文档约束所有在本仓库工作的人类与 AI Agent。当前阶段为 **Phase 1（Redis + Logging + PostgreSQL + LLM 基础设施）**。

## 1. 架构规范

- 分层清晰，禁止跨层乱引用：
  - `api` → `services` → `repositories` → `models` / `infrastructure`
  - `schemas` 负责 API 入出参；`models` 负责持久化实体
  - `agents` 仅通过 `services` / `infrastructure.llm` 交互，不直连数据库细节
- 多用户系统：所有用户数据访问必须带 `user_id` 隔离条件（后续阶段强制）
- Phase 0 禁止实现：User / Resume / Job / Interview / Memory / LangGraph 业务 / LLM Agent 业务

## 2. 代码规范

- Python 3.12+，类型注解完整，优先现代 typing
- 公共 API、配置、领域边界使用 Pydantic 模型
- 禁止业务代码直接调用 `os.getenv()` / `os.environ[...]`，统一经 `app.core.config.get_settings()`
- 异常放在 `app.core.exceptions`，日志经 `app.core.logging`
- 保持函数短小、模块单一职责；不做无关重构
- 通过 Ruff / Mypy 后方可合入

## 3. 测试规范

- 框架：`pytest` + `pytest-asyncio`（`asyncio_mode = auto`）
- 目录：
  - `tests/unit/`：纯逻辑
  - `tests/integration/`：基础设施集成
  - `tests/api/`：HTTP 契约
  - `tests/agents/`：Agent 行为（后续）
- 每个可观察行为至少有一条测试；Phase 0 必须覆盖 `GET /health`
- 运行：`uv run pytest`

## 4. Git 规范

- 主分支：`main`
- 当前开发分支：`feature/phase-1-redis`
- Commit 信息简洁说明「为什么」
- 禁止提交：`.env`、真实 API Key、数据库密码、其它 Secret
- 必须纳入版本控制：`pyproject.toml`、`uv.lock`、`Dockerfile`、`docker-compose.yml`、`.env.example`、`AGENTS.md`、`README.md`、`docs/`

## 5. uv 规范

- 唯一正式依赖管理工具：`uv`
- 必须存在：`pyproject.toml`、`uv.lock`
- 禁止使用 `requirements.txt` 作为正式依赖源
- 常用命令：
  - `uv add` / `uv add --dev`
  - `uv sync`
  - `uv lock`
  - `uv run <cmd>`
  - `uv run pytest`

## 6. Docker 规范

- 必须提供 `Dockerfile` 与 `docker-compose.yml`
- Compose 服务至少包含：`app`、`postgres`、`redis`
- 镜像版本锁定：`postgres:18.6`、`redis:8.0.2`
- 数据卷：`postgres_data`、`redis_data`
- 使用自定义 Docker Network；应用内主机名必须是 `postgres` / `redis`，禁止写 `localhost` 作为容器间地址
- 服务必须配置 `healthcheck`
- 校验：`docker compose config`；启动：`docker compose up -d`

## 7. 多用户隔离规范

- 后续所有会话、Memory、简历、面试记录必须以 `user_id` 为隔离键
- Repository / Service 层禁止提供「无用户上下文」的越权查询 API
- Agent 状态与 Memory 读写必须绑定用户与会话作用域
- Phase 0 仅预留结构，不实现用户域模型

## 8. Agent 规范

- Agent 编排基于 LangGraph；工具与模型访问经 `infrastructure/llm`
- Agent 输出需可观测、可测试；禁止在 Agent 内硬编码 Secret
- Prompt / Graph 定义与业务 Service 分离
- Phase 0 仅保留 `app/agents/` 包结构，不实现业务 Graph

## 9. Memory 规范

- Memory 支持长期用户画像与 Markdown Memory（后续）
- Memory 写入必须可追溯（来源会话、时间、用户）
- 检索与写入均需用户隔离
- Phase 0 仅保留 `app/memory/` 包结构

## 10. 配置规范

- 非 Secret 配置：`config/base.yaml` + `config/{dev,test,prod}.yaml`
- Secret 仅通过环境变量注入（见 `.env.example`）：
  - `DATABASE_URL`
  - `REDIS_URL`（单机 `redis://`、Sentinel `sentinel://`、Cluster `cluster://`）
  - `LLM_<MODEL>_API_KEY`（例如 `LLM_CHAT_API_KEY`；与 YAML `llm.models` 名称对应）
- 统一入口：`Settings` / `get_settings()`
- 配置与代码分离；环境差异用 YAML 覆盖，密钥永不入库

## Phase 边界

当前阶段为 **Phase 1（基础设施）**：Redis + Logging + PostgreSQL + 多模型 LLM。

完成当前指令后停止，等待下一指令。不得擅自扩展 User / Resume / Job / Interview / Memory / LangGraph 业务。

# offer-helper

生产级 AI 求职助手后端。

**当前阶段：Phase 2**（Phase 0 / Phase 1 已完成）。

## 阶段进度

| 阶段 | 状态 | 内容 |
|------|------|------|
| Phase 0 | 已完成 | 工程引导：项目骨架、Docker、配置、`GET /health`、pytest / Ruff / Mypy |
| Phase 1 | 已完成 | 基础组件：Redis、Logging（trace_id）、PostgreSQL、多模型 LLM |
| Phase 2 | 进行中 | 业务基础（具体范围见后续开发指令） |

## 功能愿景

- 多用户、多轮对话
- 长期用户画像与 Markdown Memory
- 简历生成与优化
- 面试分析
- 职业规划

## 技术栈

| 类别 | 选型 |
|------|------|
| 语言 | Python 3.12+ |
| Web | FastAPI / Pydantic / Pydantic Settings |
| 数据 | SQLAlchemy 2.x / asyncpg / PostgreSQL 18.6 / Alembic |
| 缓存 | Redis 8.0.2 |
| Agent | LangChain / LangGraph（业务 Graph 待 Phase 2+） |
| 包管理 | uv |
| 质量 | pytest / pytest-asyncio / Ruff / Mypy |
| 运行 | Docker / Docker Compose |

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 环境变量

```bash
cp .env.example .env
```

不要将真实 Secret 写入仓库。业务代码必须通过 `get_settings()` 读取配置，禁止直接 `os.getenv()`。

### 3. 本地运行（不含基础设施）

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

### 4. Docker Compose

```bash
cp .env.example .env
docker compose up -d --build
```

服务：

- `app` → http://localhost:8000
- `postgres`（hostname：`postgres`）
- `redis`（hostname：`redis`）

### 5. 测试与静态检查

```bash
uv run pytest
uv run ruff check .
uv run mypy .
```

## 目录结构

```text
app/                 # 应用代码
config/              # YAML 配置（非 Secret）
migrations/          # Alembic 迁移（业务迁移随 Phase 2+）
tests/               # unit / integration / api / agents
docs/                # 架构与规范文档
```

更多规范见 [AGENTS.md](AGENTS.md) 与 [docs/](docs/)。

## 许可

见 [LICENSE](LICENSE)。

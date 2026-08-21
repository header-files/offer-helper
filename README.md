# offer-helper

生产级 AI 求职助手后端（Phase 0：工程引导）。

## 功能愿景（后续阶段）

- 多用户、多轮对话
- 长期用户画像与 Markdown Memory
- 简历生成与优化
- 面试分析
- 职业规划

Phase 0 **仅**完成：项目初始化、工程结构、Docker、配置、FastAPI `/health`、测试与质量工具、Git。

## 技术栈

| 类别 | 选型 |
|------|------|
| 语言 | Python 3.12+ |
| Web | FastAPI / Pydantic / Pydantic Settings |
| 数据 | SQLAlchemy 2.x / asyncpg / PostgreSQL 18.6 / Alembic |
| 缓存 | Redis 8.0.2 |
| Agent | LangChain / LangGraph（Phase 0 未启用业务实现） |
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
migrations/          # Alembic 迁移（后续阶段）
tests/               # unit / integration / api / agents
docs/                # 架构与规范文档
```

更多规范见 [AGENTS.md](AGENTS.md) 与 [docs/](docs/)。

## 许可

见 [LICENSE](LICENSE)。

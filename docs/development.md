# 开发文档

## 前置

- Python 3.12+
- uv
- Docker / Docker Compose
- Git

## 初始化

```bash
# Phase 2 按任务新建分支，例如：
# git checkout -b feature/phase-2-<topic>
uv sync
cp .env.example .env
```

## 日常命令

```bash
# 依赖
uv add <package>
uv add --dev <package>
uv sync
uv lock

# 运行
uv run uvicorn app.main:app --reload

# 质量门禁
uv run pytest
uv run ruff check .
uv run mypy .
```

## 配置

- YAML：`config/base.yaml`、`dev.yaml`、`test.yaml`、`prod.yaml`
- Secret：`.env`（由 `.env.example` 复制，勿提交）
- 读取：`from app.core.config import get_settings`
- Redis：业务代码使用 `from app.infrastructure.redis import get_redis_client`
- PostgreSQL：业务代码使用 `from app.infrastructure.database import session_scope` 或依赖注入 `get_db_session`
- 日志：业务代码使用 `from app.core.logging import get_logger, get_trace_id`

本地已部署 Redis / PostgreSQL：

```bash
# host 进程 / pytest
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb

# Docker Compose 内（compose 会强制覆盖为服务名）
REDIS_URL=redis://redis:6379/0
DATABASE_URL=postgresql+asyncpg://offer:offer@postgres:5432/offer_helper
```

其它拓扑：

```text
sentinel://:password@mymaster?sentinels=host1:26379,host2:26379
cluster://:password@host:6379?nodes=host2:6379,host3:6379
```

日志配置示例（`config/*.yaml`）：

```yaml
logging:
  level: INFO
  console:
    enabled: true
  file:
    enabled: true
    path: logs/offer-helper.log
    max_bytes: 10485760   # 单文件上限（字节）
    backup_count: 5       # 滚动保留份数
```

LLM 多模型（新增模型只改 YAML + `.env`，不改代码）：

```yaml
llm:
  default: chat
  models:
    chat:
      model: gpt-4o-mini
      base_url: https://api.openai.com/v1
      temperature: 0.7
```

```bash
LLM_CHAT_API_KEY=sk-xxx
# LLM_CHAT_BASE_URL=https://optional-override/v1
```

```python
from app.infrastructure.llm import get_chat_model
llm = get_chat_model("chat")
```

## 分支

- `main`：稳定主干
- `feature/phase-1-infrastructure`：Phase 1（基础组件，已完成）
- `feature/phase-2-*`：Phase 2（进行中，按任务开分支）

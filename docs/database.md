# 数据库文档

## 引擎

- PostgreSQL **18.6**
- 异步驱动：`asyncpg`
- ORM：SQLAlchemy 2.x（`AsyncEngine` + `AsyncSession`）
- 连接池：SQLAlchemy `AsyncAdaptedQueuePool`（`pool_size` / `max_overflow` / `pool_pre_ping`）
- 迁移：Alembic（目录 `migrations/`，业务迁移后续添加）

## 连接

环境变量：`DATABASE_URL`

开发（本机 `postgres-server`）：

```text
postgresql+asyncpg://testuser:testpassword@localhost:5432/testdb
```

Docker Compose 内（服务名 `postgres`）：

```text
postgresql+asyncpg://offer:offer@postgres:5432/offer_helper
```

业务代码通过：

```python
from app.infrastructure.database import get_engine, session_scope, get_session_factory
from app.api.dependencies import get_db_session
```

禁止业务代码直接 `create_async_engine()` / `asyncpg.connect()`。

## 连接池配置（YAML）

```yaml
database:
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 1800
  echo: false
```

## 卷（Compose）

- Compose volume：`postgres_data`
- 挂载点：`/var/lib/postgresql`

## 当前范围

已提供引擎、连接池、Session 工厂与 lifespan 启停。

不创建业务表（User / Resume / Job 等）。

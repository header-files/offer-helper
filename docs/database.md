# 数据库文档（Phase 0）

## 引擎

- PostgreSQL **18.6**（Docker 镜像 `postgres:18.6`）
- 异步驱动：`asyncpg`
- ORM：SQLAlchemy 2.x
- 迁移：Alembic（目录 `migrations/`，业务迁移在后续阶段添加）

## 连接

- 环境变量：`DATABASE_URL`
- Compose 内示例：

```text
postgresql+asyncpg://offer:offer@postgres:5432/offer_helper
```

注意主机名为 `postgres`，不是 `localhost`。

## 卷

- Compose volume：`postgres_data`
- 挂载点：`/var/lib/postgresql`（适配 PostgreSQL 18 镜像布局）

## Phase 0 范围

不创建业务表（User / Resume / Job 等）。仅保证数据库容器可健康启动，供后续迁移使用。

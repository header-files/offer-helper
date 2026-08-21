# Docker 文档

## 文件

- `Dockerfile`：Python 3.12 + `uv sync --frozen`，运行 `uvicorn app.main:app`
- `docker-compose.yml`：`app` / `postgres` / `redis`
- App healthcheck：容器内用 `curl -fsS http://127.0.0.1:8000/health`

## 版本锁定

| 服务 | 镜像 |
|------|------|
| PostgreSQL | `postgres:18.6` |
| Redis | `redis:8.0.2` |

## 网络与主机名

- Network：`offer-helper-net`
- App → DB：`postgres`
- App → Cache：`redis`

## 数据卷

- `postgres_data`
- `redis_data`

## Healthcheck

三个服务均配置 healthcheck；`app` 依赖 postgres/redis 健康后再启动。

## 常用命令

```bash
cp .env.example .env
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs -f app
docker compose down
```

验证健康：

```bash
curl http://127.0.0.1:8000/health
```

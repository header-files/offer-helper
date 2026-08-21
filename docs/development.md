# 开发文档

## 前置

- Python 3.12+
- uv
- Docker / Docker Compose
- Git

## 初始化

```bash
git checkout feature/phase-0-bootstrap
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

## 分支

- `main`：稳定主干
- `feature/phase-0-bootstrap`：当前阶段

完成验收后等待下一阶段指令，不要自行进入 Phase 1。

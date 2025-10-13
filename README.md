# Task Time Tracking

タスクタイムトラッキングWebアプリ - Django REST Framework + React

## 開発環境

### 必要なツール

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- uv (Python package manager)
- pnpm (Node.js package manager)
- lefthook (Git hooks manager)

### セットアップ

#### 1. Backend (Django)

```bash
cd backend
uv sync --all-extras
```

#### 2. Frontend (React)

```bash
cd frontend
pnpm install
```

#### 3. Git Hooks

```bash
lefthook install
```

## 開発

### Backend

```bash
cd backend
uv run python manage.py runserver
```

### Frontend

```bash
cd frontend
pnpm dev
```

## テスト

### Backend

```bash
cd backend
uv run pytest
```

### Frontend

```bash
cd frontend
pnpm test
```

## リンター・フォーマッター

### Backend

```bash
cd backend
uv run ruff check .
uv run black .
uv run mypy .
```

### Frontend

```bash
cd frontend
pnpm eslint .
pnpm prettier --write .
```

## ディレクトリ構成

```
.
├── backend/          # Django REST Framework API
├── frontend/         # React + TypeScript SPA
├── .kiro/            # Kiro spec-driven development
├── lefthook.yml      # Git hooks configuration
└── README.md
```

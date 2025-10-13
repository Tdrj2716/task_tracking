# Implementation Tasks

## Overview

このドキュメントは、タスクタイムトラッキングWebアプリの実装タスクを定義します。Django REST FrameworkバックエンドとReactフロントエンドの構築、Google OAuth認証、タスク階層構造、プロジェクト管理、タグ管理、時間記録・レポート機能を実装します。

すべてのタスクは要件ドキュメント（requirements.md）と設計ドキュメント（design.md）にトレース可能であり、段階的に実装を進めます。

## Development Environment Setup

### パッケージ管理ツール

- **Backend**: uv（Python パッケージ管理）
- **Frontend**: pnpm（Node.js パッケージ管理）
- **Git Hooks**: lefthook（pre-commit フック管理）

### Phase 動作テスト

各 Phase 終了時に動作テストを実施します：

- **Phase 1 完了時**: Backend API の基本動作確認（Django Admin、モデル CRUD）
- **Phase 2 完了時**: API エンドポイントの統合テスト（Postman/HTTPie）
- **Phase 3 完了時**: Frontend 基盤の動作確認（Storybook、API 通信）
- **Phase 4 完了時**: E2E フロー確認（ログイン → タイマー → レポート）

## Task List

### Task 1: 開発環境のセットアップ（uv、pnpm、lefthook）

**Status**: pending

**Requirement Traceability**: 全要件の基盤

**Design Traceability**: Development Environment

**Description**: uv、pnpm、lefthook をセットアップし、プロジェクトの開発環境を整備します。

**Implementation**:

1. **uv のインストールと設定**
   - uv をインストール（`curl -LsSf https://astral.sh/uv/install.sh | sh`）
   - Backend ディレクトリで `uv init` を実行
   - `pyproject.toml` に Django、DRF、PostgreSQL driver などの依存関係を追加
   - `uv sync` で依存関係をインストール
2. **pnpm のインストールと設定**
   - pnpm をインストール（`npm install -g pnpm`）
   - Frontend ディレクトリで pnpm を使用する設定
3. **lefthook のインストールと設定**
   - lefthook をインストール
   - `lefthook.yml` を作成
     - pre-commit: Backend（ruff、black、mypy）と Frontend（ESLint、Prettier）のリンター実行
     - pre-push: テスト実行
   - `lefthook install` で Git hooks を有効化
4. `.gitignore` を作成
   - Python（`__pycache__/`, `.venv/`, `*.pyc`）
   - Node.js（`node_modules/`, `dist/`）
   - IDE（`.vscode/`, `.idea/`）

**Acceptance Criteria**:

- uv で Python 依存関係がインストールされる
- pnpm で Node.js 依存関係がインストールされる
- lefthook の pre-commit フックが動作する

---

### Task 2: Django プロジェクトのセットアップ

**Status**: pending

**Requirement Traceability**: 全要件の基盤、特に Requirement 7（データ永続化）、Requirement 8（ユーザー認証）

**Design Traceability**: Architecture - Backend (Django 5.x + DRF + PostgreSQL)

**Description**: Django プロジェクトとアプリケーションの初期セットアップを行い、PostgreSQL データベースとの接続を確立します。

**Implementation**:

1. uv で Django 5.x プロジェクトを作成（`uv run django-admin startproject config .`）
2. メインアプリケーション `api` を作成（`uv run python manage.py startapp api`）
3. PostgreSQL データベース設定を `settings.py` に追加
   - `DATABASES` 設定（psycopg3 使用）
4. Django REST Framework を `pyproject.toml` に追加して `uv sync`
5. `INSTALLED_APPS` に DRF と api アプリを追加
6. 初期マイグレーションを実行してデータベーススキーマを作成
7. 開発サーバーが正常に起動することを確認

**Acceptance Criteria**:

- `uv run python manage.py runserver` で開発サーバーが起動する
- PostgreSQL に接続できる
- Django Admin にアクセスできる

---

### Task 3: ユーザーモデルとプロジェクト・タグ・タスクモデルの定義

**Status**: completed

**Requirement Traceability**: Requirement 1（タスク管理）、Requirement 9（タスク階層）、Requirement 10（プロジェクト管理）、Requirement 11（タグ管理）

**Design Traceability**: Data Models - User, Project, Tag, Task

**Description**: Django ORM を使用して User（AbstractUser）、Project、Tag、Task モデルを定義し、リレーションシップとバリデーションロジックを実装します。

**Implementation**:

1. `User` モデル（Django AbstractUser を継承）を定義
2. `Project` モデルを定義
   - `user` ForeignKey (CASCADE)
   - `name` CharField(max_length=100)
   - `is_inbox` BooleanField(default=False)
   - `created_at`, `updated_at` DateTimeField
   - UniqueConstraint で各ユーザー1つのInboxを保証
   - Meta: ordering, indexes
3. `Tag` モデルを定義
   - `user` ForeignKey (CASCADE)
   - `name` CharField(max_length=50)
   - `color` CharField(max_length=7, default='#gray')
   - `created_at` DateTimeField
   - UniqueConstraint で (user, name) の一意性を保証
   - Meta: ordering, indexes
4. `Task` モデルを定義
   - `user` ForeignKey (CASCADE)
   - `name` CharField(max_length=100)
   - `project` ForeignKey to Project (SET_NULL, nullable)
   - `parent` ForeignKey to self (CASCADE, nullable)
   - `tags` ManyToManyField to Tag
   - `created_at`, `updated_at` DateTimeField
   - `get_depth()` メソッド: 階層の深さを計算（0=ルート、1=子、2=孫）
   - `clean()` メソッド: 3階層制限のバリデーション
   - `save()` メソッド: `full_clean()` を呼び出してバリデーション
   - `get_all_children()` メソッド: すべての子孫タスクを再帰的に取得
   - Meta: ordering, indexes（user+created_at、user+project、parent）
5. マイグレーションファイルを生成して実行
6. Django Admin でモデルを登録して動作確認

**Acceptance Criteria**:

- すべてのモデルがマイグレーション済み
- Django Admin でモデルの CRUD 操作が可能
- Task の `get_depth()` が正しく階層レベルを返す
- Task の `clean()` が3階層を超えるタスクを拒否する

---

### Task 4: TimeEntry モデルの定義

**Status**: pending

**Requirement Traceability**: Requirement 2（時間記録）、Requirement 3（時間記録の編集・削除）、Requirement 4（時間記録一覧）

**Design Traceability**: Data Models - TimeEntry

**Description**: 時間記録を管理する TimeEntry モデルを定義し、タスクとのリレーションシップと経過時間の自動計算を実装します。

**Implementation**:

1. `TimeEntry` モデルを定義
   - `user` ForeignKey to User (CASCADE)
   - `task` ForeignKey to Task (SET_NULL, nullable)
   - `start_time` DateTimeField
   - `end_time` DateTimeField
   - `duration_seconds` IntegerField
   - `created_at` DateTimeField(auto_now_add=True)
   - `save()` メソッド: duration_seconds を自動計算
   - `__str__()` メソッド: タスク名（または「タスク未指定」）と duration を表示
   - Meta: ordering by start_time DESC、indexes（user+start_time、user+task+start_time）
2. マイグレーションファイルを生成して実行
3. Django Admin で TimeEntry を登録して動作確認

**Acceptance Criteria**:

- TimeEntry モデルがマイグレーション済み
- `save()` で duration_seconds が自動計算される
- タスク削除時に TimeEntry の task フィールドが NULL に更新される（SET_NULL）

---

### Task 5: django-allauth と dj-rest-auth のセットアップ

**Status**: pending

**Requirement Traceability**: Requirement 8（ユーザー認証）

**Design Traceability**: Components - AuthService (django-allauth + dj-rest-auth)

**Description**: Google OAuth 認証のために django-allauth と dj-rest-auth をインストール・設定します。

**Implementation**:

1. django-allauth と dj-rest-auth をインストール
2. `INSTALLED_APPS` に追加
   - `rest_framework.authtoken`
   - `dj_rest_auth`
   - `django.contrib.sites`
   - `allauth`
   - `allauth.account`
   - `allauth.socialaccount`
   - `allauth.socialaccount.providers.google`
   - `dj_rest_auth.registration`
3. `AUTHENTICATION_BACKENDS` に追加
   - `django.contrib.auth.backends.ModelBackend`
   - `allauth.account.auth_backends.AuthenticationBackend`
4. `SOCIALACCOUNT_PROVIDERS` で Google 設定
   - SCOPE: ['profile', 'email']
   - AUTH_PARAMS: {'access_type': 'online'}
   - OAUTH_PKCE_ENABLED: True
5. `SITE_ID = 1` を設定
6. URLs に allauth と dj-rest-auth のエンドポイントを追加
7. マイグレーションを実行
8. Django Admin で SocialApp（Google OAuth）を作成

**Acceptance Criteria**:

- `/accounts/google/login/` にアクセスすると Google OAuth リダイレクトが発生する
- `/api/auth/user/` が認証済みユーザー情報を返す

---

### Task 6: DRF の認証・パーミッション設定

**Status**: pending

**Requirement Traceability**: Requirement 8（ユーザー認証）、全要件（認証必須）

**Design Traceability**: Architecture - DRF ViewSet and TokenAuthentication

**Description**: Django REST Framework の認証とパーミッションを設定し、すべての API エンドポイントを保護します。

**Implementation**:

1. `REST_FRAMEWORK` 設定を `settings.py` に追加
   - `DEFAULT_AUTHENTICATION_CLASSES`: `rest_framework.authentication.TokenAuthentication`
   - `DEFAULT_PERMISSION_CLASSES`: `rest_framework.permissions.IsAuthenticated`
   - `DEFAULT_PAGINATION_CLASS`: `rest_framework.pagination.PageNumberPagination`
   - `PAGE_SIZE`: 100
2. カスタムパーミッション `IsOwner` を作成
   - `has_object_permission` でユーザー所有チェック
3. ヘルスチェックエンドポイント `/api/health/` を作成（認証不要）

**Acceptance Criteria**:

- 未認証のリクエストが 401 Unauthorized を返す
- 認証済みのリクエストが成功する
- `/api/health/` が認証なしでアクセス可能

---

### Task 7: Phase 1 動作テスト - Backend 基本動作確認

**Status**: pending

**Requirement Traceability**: 全要件（Phase 1 の基盤確認）

**Design Traceability**: Testing Strategy

**Description**: Phase 1 完了時の動作テストを実施し、Django Admin とモデル CRUD の基本動作を確認します。

**Implementation**:

1. Django Admin にアクセスして全モデルが表示されることを確認
2. Admin でユーザーを作成し、Inbox プロジェクトが自動作成されることを確認
3. Admin でタスクを作成し、階層構造（親・子・孫）が正しく動作することを確認
4. Admin で孫タスクに子を追加しようとすると、バリデーションエラーが発生することを確認
5. Admin でタスクを削除し、子孫タスクも削除されることを確認
6. Admin で TimeEntry を作成し、duration_seconds が自動計算されることを確認
7. PostgreSQL に直接接続して、制約（UniqueConstraint など）が正しく設定されていることを確認

**Acceptance Criteria**:

- すべてのモデルが Django Admin で正しく表示・操作できる
- タスク階層の3階層制限が動作する
- Inbox プロジェクトが自動作成される
- データベース制約が正しく機能する

---

### Task 8: Project ViewSet とシリアライザの実装

**Status**: pending

**Requirement Traceability**: Requirement 10（プロジェクト管理）

**Design Traceability**: Requirements Traceability - Requirement 10

**Description**: Project の CRUD API エンドポイントを実装し、Inbox プロジェクトの自動作成を実装します。

**Implementation**:

1. `ProjectSerializer` を作成
   - fields: ['id', 'name', 'is_inbox', 'created_at', 'updated_at']
   - read_only_fields: ['id', 'is_inbox', 'created_at', 'updated_at']
   - バリデーション: name は必須、max_length=100
2. `ProjectViewSet` を作成
   - `get_queryset()`: `Project.objects.filter(user=request.user)`
   - `perform_create()`: user を自動設定
3. URLs に `/api/projects/` を追加
4. ユーザー作成時に自動的に Inbox プロジェクトを作成する signal を実装
   - `post_save` signal for User model
   - `Project.objects.get_or_create(user=user, is_inbox=True, defaults={'name': 'Inbox'})`

**Acceptance Criteria**:

- GET `/api/projects/` でユーザーのプロジェクト一覧を取得できる
- POST `/api/projects/` で新しいプロジェクトを作成できる
- 新規ユーザー作成時に Inbox プロジェクトが自動作成される
- Inbox プロジェクトは削除できない（バリデーションまたは ViewSet で制限）

---

### Task 9: Tag ViewSet とシリアライザの実装

**Status**: pending

**Requirement Traceability**: Requirement 11（タグ管理）

**Design Traceability**: Requirements Traceability - Requirement 11

**Description**: Tag の CRUD API エンドポイントを実装し、ユーザー単位でのタグ名の一意性を保証します。

**Implementation**:

1. `TagSerializer` を作成
   - fields: ['id', 'name', 'color', 'created_at']
   - read_only_fields: ['id', 'created_at']
   - バリデーション: name は必須、max_length=50、color は Hex 形式
2. `TagViewSet` を作成
   - `get_queryset()`: `Tag.objects.filter(user=request.user)`
   - `perform_create()`: user を自動設定
3. URLs に `/api/tags/` を追加

**Acceptance Criteria**:

- GET `/api/tags/` でユーザーのタグ一覧を取得できる
- POST `/api/tags/` で新しいタグを作成できる
- 同じユーザーで同じ名前のタグを作成すると 400 エラーを返す

---

### Task 10: Task ViewSet とシリアライザの実装

**Status**: pending

**Requirement Traceability**: Requirement 1（タスク管理）、Requirement 9（タスク階層）

**Design Traceability**: Components - TaskViewSet、Requirements Traceability - Requirement 1, 9

**Description**: Task の CRUD API エンドポイントを実装し、階層構造とタグ・プロジェクトのリレーションシップをサポートします。

**Implementation**:

1. `TaskSerializer` を作成
   - fields: ['id', 'name', 'project', 'parent', 'tags', 'created_at', 'updated_at']
   - read_only_fields: ['id', 'created_at', 'updated_at']
   - `project_name` フィールド（read_only）: project.name を表示
   - `parent_name` フィールド（read_only）: parent.name を表示
   - `tag_names` フィールド（read_only）: tags の name リストを表示
   - `depth` フィールド（read_only）: `get_depth()` を表示
   - バリデーション: name は必須、max_length=100
2. `TaskViewSet` を作成
   - `get_queryset()`: `Task.objects.filter(user=request.user).select_related('project', 'parent').prefetch_related('tags')`
   - `perform_create()`: user を自動設定、project が未設定の場合は Inbox プロジェクトを設定
   - フィルタリング: DjangoFilterBackend で project、parent、tags によるフィルタリング
   - ソート: OrderingFilter で created_at、name によるソート
3. URLs に `/api/tasks/` を追加
4. タスク作成時に project が null の場合、Inbox プロジェクトを自動設定するロジックを `perform_create()` に追加

**Acceptance Criteria**:

- GET `/api/tasks/` でユーザーのタスク一覧を取得できる
- POST `/api/tasks/` で新しいタスクを作成できる
- タスク作成時に project が未設定の場合、自動的に Inbox プロジェクトが設定される
- 親タスクを指定してサブタスクを作成できる
- 3階層を超えるタスクを作成しようとすると 400 エラーを返す
- タスクに複数のタグを設定できる

---

### Task 11: TimeEntry ViewSet とシリアライザの実装

**Status**: pending

**Requirement Traceability**: Requirement 2（時間記録）、Requirement 3（時間記録の編集・削除）、Requirement 4（時間記録一覧）

**Design Traceability**: Components - TimeEntryViewSet、Requirements Traceability - Requirement 2, 3, 4

**Description**: TimeEntry の CRUD API エンドポイントを実装し、タスク未指定の時間記録をサポートします。

**Implementation**:

1. `TimeEntrySerializer` を作成
   - fields: ['id', 'task', 'task_name', 'start_time', 'end_time', 'duration_seconds', 'created_at']
   - read_only_fields: ['id', 'duration_seconds', 'created_at']
   - `task_name` フィールド（read_only）: task.name を表示（nullable）
   - `validate()`: end_time > start_time のバリデーション
   - `create()`: duration_seconds を自動計算、user を自動設定
   - `update()`: duration_seconds を再計算
2. `TimeEntryViewSet` を作成
   - `get_queryset()`: `TimeEntry.objects.filter(user=request.user).select_related('task')`
   - フィルタリング: DjangoFilterBackend で task、date（start_time__date）、date_range によるフィルタリング
   - ソート: OrderingFilter で start_time、created_at によるソート（デフォルト: -start_time）
3. URLs に `/api/time-entries/` を追加

**Acceptance Criteria**:

- GET `/api/time-entries/` でユーザーの時間記録一覧を取得できる
- POST `/api/time-entries/` で新しい時間記録を作成できる（task は optional）
- PUT `/api/time-entries/{id}/` で時間記録を編集できる
- DELETE `/api/time-entries/{id}/` で時間記録を削除できる
- end_time が start_time より前の場合、400 エラーを返す
- `?date=2025-10-13` でフィルタリングできる

---

### Task 12: レポート API の実装（日次・週次・月次）

**Status**: pending

**Requirement Traceability**: Requirement 5（時間統計とレポート）

**Design Traceability**: Components - ReportView (APIView)、Requirements Traceability - Requirement 5

**Description**: 日次・週次・月次の時間レポート API を実装し、タスクごとの集計データを提供します。

**Implementation**:

1. `DailyReportView` (APIView) を作成
   - `get(request)`: `?date=YYYY-MM-DD` パラメータ必須
   - `TimeEntry.objects.filter(user=request.user, start_time__date=date)`
   - タスクごとの集計: `.values('task__id', 'task__name').annotate(duration_seconds=Sum('duration_seconds'), entry_count=Count('id'))`
   - レスポンス: `{date, tasks: [...], total_seconds}`
2. `WeeklyReportView` (APIView) を作成
   - `get(request)`: `?start_date=YYYY-MM-DD` パラメータ必須
   - 7日間の日次レポートを集計
   - レスポンス: `{week_start, week_end, daily_breakdown: [...], total_seconds}`
3. `MonthlyReportView` (APIView) を作成
   - `get(request)`: `?year=YYYY&month=MM` パラメータ必須
   - 月内の日次レポートを集計
   - レスポンス: `{year, month, daily_breakdown: [...], total_seconds}`
4. URLs に `/api/reports/daily/`、`/api/reports/weekly/`、`/api/reports/monthly/` を追加
5. プロジェクト別レポート API `ProjectReportView` を作成
   - レスポンス: プロジェクトごとの合計作業時間
6. タグ別レポート API `TagReportView` を作成
   - レスポンス: タグごとの合計作業時間

**Acceptance Criteria**:

- GET `/api/reports/daily/?date=2025-10-13` で日次レポートを取得できる
- GET `/api/reports/weekly/?start_date=2025-10-13` で週次レポートを取得できる
- GET `/api/reports/monthly/?year=2025&month=10` で月次レポートを取得できる
- プロジェクト別レポートとタグ別レポートを取得できる

---

### Task 13: CORS 設定とフロントエンド連携準備

**Status**: pending

**Requirement Traceability**: 全要件（フロントエンド連携のため）

**Design Traceability**: Security Considerations - CORS 設定

**Description**: django-cors-headers をインストールして CORS を設定し、React フロントエンドからのリクエストを許可します。

**Implementation**:

1. django-cors-headers をインストール
2. `INSTALLED_APPS` に `corsheaders` を追加
3. `MIDDLEWARE` の先頭に `corsheaders.middleware.CorsMiddleware` を追加
4. `CORS_ALLOWED_ORIGINS` を設定
   - `http://localhost:5173` (Vite dev server)
5. `CORS_ALLOW_CREDENTIALS = True` を設定

**Acceptance Criteria**:

- React フロントエンド（localhost:5173）から API リクエストが成功する
- CORS エラーが発生しない

---

### Task 14: Phase 2 動作テスト - API エンドポイント統合テスト

**Status**: pending

**Requirement Traceability**: 全要件（Phase 2 の API 確認）

**Design Traceability**: Testing Strategy - Integration Tests

**Description**: Phase 2 完了時の動作テストを実施し、すべての API エンドポイントが正しく動作することを確認します。

**Implementation**:

1. HTTPie または Postman で API テストスイートを作成
2. 認証フロー確認
   - Google OAuth ログイン → トークン取得 → `/api/auth/user/` でユーザー情報取得
3. プロジェクト API 確認
   - POST `/api/projects/` でプロジェクト作成
   - GET `/api/projects/` でプロジェクト一覧取得
   - Inbox プロジェクトの削除が拒否されることを確認
4. タグ API 確認
   - POST `/api/tags/` でタグ作成
   - 同名タグ作成時に 400 エラー確認
5. タスク API 確認
   - POST `/api/tasks/` でタスク作成（project 未指定時に Inbox 設定確認）
   - 親タスク → 子タスク → 孫タスク作成
   - 孫タスクに子タスク作成時に 400 エラー確認
6. TimeEntry API 確認
   - POST `/api/time-entries/` で時間記録作成
   - GET `/api/time-entries/?date=YYYY-MM-DD` でフィルタリング確認
7. レポート API 確認
   - GET `/api/reports/daily/?date=YYYY-MM-DD` で日次レポート取得
   - GET `/api/reports/weekly/`、`/api/reports/monthly/` 確認

**Acceptance Criteria**:

- すべての API エンドポイントが正しくレスポンスを返す
- 認証が必要なエンドポイントで未認証時に 401 を返す
- バリデーションエラーが正しく動作する

---

### Task 15: React プロジェクトのセットアップ

**Status**: pending

**Requirement Traceability**: Requirement 6（ユーザーインターフェース）、全要件（UI 実装のため）

**Design Traceability**: Architecture - Frontend (React 18 + TypeScript + Vite)

**Description**: React + TypeScript + Vite でフロントエンドプロジェクトを作成し、必要なライブラリをインストールします。

**Implementation**:

1. pnpm で Vite + React + TypeScript プロジェクトを作成（`pnpm create vite frontend --template react-ts`）
2. 必要なライブラリを pnpm でインストール
   - `axios`: API 通信
   - `zustand`: 状態管理
   - `react-router-dom`: ルーティング
   - `tailwindcss`: スタイリング
   - `@radix-ui/react-*`: UI コンポーネント
   - `date-fns`: 日付操作
3. Tailwind CSS を設定
4. `src/` ディレクトリ構造を作成
   - `components/`: React コンポーネント
   - `stores/`: Zustand ストア
   - `services/`: API クライアント、Timer Service
   - `pages/`: ページコンポーネント
   - `types/`: TypeScript 型定義
5. `vite.config.ts` に環境変数設定
   - `VITE_API_URL`: バックエンド API URL

**Acceptance Criteria**:

- `pnpm dev` で開発サーバーが起動する
- Tailwind CSS が正しく動作する
- ディレクトリ構造が整備されている

---

### Task 16: Storybook のセットアップ

**Status**: pending

**Requirement Traceability**: Requirement 6（ユーザーインターフェース）

**Design Traceability**: Testing Strategy - Frontend UI Testing

**Description**: Storybook を導入し、UI コンポーネントの開発環境を整備します。将来的な Storycap + reg-suit 対応を考慮した設定を行います。

**Implementation**:

1. Storybook を pnpm でインストール（`pnpm dlx storybook@latest init`）
2. Tailwind CSS を Storybook に統合
   - `.storybook/preview.ts` で Tailwind CSS をインポート
3. Storybook の基本設定
   - `.storybook/main.ts` で Vite との統合設定
4. サンプルストーリーを作成
   - `src/components/Button.stories.tsx` を作成
5. 将来の Storycap + reg-suit 対応のためのコメントを追加
   - `package.json` に `storycap` と `reg-suit` の設定例をコメントで記載

**Acceptance Criteria**:

- `pnpm storybook` で Storybook が起動する
- Tailwind CSS が Storybook で動作する
- サンプルストーリーが表示される

---

### Task 17: Axios API クライアントの実装

**Status**: pending

**Requirement Traceability**: 全要件（API 通信のため）

**Design Traceability**: Components - Axios API Client

**Description**: Axios インスタンスを作成し、認証トークンの自動付与とエラーハンドリングを実装します。

**Implementation**:

1. `src/services/apiClient.ts` を作成
2. Axios インスタンスを作成
   - baseURL: `import.meta.env.VITE_API_URL || 'http://localhost:8000'`
   - headers: `Content-Type: application/json`
3. リクエストインターセプターを実装
   - localStorage から authToken を取得
   - `Authorization: Token ${token}` ヘッダーを付与
4. レスポンスインターセプターを実装
   - 401 Unauthorized の場合、localStorage から authToken を削除し、ログインページへリダイレクト
   - エラーメッセージを統一形式で処理

**Acceptance Criteria**:

- API リクエストに自動的に認証トークンが付与される
- 401 エラー時にログインページへリダイレクトされる

---

### Task 18: TypeScript 型定義の作成

**Status**: pending

**Requirement Traceability**: 全要件（型安全性のため）

**Design Traceability**: Frontend - React 18 + TypeScript

**Description**: バックエンド API のレスポンス型と Domain Model に対応する TypeScript 型を定義します。

**Implementation**:

1. `src/types/index.ts` を作成
2. 型定義を追加
   - `User`: id, username, email
   - `Project`: id, name, is_inbox, created_at, updated_at
   - `Tag`: id, name, color, created_at
   - `Task`: id, name, project, project_name, parent, parent_name, tags, tag_names, depth, created_at, updated_at
   - `TimeEntry`: id, task, task_name, start_time, end_time, duration_seconds, created_at
   - `DailyReport`: date, tasks, total_seconds
   - `ActiveTimer`: taskId, startTime

**Acceptance Criteria**:

- すべての API レスポンスに対応する型が定義されている
- IDE で型補完が動作する

---

### Task 19: Zustand ストアの実装

**Status**: pending

**Requirement Traceability**: Requirement 6（ユーザーインターフェース）、全要件（状態管理のため）

**Design Traceability**: Frontend - State Management (Zustand)

**Description**: グローバル状態管理のための Zustand ストアを実装します。

**Implementation**:

1. `src/stores/authStore.ts` を作成
   - state: currentUser, authToken
   - actions: login, logout, fetchCurrentUser
2. `src/stores/projectStore.ts` を作成
   - state: projects
   - actions: fetchProjects, createProject, deleteProject
3. `src/stores/tagStore.ts` を作成
   - state: tags
   - actions: fetchTags, createTag, deleteTag
4. `src/stores/taskStore.ts` を作成
   - state: tasks
   - actions: fetchTasks, createTask, updateTask, deleteTask, filterByProject, filterByTags
5. `src/stores/timeEntryStore.ts` を作成
   - state: timeEntries, recentEntries
   - actions: fetchTimeEntries, createTimeEntry, updateTimeEntry, deleteTimeEntry
6. `src/stores/timerStore.ts` を作成
   - state: isRunning, elapsedSeconds, activeTimer
   - actions: updateElapsed

**Acceptance Criteria**:

- 各ストアが正しく状態管理を行う
- API 呼び出しがストアのアクションに実装されている

---

### Task 20: Timer Service の実装

**Status**: pending

**Requirement Traceability**: Requirement 2（時間記録）

**Design Traceability**: Components - Timer Service (Client-side)

**Description**: クライアント側でのタイマー管理ロジックを実装し、localStorage への永続化とバックエンドへの POST を実装します。

**Implementation**:

1. `src/services/timerService.ts` を作成
2. `TimerService` クラスを実装
   - `startTimer(taskId?: string)`: タイマーを開始、localStorage に保存、既存タイマーを自動停止
   - `stopTimer()`: タイマーを停止、TimeEntry を POST、localStorage をクリア、timeEntryStore を更新
   - `getElapsedSeconds()`: 経過秒数を取得
   - `isRunning()`: タイマーが実行中かどうか
   - `getActiveTimer()`: localStorage から ActiveTimer を取得
   - `restoreTimer()`: ページリロード時に localStorage からタイマーを復元
3. `setInterval` で毎秒 `timerStore.updateElapsed()` を呼び出す
4. ページリロード時に `restoreTimer()` を呼び出す

**Acceptance Criteria**:

- タイマーを開始・停止できる
- 経過時間がリアルタイムで更新される
- ページリロード後もタイマーが復元される
- タイマー停止時に TimeEntry がバックエンドに保存される

---

### Task 21: Phase 3 動作テスト - Frontend 基盤確認

**Status**: pending

**Requirement Traceability**: 全要件（Phase 3 の Frontend 基盤確認）

**Design Traceability**: Testing Strategy - Frontend Integration

**Description**: Phase 3 完了時の動作テストを実施し、Frontend 基盤（Storybook、API 通信、状態管理）が正しく動作することを確認します。

**Implementation**:

1. Storybook で UI コンポーネントを確認
   - すべてのストーリーが正しく表示されることを確認
2. Axios API クライアントのテスト
   - ブラウザ DevTools で認証トークンが自動付与されることを確認
   - 401 エラー時にログインページへリダイレクトされることを確認
3. Zustand ストアのテスト
   - ブラウザで各ストアの state が正しく更新されることを確認
   - API 呼び出しが成功することを確認
4. Timer Service のテスト
   - タイマーを開始してリアルタイム更新を確認
   - ページリロード後にタイマーが復元されることを確認
   - localStorage にタイマー状態が保存されることを確認
5. Backend API との統合確認
   - Frontend から Backend API へリクエストが成功することを確認
   - CORS エラーが発生しないことを確認

**Acceptance Criteria**:

- Storybook ですべてのコンポーネントが正しく表示される
- API クライアントが正しく動作する
- Zustand ストアが状態管理を正しく行う
- Timer Service がリアルタイムで動作する
- Frontend-Backend 統合が成功する

---

### Task 22: ログインページの実装

**Status**: pending

**Requirement Traceability**: Requirement 8（ユーザー認証）

**Design Traceability**: System Flows - 認証フロー（django-allauth Google OAuth）

**Description**: Google OAuth ログインのための UI を実装します。

**Implementation**:

1. `src/pages/LoginPage.tsx` を作成
2. Google ログインボタンを実装
   - クリック時に `window.location.href = 'http://localhost:8000/accounts/google/login/'` へリダイレクト
3. OAuth コールバック後のトークン処理
   - URL パラメータまたはクッキーからトークンを取得
   - localStorage に authToken を保存
   - authStore の login() を呼び出し
   - ダッシュボードへリダイレクト
4. LoginPage の Storybook ストーリーを作成

**Acceptance Criteria**:

- ログインページで Google ログインボタンが表示される
- ボタンクリックで Google OAuth 認証フローが開始される
- 認証成功後にトークンが保存され、ダッシュボードへリダイレクトされる
- Storybook でログインページが表示される

---

### Task 23: ダッシュボードページの実装

**Status**: pending

**Requirement Traceability**: Requirement 6（ユーザーインターフェース）、全要件（メイン画面のため）

**Design Traceability**: Components - Dashboard Component

**Description**: メインダッシュボードを実装し、タイマーウィジェット、タスク一覧、最近の時間記録を統合表示します。

**Implementation**:

1. `src/pages/DashboardPage.tsx` を作成
2. `useEffect` で初期データ取得
   - `projectStore.fetchProjects()`
   - `tagStore.fetchTags()`
   - `taskStore.fetchTasks()`
   - `timeEntryStore.fetchTimeEntries()`
3. レイアウト構成
   - ヘッダー: ユーザー名、ログアウトボタン
   - メインエリア: TimerWidget、TaskList、RecentEntries の3つのセクション

**Acceptance Criteria**:

- ダッシュボードが正しく表示される
- 初期データが取得されて表示される
- ログアウトボタンが機能する

---

### Task 24: Timer Widget コンポーネントの実装

**Status**: pending

**Requirement Traceability**: Requirement 2（時間記録）

**Design Traceability**: Components - Timer Service

**Description**: タイマーの開始・停止 UI とリアルタイム経過時間表示を実装します。

**Implementation**:

1. `src/components/TimerWidget.tsx` を作成
2. タスク選択ドロップダウン（全タスク一覧、階層表示）
3. 経過時間表示（HH:MM:SS 形式）
4. スタートボタン（タスク選択 or 未選択）
   - クリック時に `timerService.startTimer(taskId)` を呼び出し
5. ストップボタン
   - クリック時に `timerService.stopTimer()` を呼び出し
6. `timerStore` から `isRunning`, `elapsedSeconds` を購読

**Acceptance Criteria**:

- タスクを選択してタイマーを開始できる
- タスク未選択でもタイマーを開始できる
- 経過時間がリアルタイムで更新される
- ストップボタンで時間記録が保存される

---

### Task 25: Task List コンポーネントの実装

**Status**: pending

**Requirement Traceability**: Requirement 1（タスク管理）、Requirement 9（タスク階層）

**Design Traceability**: Requirements Traceability - Requirement 1, 9

**Description**: タスク一覧の表示と CRUD 操作、階層構造の表示を実装します。

**Implementation**:

1. `src/components/TaskList.tsx` を作成
2. タスク一覧表示（階層構造）
   - 親タスク、子タスク、孫タスクをインデントで表示
   - 展開/折りたたみ機能
3. タスク作成フォーム
   - タスク名、プロジェクト選択、親タスク選択、タグ選択（マルチセレクト）
4. タスク編集ボタン
   - モーダルで編集フォームを表示
5. タスク削除ボタン
   - 確認ダイアログを表示
   - 削除時に「関連する時間記録は保持されますが、タスク名は表示されなくなります」と警告
6. フィルタリング機能
   - プロジェクト別フィルター
   - タグ別フィルター

**Acceptance Criteria**:

- タスク一覧が階層構造で表示される
- 新しいタスクを作成できる
- タスクを編集・削除できる
- フィルタリングが機能する

---

### Task 26: Recent Entries コンポーネントの実装

**Status**: pending

**Requirement Traceability**: Requirement 4（時間記録一覧）

**Design Traceability**: Requirements Traceability - Requirement 4

**Description**: 最近の時間記録一覧の表示と編集・削除機能を実装します。

**Implementation**:

1. `src/components/RecentEntries.tsx` を作成
2. 時間記録一覧表示（新しい順）
   - タスク名（または「タスク未指定」）
   - 開始時刻、終了時刻
   - 経過時間（HH:MM:SS 形式）
3. 編集ボタン
   - モーダルで編集フォーム（開始時刻、終了時刻）を表示
4. 削除ボタン
   - 確認ダイアログを表示
5. 手動時間記録追加ボタン
   - モーダルでフォーム（タスク選択、開始時刻、終了時刻）を表示

**Acceptance Criteria**:

- 最近の時間記録が一覧表示される
- 時間記録を編集・削除できる
- 手動で時間記録を追加できる

---

### Task 27: レポートページの実装

**Status**: pending

**Requirement Traceability**: Requirement 5（時間統計とレポート）

**Design Traceability**: Requirements Traceability - Requirement 5

**Description**: 日次・週次・月次レポートの表示とプロジェクト・タグ別レポートを実装します。

**Implementation**:

1. `src/pages/ReportPage.tsx` を作成
2. タブ切り替え UI（日次、週次、月次、プロジェクト別、タグ別）
3. 日次レポート
   - 日付ピッカー
   - タスクごとの作業時間をテーブル表示
   - 合計時間を表示
4. 週次レポート
   - 週の開始日ピッカー
   - 日ごとのブレークダウン表示
5. 月次レポート
   - 年月ピッカー
   - 日ごとのブレークダウン表示
6. プロジェクト別レポート
   - プロジェクトごとの合計作業時間を表示
7. タグ別レポート
   - タグごとの合計作業時間を表示

**Acceptance Criteria**:

- 日次・週次・月次レポートが表示される
- プロジェクト別・タグ別レポートが表示される
- 日付フィルターが機能する

---

### Task 28: Project 管理ページの実装

**Status**: pending

**Requirement Traceability**: Requirement 10（プロジェクト管理）

**Design Traceability**: Requirements Traceability - Requirement 10

**Description**: プロジェクト一覧と CRUD 操作を実装します。

**Implementation**:

1. `src/pages/ProjectPage.tsx` を作成
2. プロジェクト一覧表示
   - Inbox プロジェクトを特別表示
3. プロジェクト作成フォーム
   - プロジェクト名入力
4. プロジェクト編集ボタン
   - モーダルで編集フォーム
5. プロジェクト削除ボタン
   - Inbox プロジェクトは削除不可（ボタンを無効化）
   - 削除時に「関連タスクは Inbox プロジェクトに移動されます」と警告

**Acceptance Criteria**:

- プロジェクト一覧が表示される
- 新しいプロジェクトを作成できる
- プロジェクトを編集・削除できる
- Inbox プロジェクトは削除できない

---

### Task 29: Tag 管理ページの実装

**Status**: pending

**Requirement Traceability**: Requirement 11（タグ管理）

**Design Traceability**: Requirements Traceability - Requirement 11

**Description**: タグ一覧と CRUD 操作を実装します。

**Implementation**:

1. `src/pages/TagPage.tsx` を作成
2. タグ一覧表示
   - タグ名と色を表示
3. タグ作成フォーム
   - タグ名入力、色ピッカー
4. タグ編集ボタン
   - モーダルで編集フォーム
5. タグ削除ボタン
   - 確認ダイアログを表示

**Acceptance Criteria**:

- タグ一覧が表示される
- 新しいタグを作成できる
- タグを編集・削除できる

---

### Task 30: ルーティングの実装

**Status**: pending

**Requirement Traceability**: Requirement 6（ユーザーインターフェース）

**Design Traceability**: Frontend - React Router

**Description**: React Router でページ間のナビゲーションを実装します。

**Implementation**:

1. `src/App.tsx` でルーティング設定
   - `/login`: LoginPage
   - `/dashboard`: DashboardPage（認証必須）
   - `/reports`: ReportPage（認証必須）
   - `/projects`: ProjectPage（認証必須）
   - `/tags`: TagPage（認証必須）
2. ProtectedRoute コンポーネントを作成
   - authStore の authToken をチェック
   - 未認証の場合は LoginPage へリダイレクト
3. ナビゲーションバーコンポーネント
   - ダッシュボード、レポート、プロジェクト、タグへのリンク

**Acceptance Criteria**:

- すべてのページへナビゲーションできる
- 未認証時に保護されたページにアクセスすると LoginPage へリダイレクトされる

---

### Task 31: Phase 4 動作テスト - E2E フロー確認

**Status**: pending

**Requirement Traceability**: 全要件（Phase 4 の E2E 確認）

**Design Traceability**: Testing Strategy - E2E Tests

**Description**: Phase 4 完了時の動作テストを実施し、ログインから主要機能までの E2E フローを確認します。

**Implementation**:

1. **ログインフロー確認**
   - ログインページ表示 → Google ログインボタンクリック → OAuth 認証 → ダッシュボード表示
2. **タスク作成フロー確認**
   - ダッシュボード → タスク作成ボタン → タスク名入力 → プロジェクト選択 → タグ選択 → 保存 → タスク一覧に表示
3. **タイマーフロー確認**
   - タスク選択 → タイマー開始 → 経過時間表示 → ストップ → 時間記録一覧に表示
4. **階層タスク作成フロー確認**
   - 親タスク作成 → 子タスク作成 → 孫タスク作成 → 階層構造で表示
   - 孫タスクに子タスク作成時にエラーメッセージ表示
5. **レポート確認**
   - レポートページ → 日次レポート表示 → 週次・月次レポート切り替え
6. **プロジェクト・タグ管理確認**
   - プロジェクトページでプロジェクト作成・編集・削除
   - タグページでタグ作成・編集・削除
7. **ページ間ナビゲーション確認**
   - ダッシュボード ⇔ レポート ⇔ プロジェクト ⇔ タグ
8. **Storybook 確認**
   - すべてのコンポーネントのストーリーが正しく表示される

**Acceptance Criteria**:

- ログインから主要機能まですべてのフローが正常に動作する
- UI が正しく表示される
- データが正しく保存・取得される
- エラーハンドリングが正しく動作する
- Storybook ですべてのコンポーネントが確認できる

---

### Task 32: エラーハンドリングと通知の実装

**Status**: pending

**Requirement Traceability**: Requirement 6（ユーザーインターフェース）

**Design Traceability**: Error Handling - Error Strategy

**Description**: API エラーのハンドリングと Toast 通知を実装します。

**Implementation**:

1. Toast 通知ライブラリ（react-hot-toast）を pnpm でインストール
2. `src/components/Toast.tsx` を作成
3. API エラー時に Toast 通知を表示
   - 400 Bad Request: フィールドレベルエラーメッセージ
   - 401 Unauthorized: 自動ログアウト
   - 404 Not Found: 「見つかりませんでした」通知
   - 5xx Server Error: 「一時的にサービスが利用できません」通知
4. 成功時の通知
   - タスク作成、時間記録保存などで「保存しました」通知
5. Toast コンポーネントの Storybook ストーリーを作成

**Acceptance Criteria**:

- API エラー時に適切な通知が表示される
- 成功時にも通知が表示される
- Storybook で Toast が表示される

---

### Task 33: ローディング状態の実装

**Status**: pending

**Requirement Traceability**: Requirement 6（ユーザーインターフェース）

**Design Traceability**: Frontend - UI Components

**Description**: API リクエスト中のローディングスピナーを実装します。

**Implementation**:

1. `src/components/LoadingSpinner.tsx` を作成
2. 各ストアに `isLoading` 状態を追加
3. API リクエスト中は `isLoading: true` に設定
4. ページコンポーネントで `isLoading` を購読し、LoadingSpinner を表示

**Acceptance Criteria**:

- API リクエスト中にローディングスピナーが表示される
- Storybook でローディングスピナーが表示される

---

### Task 34: Unit テストの作成（Backend）

**Status**: pending

**Requirement Traceability**: Testing Strategy - Unit Tests

**Design Traceability**: Testing Strategy - Backend (Django)

**Description**: Django モデル、シリアライザ、ViewSet の単体テストを作成します。

**Implementation**:

1. `api/tests/` ディレクトリを作成
2. `test_models.py` を作成
   - Task の `get_depth()` テスト
   - Task の `clean()` バリデーションテスト（3階層制限）
   - TimeEntry の `save()` で duration_seconds が計算されることをテスト
3. `test_serializers.py` を作成
   - TimeEntrySerializer の終了時刻バリデーションテスト
   - TaskSerializer のバリデーションテスト
4. `test_viewsets.py` を作成
   - TaskViewSet のユーザー単位フィルタリングテスト
   - TimeEntryViewSet の CRUD テスト
5. `pytest` でテストを実行

**Acceptance Criteria**:

- すべてのテストが pass する
- テストカバレッジが 80% 以上

---

### Task 35: Integration テストの作成（Backend）

**Status**: pending

**Requirement Traceability**: Testing Strategy - Integration Tests

**Design Traceability**: Testing Strategy - Integration Tests

**Description**: API エンドポイントの統合テストを作成します。

**Implementation**:

1. `api/tests/test_integration.py` を作成
2. 認証フロー統合テスト
   - ログイン → トークン取得 → ユーザー情報取得
3. タイマーフロー統合テスト
   - タスク作成 → タイマー開始 → 停止 → TimeEntry 保存確認
4. タスク削除統合テスト
   - タスク削除 → TimeEntry の task フィールドが NULL 確認
5. フィルタリング統合テスト
   - 日付フィルター、タスクフィルター、タグフィルター

**Acceptance Criteria**:

- すべての統合テストが pass する

---

### Task 36: E2E テストの作成（Frontend）

**Status**: pending

**Requirement Traceability**: Testing Strategy - E2E Tests

**Design Traceability**: Testing Strategy - E2E Tests

**Description**: Playwright で E2E テストを作成します。

**Implementation**:

1. Playwright を pnpm でインストール
2. `tests/e2e/` ディレクトリを作成
3. `timer-flow.spec.ts` を作成
   - ログイン → タスク作成 → タイマー開始 → 停止 → 時間記録確認
4. `task-crud.spec.ts` を作成
   - タスク作成 → 編集 → 削除
5. `report.spec.ts` を作成
   - レポートページ表示 → 日次レポート確認

**Acceptance Criteria**:

- すべての E2E テストが pass する

---

### Task 37: デプロイ準備とドキュメント作成

**Status**: pending

**Requirement Traceability**: 全要件（デプロイのため）

**Design Traceability**: Performance & Scalability

**Description**: 本番環境へのデプロイ準備とドキュメントを作成します。

**Implementation**:

1. README.md を作成
   - プロジェクト概要
   - セットアップ手順
   - 開発環境の起動方法
   - テスト実行方法
2. 環境変数のドキュメント化
   - `.env.example` を作成
3. Django 本番設定
   - `settings_production.py` を作成
   - `DEBUG = False`
   - `ALLOWED_HOSTS` 設定
   - `SECURE_SSL_REDIRECT = True`
4. Gunicorn + Nginx 設定
5. PostgreSQL 本番環境設定
6. フロントエンドビルド設定
   - `npm run build`
   - 静的ファイルの配信

**Acceptance Criteria**:

- README.md が完成している
- 本番環境設定ファイルが作成されている
- ビルドが成功する

---

## Summary

合計 37 タスクを定義しました。以下のフェーズに分類されます：

- **Phase 0: 開発環境セットアップ**（Task 1: uv、pnpm、lefthook）
- **Phase 1: Backend セットアップとモデル定義**（Task 2-6 + Phase 1 テスト: Task 7）
  - Django プロジェクト作成、モデル定義、認証設定、DRF 設定
  - **Phase 1 テスト**: Django Admin での動作確認
- **Phase 2: API エンドポイント実装**（Task 8-13 + Phase 2 テスト: Task 14）
  - Project/Tag/Task/TimeEntry ViewSet、レポート API、CORS 設定
  - **Phase 2 テスト**: HTTPie/Postman での API 統合テスト
- **Phase 3: Frontend セットアップと基盤実装**（Task 15-20 + Phase 3 テスト: Task 21）
  - React プロジェクト作成、Storybook、API クライアント、型定義、Zustand ストア、Timer Service
  - **Phase 3 テスト**: Storybook 確認、API 通信確認、Timer Service 動作確認
- **Phase 4: UI コンポーネント実装**（Task 22-30 + Phase 4 テスト: Task 31）
  - ログイン、ダッシュボード、Timer Widget、Task List、Recent Entries、レポート、プロジェクト管理、タグ管理、ルーティング
  - **Phase 4 テスト**: E2E フロー確認（ログイン → タイマー → レポート）
- **Phase 5: エラーハンドリングとローディング**（Task 32-33）
  - Toast 通知、ローディングスピナー
- **Phase 6: テスト**（Task 34-36）
  - Backend Unit テスト、Integration テスト、Frontend E2E テスト（Playwright）
- **Phase 7: デプロイ準備**（Task 37）
  - README.md、本番環境設定

### 各 Phase のテスト

- **Task 7**: Phase 1 テスト（Django Admin での基本動作確認）
- **Task 14**: Phase 2 テスト（API エンドポイント統合テスト）
- **Task 21**: Phase 3 テスト（Frontend 基盤確認、Storybook、API 通信）
- **Task 31**: Phase 4 テスト（E2E フロー確認）

### パッケージ管理

- **Backend**: uv（Python）
- **Frontend**: pnpm（Node.js）
- **Git Hooks**: lefthook（pre-commit、pre-push）

### Storybook

- Task 16 で Storybook をセットアップ
- 将来的な Storycap + reg-suit 対応を考慮した設定
- 各 UI コンポーネント実装時にストーリーを作成

各タスクは独立して実装可能で、依存関係が明確に定義されています。

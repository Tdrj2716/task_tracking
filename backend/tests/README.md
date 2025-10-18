# Tests Directory

Task Tracking API のテストコードをまとめたディレクトリです。

## ディレクトリ構造

```
tests/
├── README.md               # このファイル
├── __init__.py
├── unit/                   # ユニットテスト
│   ├── __init__.py
│   └── test_models.py     # モデルのテスト（20テスト）
└── api/                    # APIテスト
    ├── __init__.py
    ├── test_postman.py    # Postman APIテスト（9テスト）
    └── postman/           # Postmanコレクション
        ├── README.md
        ├── Task_Tracking_API.postman_collection.json
        └── local.postman_environment.json
```

## テストの種類

### 1. ユニットテスト (`tests/unit/`)

モデルとビジネスロジックの単体テスト

**テスト内容**:
- タスク階層構造（親・子・孫タスク）
- 3階層制限のバリデーション
- プロジェクト継承と伝播
- タスクのカスケード削除
- TimeEntry の duration_seconds 自動計算
- データベース制約（ユニーク制約、CHECK制約）
- タスクのduration_seconds計算（子孫タスクを含む）

**テストケース数**: 20

#### テストケース詳細

**TaskHierarchyTestCase (6テスト)**
- `test_create_parent_task` - 親タスク（Level 0）の作成
- `test_create_child_task` - 子タスク（Level 1）の作成
- `test_create_grandchild_task` - 孫タスク（Level 2）の作成
- `test_project_inheritance_from_root` - プロジェクトのルートタスクからの継承
- `test_project_update_propagation` - プロジェクト変更の子孫タスクへの伝播
- `test_task_with_null_project` - プロジェクトがnullのタスク作成

**TaskHierarchyValidationTestCase (2テスト)**
- `test_cannot_create_great_grandchild_task` - ひ孫タスク（Level 3）の作成拒否
- `test_grandchild_cannot_have_children` - 孫タスクが子を持てないことの確認

**TaskCascadeDeleteTestCase (2テスト)**
- `test_delete_parent_deletes_children` - 親タスク削除時の子タスクのカスケード削除
- `test_delete_parent_deletes_all_descendants` - 親タスク削除時の全子孫タスクのカスケード削除

**TimeEntryTestCase (4テスト)**
- `test_duration_seconds_auto_calculation` - duration_secondsの自動計算
- `test_duration_seconds_null_when_end_time_null` - end_timeがnullの場合のduration_seconds
- `test_name_and_project_auto_set_from_task` - nameとprojectのタスクからの自動設定
- `test_task_delete_sets_null` - タスク削除時のtaskフィールドのNULL設定

**DatabaseConstraintTestCase (4テスト)**
- `test_unique_tag_name_per_user` - ユーザーごとのタグ名ユニーク制約
- `test_different_users_can_have_same_tag_name` - 異なるユーザーが同じタグ名を持てること
- `test_task_level_check_constraint` - タスクのlevelがCHECK制約で2以下に制限
- `test_project_delete_sets_task_project_null` - プロジェクト削除時のタスクのprojectフィールドNULL設定

**TaskDurationTrackingTestCase (12テスト)**
- `test_task_estimate_minutes_can_be_set` - estimate_minutesの設定
- `test_task_estimate_minutes_can_be_null` - estimate_minutesのnull許容
- `test_task_duration_seconds_default_zero` - duration_secondsのデフォルト値（0）
- `test_get_completed_duration_seconds_single_entry` - 単一完了TimeEntryのduration_seconds計算
- `test_get_completed_duration_seconds_multiple_entries` - 複数完了TimeEntryのduration_seconds合計
- `test_duration_seconds_excludes_ongoing_entries` - 進行中TimeEntryの除外
- `test_get_current_duration_seconds_includes_ongoing` - get_current_duration_secondsが進行中を含むこと
- `test_duration_includes_child_tasks` - 子タスクのTimeEntryが親のdurationに含まれること
- `test_duration_includes_grandchild_tasks` - 孫タスクのTimeEntryが親・ルートのdurationに含まれること
- `test_get_all_ancestors` - get_all_ancestorsメソッドの動作確認

### 2. APIテスト (`tests/api/`)

REST API エンドポイントの機能テスト

**テスト方法**:
- **python-postman** - Postmanコレクションを直接Pythonから実行
- 非同期実行により高速なテスト実行
- 動的な環境変数設定（base_url, auth_token）

**テスト内容**:
- Health Check エンドポイント
- Projects API (GET, POST, PATCH, PUT, DELETE)
- 認証テスト（401エラー確認）

**テストケース数**: 9

#### テストケース詳細

1. **Health Check** (1テスト)
   - `GET /api/health/` - ステータス200、`{"status": "ok"}`

2. **Projects API** (7テスト)
   - `GET /api/projects/` - プロジェクト一覧取得（認証あり）
   - `POST /api/projects/` - プロジェクト作成
   - `GET /api/projects/{id}/` - 特定プロジェクト取得
   - `PATCH /api/projects/{id}/` - プロジェクト部分更新
   - `PUT /api/projects/{id}/` - プロジェクト全体更新
   - `DELETE /api/projects/{id}/` - プロジェクト削除
   - `GET /api/projects/{id}/` (削除後) - 404確認

3. **認証テスト** (1テスト)
   - `GET /api/projects/` (認証なし) - 401エラー確認

#### python-postmanの特徴

- ✅ Postmanコレクションを直接読み込み
- ✅ 環境変数の動的設定
- ✅ フォルダ構造の再帰的処理
- ✅ 非同期リクエスト実行
- ✅ 詳細な実行ログ（リクエスト名、ステータスコード、結果）
- ✅ テスト結果サマリー（Total/Passed/Failed/Skipped）

## テスト実行方法

### すべてのテストを実行

```bash
cd backend
uv run python manage.py test
```

**出力例**:
```
Found 29 test(s).
...
Ran 29 tests in 7.475s

OK
```

### カテゴリ別にテストを実行

#### ユニットテストのみ

```bash
uv run python manage.py test tests.unit
```

#### APIテストのみ

```bash
uv run python manage.py test tests.api
```

#### Postmanコレクションテストのみ

```bash
uv run python manage.py test tests.api.test_postman
```

### 特定のテストクラスを実行

```bash
# タスク階層のテストのみ
uv run python manage.py test tests.unit.test_models.TaskHierarchyTestCase

# Postman APIテストのみ
uv run python manage.py test tests.api.test_postman.PostmanAPITestCase
```

### 特定のテストメソッドを実行

```bash
# 親タスク作成テストのみ
uv run python manage.py test tests.unit.test_models.TaskHierarchyTestCase.test_create_parent_task

# Postmanコレクションテストのみ
uv run python manage.py test tests.api.test_postman.PostmanAPITestCase.test_run_postman_collection
```

### 詳細なログ出力

```bash
# Verbosity レベル 2（詳細）
uv run python manage.py test --verbosity=2

# Verbosity レベル 3（最も詳細）
uv run python manage.py test --verbosity=3
```

## Postman テストについて

### python-postmanを使用したテスト実行

APIテストは`python-postman`パッケージを使用してPostmanコレクションを実行します。

**実装の詳細**:
- `PythonPostman.from_file()` でコレクションを読み込み
- `ExecutionContext` で環境変数を管理
- `RequestExecutor` で非同期リクエスト実行
- Folder型とRequest型を自動判別して再帰的に処理

**実行結果の例**:
```
============================================================
Running Postman Collection: Task Tracking API
============================================================

Running: Health Check
  Status: 200
  Result: PASSED

Folder: Projects

Running: Get All Projects
  Status: 200
  Result: PASSED

Running: Create Project
  Status: 201
  Result: PASSED

...

============================================================
Test Results:
  Total: 9
  Passed: 9
  Failed: 0
  Skipped: 0
============================================================
```

### 認証トークンの取得と設定

Postman環境ファイルの認証トークンを自動的に取得・更新するスクリプトが用意されています。

**スクリプトの場所**: [tests/api/get_auth_token.py](./api/get_auth_token.py)

#### 既存ユーザーのトークンを取得

```bash
cd backend
uv run python tests/api/get_auth_token.py <username>
```

例:
```bash
uv run python tests/api/get_auth_token.py testuser
```

**実行結果**:
```
✅ 既存のトークンを取得しました

============================================================
ユーザー情報
============================================================
ユーザー名: testuser
メール: test@example.com
トークン: 588fc0e9d6ea04acb5a853deccabd6481463db23
============================================================

✅ 環境ファイルを更新しました: tests/api/postman/local.postman_environment.json

📝 Postman環境ファイルの auth_token が更新されました
   ファイル: tests/api/postman/local.postman_environment.json

✅ 完了
```

#### 新しいユーザーを作成してトークンを取得

```bash
uv run python tests/api/get_auth_token.py --create-user <username> <email> <password>
```

例:
```bash
uv run python tests/api/get_auth_token.py --create-user newuser new@example.com password123
```

#### トークンのみ表示（環境ファイルを更新しない）

```bash
uv run python tests/api/get_auth_token.py <username> --no-update
```

#### スクリプトの機能

- ✅ 指定されたユーザーの認証トークンを取得
- ✅ トークンが存在しない場合は自動作成
- ✅ Postman環境ファイル（`local.postman_environment.json`）の`auth_token`を自動更新
- ✅ 新しいユーザーの作成とトークン生成
- ✅ `--no-update`フラグでトークン表示のみ

### Postman コレクションの詳細

Postman コレクションとその使用方法の詳細は以下を参照:

- [tests/api/postman/README.md](./api/postman/README.md) - 詳細なドキュメント
- [tests/api/postman/QUICKSTART.md](./api/postman/QUICKSTART.md) - クイックスタートガイド

## テストデータベース

Django のテストは自動的にテスト用データベースを作成・破棄します:

- **ユニットテスト**: SQLite インメモリDB（高速）
- **APIテスト (LiveServerTestCase)**: テスト用 SQLite DB

設定: `backend/config/settings.py`

```python
if "test" in sys.argv:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
```

## 依存関係

### 必須パッケージ

テストに必要なパッケージは`pyproject.toml`の`dependency-groups`で管理されています:

```toml
[dependency-groups]
dev = [
    "pytest-django>=4.11.1",
    "requests>=2.32.5",
    "python-postman>=0.1.3",
]
```

### インストール

```bash
cd backend
uv sync
```

## カバレッジ測定

テストカバレッジを測定する場合:

```bash
# カバレッジ測定
uv run coverage run --source='.' manage.py test

# レポート表示
uv run coverage report

# HTML レポート生成
uv run coverage html
# htmlcov/index.html を開く
```

## CI/CD での実行

### GitHub Actions の例

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: |
          cd backend
          uv sync

      - name: Run tests
        run: |
          cd backend
          uv run python manage.py test
```

## トラブルシューティング

### テストが失敗する場合

1. **マイグレーションが最新か確認**
   ```bash
   uv run python manage.py makemigrations
   uv run python manage.py migrate
   ```

2. **依存関係を再インストール**
   ```bash
   uv sync
   ```

3. **特定のテストだけ実行して問題を特定**
   ```bash
   uv run python manage.py test tests.unit.test_models.TaskHierarchyTestCase --verbosity=2
   ```

### python-postmanのインポートエラー

`python-postman`がインストールされていない場合:

```bash
cd backend
uv sync
```

### APIテストで401エラーが発生

`test_postman.py`の`PostmanAPITestCase`は`LiveServerTestCase`を使用しており、自動的にテスト用トークンを生成します。

手動でトークンを設定する必要はありません。

## ベストプラクティス

1. **新しい機能を追加する際は、必ずテストも追加する**
   - モデルを追加 → `tests/unit/test_models.py` にテスト追加
   - APIエンドポイントを追加 → Postmanコレクションに追加

2. **テストを先に書く（TDD）**
   - テストを書く → 失敗することを確認 → 実装 → テストが通ることを確認

3. **テストは独立させる**
   - 各テストは他のテストに依存しない
   - `setUp()` でデータを作成、`tearDown()` でクリーンアップ（必要に応じて）

4. **意味のあるテスト名を付ける**
   - `test_create_parent_task` ✅
   - `test_task1` ❌

5. **エッジケースもテストする**
   - 正常系だけでなく、エラーケースもテスト
   - バリデーションエラー、制約違反なども確認

## まとめ

- **29テストケース**が実装済み（ユニット: 20、API: 9）
- **`uv run python manage.py test`** で全テスト実行
- **python-postman**を使用したPostmanコレクションの自動テスト
- **CI/CD対応**（自動化可能）

新しいテストを追加する際は、このREADMEを更新してください。

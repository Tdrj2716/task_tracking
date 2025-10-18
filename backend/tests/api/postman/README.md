# Postman API コレクション

Task Tracking APIのPostmanコレクションです。

## ファイル構成

- `Task_Tracking_API.postman_collection.json` - APIテストコレクション
- `local.postman_environment.json` - ローカル開発環境設定

## 使用方法

### 1. Postmanアプリで使用

#### インポート

1. Postmanアプリを開く
2. 「Import」ボタンをクリック
3. `Task_Tracking_API.postman_collection.json` をドラッグ&ドロップ
4. `local.postman_environment.json` をドラッグ&ドロップ

#### 環境の選択

1. 右上の環境ドロップダウンから「Local Development」を選択
2. 環境変数を確認・編集:
   - `base_url`: `http://localhost:8000`
   - `auth_token`: 認証トークン
   - `test_project_id`: テスト用プロジェクトID（自動設定）

### 2. python-postmanで自動テスト

`python-postman`パッケージを使用してPythonから自動実行できます。

```bash
cd backend
uv run python manage.py test tests.api.test_postman
```

詳細は [tests/README.md](../../README.md) を参照してください。

## 認証トークンの取得と設定

認証トークン取得スクリプトを使用して、環境ファイルを自動更新できます。

```bash
cd backend
uv run python tests/api/get_auth_token.py <username>
```

### 使用例

```bash
# 既存ユーザーのトークンを取得して環境ファイルを更新
uv run python tests/api/get_auth_token.py testuser

# 新しいユーザーを作成してトークンを取得
uv run python tests/api/get_auth_token.py --create-user newuser new@example.com password123

# トークンのみ表示（環境ファイルを更新しない）
uv run python tests/api/get_auth_token.py testuser --no-update
```

詳細は [get_auth_token.py](../get_auth_token.py) のヘルプを参照:

```bash
uv run python tests/api/get_auth_token.py --help
```

## テスト内容

### Health Check (1テスト)

- `GET /api/health/` - ヘルスチェックエンドポイント

### Projects API (7テスト)

- `GET /api/projects/` - プロジェクト一覧取得
- `POST /api/projects/` - プロジェクト作成
- `GET /api/projects/{id}/` - プロジェクト詳細取得
- `PATCH /api/projects/{id}/` - プロジェクト部分更新
- `PUT /api/projects/{id}/` - プロジェクト全体更新
- `DELETE /api/projects/{id}/` - プロジェクト削除
- `GET /api/projects/{id}/` (削除後) - 404確認

### Authentication Tests (1テスト)

- `GET /api/projects/` (認証なし) - 401エラー確認

## 環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|-------------|
| `base_url` | APIのベースURL | `http://localhost:8000` |
| `auth_token` | 認証トークン | (空) |
| `test_project_id` | テスト用プロジェクトID | (空、自動設定) |

## トラブルシューティング

### 401 Unauthorized エラー

認証トークンが設定されていないか、無効です。

**解決方法**:
```bash
uv run python tests/api/get_auth_token.py <username>
```

### サーバーが起動していない

**解決方法**:
```bash
cd backend
uv run python manage.py runserver
```

### テストが失敗する

1. データベースをマイグレート:
```bash
uv run python manage.py migrate
```

2. 新しいユーザーを作成してトークンを取得:
```bash
uv run python tests/api/get_auth_token.py --create-user testuser test@example.com password123
```

3. コレクションを再実行

## コレクションのエクスポート

Postmanアプリで変更を加えた場合、エクスポートしてこのファイルを更新してください。

1. コレクションを右クリック → 「Export」
2. Collection v2.1形式を選択
3. `Task_Tracking_API.postman_collection.json` を上書き

## 関連ドキュメント

- [tests/README.md](../../README.md) - テスト全体のドキュメント
- [get_auth_token.py](../get_auth_token.py) - トークン取得スクリプト

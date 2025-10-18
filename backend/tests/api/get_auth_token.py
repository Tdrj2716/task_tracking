#!/usr/bin/env python
"""
認証トークン取得スクリプト

このスクリプトは、指定されたユーザーの認証トークンを取得し、
Postman環境ファイルに自動的に設定します。

使用方法:
    python tests/api/get_auth_token.py <username>
    python tests/api/get_auth_token.py --create-user <username> <email> <password>

例:
    python tests/api/get_auth_token.py testuser
    python tests/api/get_auth_token.py --create-user newuser new@example.com password123
"""

import argparse
import json
import os
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Django settings module を設定
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Django setup
import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from rest_framework.authtoken.models import Token  # noqa: E402

User = get_user_model()


def get_postman_env_path():
    """Postman環境ファイルのパスを取得"""
    script_dir = Path(__file__).parent
    env_path = script_dir / "postman" / "local.postman_environment.json"
    return env_path


def load_postman_env(env_path):
    """Postman環境ファイルを読み込む"""
    if not env_path.exists():
        print(f"⚠️  環境ファイルが見つかりません: {env_path}")
        print("📝 新しい環境ファイルを作成します...")
        return create_default_env()

    with open(env_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_default_env():
    """デフォルトのPostman環境ファイルを作成"""
    return {
        "id": "local-environment",
        "name": "Local Development",
        "values": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "default",
                "enabled": True
            },
            {
                "key": "auth_token",
                "value": "",
                "type": "secret",
                "enabled": True
            },
            {
                "key": "test_project_id",
                "value": "",
                "type": "default",
                "enabled": True
            }
        ],
        "_postman_variable_scope": "environment"
    }


def save_postman_env(env_path, env_data):
    """Postman環境ファイルを保存"""
    # ディレクトリが存在しない場合は作成
    env_path.parent.mkdir(parents=True, exist_ok=True)

    with open(env_path, "w", encoding="utf-8") as f:
        json.dump(env_data, f, indent="\t", ensure_ascii=False)
    print(f"✅ 環境ファイルを更新しました: {env_path}")


def update_env_variable(env_data, key, value):
    """環境変数を更新"""
    for variable in env_data.get("values", []):
        if variable.get("key") == key:
            variable["value"] = value
            return True
    return False


def get_or_create_token(username):
    """ユーザーのトークンを取得または作成"""
    try:
        user = User.objects.get(username=username)
        token, created = Token.objects.get_or_create(user=user)

        if created:
            print("✅ 新しいトークンを作成しました")
        else:
            print("✅ 既存のトークンを取得しました")

        return token.key, user

    except User.DoesNotExist:
        print(f"❌ エラー: ユーザー '{username}' が見つかりません")
        print("\nユーザーを作成する場合:")
        print(
            f"  python tests/api/get_auth_token.py --create-user {username} <email> <password>"
        )
        sys.exit(1)


def create_user(username, email, password):
    """新しいユーザーを作成"""
    if User.objects.filter(username=username).exists():
        print(f"⚠️  ユーザー '{username}' は既に存在します")
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        print(f"✅ 新しいユーザーを作成しました: {username}")

    token, created = Token.objects.get_or_create(user=user)
    if created:
        print("✅ トークンを作成しました")
    else:
        print("✅ 既存のトークンを使用します")

    return token.key, user


def main():
    parser = argparse.ArgumentParser(
        description="認証トークンを取得してPostman環境ファイルに設定します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 既存ユーザーのトークンを取得
  python tests/api/get_auth_token.py testuser

  # 新しいユーザーを作成してトークンを取得
  python tests/api/get_auth_token.py --create-user newuser new@example.com password123

  # トークンのみ表示（環境ファイルを更新しない）
  python tests/api/get_auth_token.py testuser --no-update
        """,
    )

    parser.add_argument("username", nargs="?", help="トークンを取得するユーザー名")

    parser.add_argument(
        "--create-user",
        nargs=3,
        metavar=("USERNAME", "EMAIL", "PASSWORD"),
        help="新しいユーザーを作成してトークンを取得",
    )

    parser.add_argument(
        "--no-update",
        action="store_true",
        help="環境ファイルを更新せず、トークンのみ表示",
    )

    args = parser.parse_args()

    # 引数チェック
    if args.create_user:
        username, email, password = args.create_user
        token_key, user = create_user(username, email, password)
    elif args.username:
        username = args.username
        token_key, user = get_or_create_token(username)
    else:
        parser.print_help()
        sys.exit(1)

    # トークン情報を表示
    print(f"\n{'=' * 60}")
    print("ユーザー情報")
    print(f"{'=' * 60}")
    print(f"ユーザー名: {user.username}")
    print(f"メール: {user.email}")
    print(f"トークン: {token_key}")
    print(f"{'=' * 60}\n")

    # 環境ファイルを更新
    if not args.no_update:
        try:
            env_path = get_postman_env_path()
            env_data = load_postman_env(env_path)

            # auth_token を更新
            if update_env_variable(env_data, "auth_token", token_key):
                save_postman_env(env_path, env_data)
                print("\n📝 Postman環境ファイルの auth_token が更新されました")
                print(f"   ファイル: {env_path.relative_to(Path.cwd())}")
            else:
                print("⚠️  警告: 環境ファイルに auth_token が見つかりませんでした")

        except Exception as e:
            print(f"❌ エラー: {e}")
            sys.exit(1)
    else:
        print("ℹ️  --no-update が指定されているため、環境ファイルは更新されません")

    print("\n✅ 完了")


if __name__ == "__main__":
    main()

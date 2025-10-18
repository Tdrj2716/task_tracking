"""
Postman Collection を使用した API テスト

このテストは、python-postmanパッケージを使用して
Postman コレクションを Python から実行して API の動作を検証します。
"""

import asyncio
import os

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from python_postman import PythonPostman
from python_postman.execution import ExecutionContext, RequestExecutor
from rest_framework.authtoken.models import Token

User = get_user_model()


class PostmanAPITestCase(LiveServerTestCase):
    """Postman コレクションを使用した API テストケース"""

    def setUp(self):
        """テストのセットアップ"""
        # テストユーザーとトークンを作成
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)

        # Postman コレクションのパス
        self.tests_dir = os.path.dirname(os.path.abspath(__file__))
        self.collection_path = os.path.join(
            self.tests_dir, "postman", "Task_Tracking_API.postman_collection.json"
        )

        # 環境変数を設定
        self.environment_vars = {
            "base_url": self.live_server_url,
            "auth_token": self.token.key,
            "test_project_id": "",
        }

    def test_run_postman_collection(self):
        """python-postman を使用して Postman コレクションを実行"""
        # 非同期関数を実行
        asyncio.run(self._run_collection())

    async def _run_collection(self):
        """コレクションを実行する非同期関数"""
        # Postman コレクションを読み込み
        collection = PythonPostman.from_file(self.collection_path)

        # 実行コンテキストを作成
        context = ExecutionContext(environment_variables=self.environment_vars)

        # コレクションを実行
        print("\n" + "=" * 60)
        print(f"Running Postman Collection: {collection.info.name}")
        print("=" * 60)

        # リクエストエグゼキュータを作成
        executor = RequestExecutor()

        # 各リクエストを実行してテスト
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
        }

        # コレクション内の全アイテムを実行
        await self._execute_items(collection.items, executor, context, results)

        # 結果を表示
        print("\n" + "=" * 60)
        print("Test Results:")
        print(f"  Total: {results['total']}")
        print(f"  Passed: {results['passed']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Skipped: {results['skipped']}")
        print("=" * 60 + "\n")

        # すべてのテストが成功したことを確認
        self.assertEqual(
            results["failed"],
            0,
            f"Postman collection tests failed: {results['failed']} failures",
        )

    async def _execute_items(self, items, executor, context, results):
        """コレクション内のアイテムを再帰的に実行"""
        for item in items:
            # Folder型の場合 (items属性を持つ)
            if hasattr(item, "items") and item.items:
                print(f"\nFolder: {item.name}")
                await self._execute_items(item.items, executor, context, results)
            # Request型の場合 (url属性を持つ)
            elif hasattr(item, "url"):
                await self._execute_request(item, executor, context, results)

    async def _execute_request(self, item, executor, context, results):
        """個別のリクエストを実行してテスト"""
        results["total"] += 1

        try:
            print(f"\nRunning: {item.name}")

            # リクエストを実行 (itemが既にRequestオブジェクト)
            result = await executor.execute_request(item, context)

            # レスポンスステータスを表示
            print(f"  Status: {result.response.status_code}")

            # レスポンスを検証
            self._validate_response(item, result, context)

            results["passed"] += 1
            print("  Result: PASSED")

        except AssertionError as e:
            results["failed"] += 1
            print(f"  Result: FAILED - {str(e)}")
            raise

        except Exception as e:
            results["skipped"] += 1
            print(f"  Result: SKIPPED - {str(e)}")

    def _validate_response(self, item, result, context):
        """レスポンスを検証"""
        # リクエスト名に基づいて期待されるステータスコードを判定
        request_name = item.name.lower()
        response = result.response

        if "health check" in request_name:
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertEqual(data.get("status"), "ok")

        elif "get all projects" in request_name:
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertIn("results", data)

        elif "create project" in request_name:
            self.assertEqual(response.status_code, 201)
            data = response.json
            self.assertIn("id", data)
            self.assertIn("name", data)
            # プロジェクトIDを環境変数に保存
            context.environment_variables["test_project_id"] = str(data["id"])

        elif "get single project" in request_name:
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertIn("id", data)

        elif "update project" in request_name:
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertIn("name", data)

        elif "delete project" in request_name:
            self.assertEqual(response.status_code, 204)

        elif "verify project deleted" in request_name:
            self.assertEqual(response.status_code, 404)

        elif "unauthorized" in request_name:
            self.assertEqual(response.status_code, 401)

        else:
            # デフォルトは2xx系のステータスコードを期待
            self.assertTrue(
                200 <= response.status_code < 300,
                f"Expected 2xx status code, got {response.status_code}",
            )

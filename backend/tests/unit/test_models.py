"""
Phase 1 Backend 基本動作確認テスト

このテストファイルは Task 7 の実施内容をカバーします：
1. タスク階層構造（親・子・孫）の動作確認
2. 3階層制限のバリデーション確認
3. カスケード削除の動作確認
4. TimeEntry の duration_seconds 自動計算確認
5. データベース制約の確認
"""

from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from api.models import Project, Tag, Task, TimeEntry

User = get_user_model()


class TaskHierarchyTestCase(TestCase):
    """タスク階層構造のテストケース"""

    def setUp(self):
        """テスト用のユーザーとプロジェクトを作成"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.project = Project.objects.create(
            user=self.user, name="テストプロジェクト", color="#FF0000"
        )

    def test_create_parent_task(self):
        """親タスク（Level 0）の作成テスト"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )

        self.assertEqual(parent.level, 0)
        self.assertIsNone(parent.parent)
        self.assertIsNone(parent.root)
        self.assertEqual(parent.project, self.project)

    def test_create_child_task(self):
        """子タスク（Level 1）の作成テスト"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)

        self.assertEqual(child.level, 1)
        self.assertEqual(child.parent, parent)
        self.assertEqual(child.root, parent)
        # プロジェクトが親から継承されることを確認
        self.assertEqual(child.project, self.project)

    def test_create_grandchild_task(self):
        """孫タスク（Level 2）の作成テスト"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        self.assertEqual(grandchild.level, 2)
        self.assertEqual(grandchild.parent, child)
        self.assertEqual(grandchild.root, parent)
        # プロジェクトがルートから継承されることを確認
        self.assertEqual(grandchild.project, self.project)

    def test_project_inheritance_from_root(self):
        """プロジェクトがルートタスクから子孫タスクに継承されることを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        # すべてのタスクが同じプロジェクトを持つことを確認
        self.assertEqual(parent.project, self.project)
        self.assertEqual(child.project, self.project)
        self.assertEqual(grandchild.project, self.project)

    def test_project_update_propagation(self):
        """ルートタスクのプロジェクト変更が子孫タスクに伝播することを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        # 新しいプロジェクトを作成
        new_project = Project.objects.create(
            user=self.user, name="新プロジェクト", color="#00FF00"
        )

        # 親タスクのプロジェクトを変更
        parent.project = new_project
        parent.save()

        # 子孫タスクをリフレッシュ
        child.refresh_from_db()
        grandchild.refresh_from_db()

        # すべてのタスクが新しいプロジェクトを持つことを確認
        self.assertEqual(parent.project, new_project)
        self.assertEqual(child.project, new_project)
        self.assertEqual(grandchild.project, new_project)

    def test_task_with_null_project(self):
        """プロジェクトが null のタスクを作成できることを確認"""
        task = Task.objects.create(user=self.user, name="Inbox タスク", project=None)

        self.assertIsNone(task.project)
        self.assertEqual(task.level, 0)


class TaskHierarchyValidationTestCase(TestCase):
    """タスク階層の3階層制限のバリデーションテスト"""

    def setUp(self):
        """テスト用のユーザーとプロジェクトを作成"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.project = Project.objects.create(
            user=self.user, name="テストプロジェクト"
        )

    def test_cannot_create_great_grandchild_task(self):
        """ひ孫タスク（Level 3）の作成が拒否されることを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        # ひ孫タスクの作成を試みる
        with self.assertRaises(ValidationError) as context:
            Task.objects.create(user=self.user, name="ひ孫タスク", parent=grandchild)

        self.assertIn("タスクの階層は最大3レベル", str(context.exception))

    def test_grandchild_cannot_have_children(self):
        """孫タスクが子を持てないことを確認（clean() メソッドのテスト）"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        # 孫タスクに子を追加しようとする
        great_grandchild = Task(
            user=self.user, name="ひ孫タスク", parent=grandchild
        )

        with self.assertRaises(ValidationError) as context:
            great_grandchild.clean()

        self.assertIn("孫タスクは子タスクを持てません", str(context.exception))


class TaskCascadeDeleteTestCase(TestCase):
    """タスクのカスケード削除テスト"""

    def setUp(self):
        """テスト用のユーザーとプロジェクトを作成"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.project = Project.objects.create(
            user=self.user, name="テストプロジェクト"
        )

    def test_delete_parent_deletes_children(self):
        """親タスクの削除で子タスクも削除されることを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)

        parent_id = parent.id
        child_id = child.id

        # 親タスクを削除
        parent.delete()

        # 親と子の両方が削除されていることを確認
        self.assertFalse(Task.objects.filter(id=parent_id).exists())
        self.assertFalse(Task.objects.filter(id=child_id).exists())

    def test_delete_parent_deletes_all_descendants(self):
        """親タスクの削除で子孫タスクすべてが削除されることを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        parent_id = parent.id
        child_id = child.id
        grandchild_id = grandchild.id

        # 親タスクを削除
        parent.delete()

        # 親、子、孫すべてが削除されていることを確認
        self.assertFalse(Task.objects.filter(id=parent_id).exists())
        self.assertFalse(Task.objects.filter(id=child_id).exists())
        self.assertFalse(Task.objects.filter(id=grandchild_id).exists())


class TimeEntryTestCase(TestCase):
    """TimeEntry モデルのテスト"""

    def setUp(self):
        """テスト用のユーザーとタスクを作成"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.project = Project.objects.create(
            user=self.user, name="テストプロジェクト"
        )
        self.task = Task.objects.create(
            user=self.user, name="テストタスク", project=self.project
        )

    def test_duration_seconds_auto_calculation(self):
        """duration_seconds が start_time と end_time から自動計算されることを確認"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=2, minutes=30, seconds=45)

        entry = TimeEntry.objects.create(
            user=self.user, task=self.task, start_time=start_time, end_time=end_time
        )

        expected_seconds = 2 * 3600 + 30 * 60 + 45  # 9045 seconds
        self.assertEqual(entry.duration_seconds, expected_seconds)

    def test_duration_seconds_null_when_end_time_null(self):
        """end_time が null の場合、duration_seconds も null になることを確認"""
        start_time = timezone.now()

        entry = TimeEntry.objects.create(
            user=self.user, task=self.task, start_time=start_time, end_time=None
        )

        self.assertIsNone(entry.duration_seconds)

    def test_name_and_project_auto_set_from_task(self):
        """name と project がタスクから自動設定されることを確認"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        entry = TimeEntry.objects.create(
            user=self.user, task=self.task, start_time=start_time, end_time=end_time
        )

        self.assertEqual(entry.name, self.task.name)
        self.assertEqual(entry.project, self.task.project)

    def test_task_delete_sets_null(self):
        """タスク削除時、TimeEntry の task フィールドが NULL になることを確認"""
        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        entry = TimeEntry.objects.create(
            user=self.user, task=self.task, start_time=start_time, end_time=end_time
        )

        self.task.delete()

        entry.refresh_from_db()

        # task フィールドが NULL になっていることを確認
        self.assertIsNone(entry.task)
        self.assertIsNone(entry.task_id)


class DatabaseConstraintTestCase(TestCase):
    """データベース制約のテスト"""

    def setUp(self):
        """テスト用のユーザーを作成"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

    def test_unique_tag_name_per_user(self):
        """ユーザーごとにタグ名がユニークであることを確認"""
        Tag.objects.create(user=self.user, name="重要")

        # 同じユーザーで同じ名前のタグを作成しようとするとエラー
        with self.assertRaises(IntegrityError):
            Tag.objects.create(user=self.user, name="重要")

    def test_different_users_can_have_same_tag_name(self):
        """異なるユーザーは同じタグ名を持てることを確認"""
        tag1 = Tag.objects.create(user=self.user, name="重要")
        tag2 = Tag.objects.create(user=self.user2, name="重要")

        self.assertNotEqual(tag1.id, tag2.id)
        self.assertEqual(tag1.name, tag2.name)

    def test_task_level_check_constraint(self):
        """タスクの level が 2 以下であることを確認（CHECK 制約）"""
        project = Project.objects.create(user=self.user, name="テストプロジェクト")
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        # level が自動的に設定されていることを確認
        self.assertEqual(parent.level, 0)
        self.assertEqual(child.level, 1)
        self.assertEqual(grandchild.level, 2)

        # level が 2 を超えるタスクは作成できない（save() で ValidationError）
        with self.assertRaises(ValidationError):
            Task.objects.create(user=self.user, name="ひ孫タスク", parent=grandchild)

    def test_project_delete_sets_task_project_null(self):
        """プロジェクト削除時、関連タスクの project フィールドが NULL になることを確認"""
        project = Project.objects.create(user=self.user, name="テストプロジェクト")
        task = Task.objects.create(user=self.user, name="タスク", project=project)

        project.delete()

        task.refresh_from_db()

        # project フィールドが NULL になっていることを確認
        self.assertIsNone(task.project)
        self.assertIsNone(task.project_id)


class TaskDurationTrackingTestCase(TestCase):
    """Task の estimate_minutes と duration_seconds のテスト"""

    def setUp(self):
        """テスト用のユーザーとプロジェクトを作成"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.project = Project.objects.create(
            user=self.user, name="テストプロジェクト"
        )

    def test_task_estimate_minutes_can_be_set(self):
        """タスクに estimate_minutes を設定できることを確認"""
        task = Task.objects.create(
            user=self.user,
            name="見積もりありタスク",
            project=self.project,
            estimate_minutes=120,
        )

        self.assertEqual(task.estimate_minutes, 120)

    def test_task_estimate_minutes_can_be_null(self):
        """タスクの estimate_minutes が null 許容であることを確認"""
        task = Task.objects.create(
            user=self.user, name="見積もりなしタスク", project=self.project
        )

        self.assertIsNone(task.estimate_minutes)

    def test_task_duration_seconds_default_zero(self):
        """タスクの duration_seconds がデフォルトで 0 であることを確認"""
        task = Task.objects.create(
            user=self.user, name="新規タスク", project=self.project
        )

        self.assertEqual(task.duration_seconds, 0)

    def test_get_completed_duration_seconds_single_entry(self):
        """単一の完了した TimeEntry の duration_seconds が計算されることを確認"""
        task = Task.objects.create(
            user=self.user, name="タスク", project=self.project
        )

        start_time = timezone.now()
        end_time = start_time + timedelta(hours=1)

        TimeEntry.objects.create(
            user=self.user, task=task, start_time=start_time, end_time=end_time
        )

        # TimeEntry 保存時に task.duration_seconds が更新される
        task.refresh_from_db()
        self.assertEqual(task.duration_seconds, 3600)

    def test_get_completed_duration_seconds_multiple_entries(self):
        """複数の完了した TimeEntry の duration_seconds が合計されることを確認"""
        task = Task.objects.create(
            user=self.user, name="タスク", project=self.project
        )

        start_time = timezone.now()

        # 1時間のエントリ
        TimeEntry.objects.create(
            user=self.user,
            task=task,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
        )

        # 30分のエントリ
        TimeEntry.objects.create(
            user=self.user,
            task=task,
            start_time=start_time + timedelta(hours=2),
            end_time=start_time + timedelta(hours=2, minutes=30),
        )

        task.refresh_from_db()
        expected_seconds = 3600 + 1800  # 1時間 + 30分
        self.assertEqual(task.duration_seconds, expected_seconds)

    def test_duration_seconds_excludes_ongoing_entries(self):
        """進行中の TimeEntry は duration_seconds に含まれないことを確認"""
        task = Task.objects.create(
            user=self.user, name="タスク", project=self.project
        )

        start_time = timezone.now()

        # 完了したエントリ
        TimeEntry.objects.create(
            user=self.user,
            task=task,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
        )

        # 進行中のエントリ (end_time が null)
        TimeEntry.objects.create(
            user=self.user, task=task, start_time=start_time + timedelta(hours=2)
        )

        task.refresh_from_db()
        # 完了した1時間のみがカウントされる
        self.assertEqual(task.duration_seconds, 3600)

    def test_get_current_duration_seconds_includes_ongoing(self):
        """get_current_duration_seconds が進行中のエントリを含むことを確認"""
        task = Task.objects.create(
            user=self.user, name="タスク", project=self.project
        )

        start_time = timezone.now() - timedelta(hours=2)

        # 完了したエントリ
        TimeEntry.objects.create(
            user=self.user,
            task=task,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
        )

        # 進行中のエントリ (1時間前に開始)
        ongoing_start = timezone.now() - timedelta(hours=1)
        TimeEntry.objects.create(user=self.user, task=task, start_time=ongoing_start)

        task.refresh_from_db()
        current_duration = task.get_current_duration_seconds()

        # 完了分(3600秒) + 進行中(約3600秒)
        # 進行中の時間は厳密ではないため、範囲でチェック
        self.assertGreaterEqual(current_duration, 7000)  # 少なくとも約2時間
        self.assertLessEqual(current_duration, 7400)  # 最大約2時間6分

    def test_duration_includes_child_tasks(self):
        """子タスクの TimeEntry も親タスクの duration に含まれることを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)

        start_time = timezone.now()

        # 親タスクに1時間
        TimeEntry.objects.create(
            user=self.user,
            task=parent,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
        )

        # 子タスクに30分
        TimeEntry.objects.create(
            user=self.user,
            task=child,
            start_time=start_time + timedelta(hours=2),
            end_time=start_time + timedelta(hours=2, minutes=30),
        )

        parent.refresh_from_db()
        child.refresh_from_db()

        # 子タスクは自分の30分のみ
        self.assertEqual(child.duration_seconds, 1800)

        # 親タスクは子タスクの分も含む
        expected_parent_seconds = 3600 + 1800  # 1時間 + 30分
        self.assertEqual(parent.duration_seconds, expected_parent_seconds)

    def test_duration_includes_grandchild_tasks(self):
        """孫タスクの TimeEntry も親・ルートタスクの duration に含まれることを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        start_time = timezone.now()

        # 親タスクに1時間
        TimeEntry.objects.create(
            user=self.user,
            task=parent,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
        )

        # 子タスクに30分
        TimeEntry.objects.create(
            user=self.user,
            task=child,
            start_time=start_time + timedelta(hours=2),
            end_time=start_time + timedelta(hours=2, minutes=30),
        )

        # 孫タスクに15分
        TimeEntry.objects.create(
            user=self.user,
            task=grandchild,
            start_time=start_time + timedelta(hours=3),
            end_time=start_time + timedelta(hours=3, minutes=15),
        )

        parent.refresh_from_db()
        child.refresh_from_db()
        grandchild.refresh_from_db()

        # 孫タスクは自分の15分のみ
        self.assertEqual(grandchild.duration_seconds, 900)

        # 子タスクは自分の30分 + 孫の15分
        self.assertEqual(child.duration_seconds, 1800 + 900)

        # 親タスクはすべての合計
        expected_parent_seconds = 3600 + 1800 + 900  # 1時間 + 30分 + 15分
        self.assertEqual(parent.duration_seconds, expected_parent_seconds)

    def test_get_all_ancestors(self):
        """get_all_ancestors が先祖タスクをすべて返すことを確認"""
        parent = Task.objects.create(
            user=self.user, name="親タスク", project=self.project
        )
        child = Task.objects.create(user=self.user, name="子タスク", parent=parent)
        grandchild = Task.objects.create(
            user=self.user, name="孫タスク", parent=child
        )

        # 孫タスクの先祖は [子, 親]
        ancestors = grandchild.get_all_ancestors()
        self.assertEqual(len(ancestors), 2)
        self.assertEqual(ancestors[0], child)
        self.assertEqual(ancestors[1], parent)

        # 子タスクの先祖は [親]
        ancestors = child.get_all_ancestors()
        self.assertEqual(len(ancestors), 1)
        self.assertEqual(ancestors[0], parent)

        # 親タスクの先祖は []
        ancestors = parent.get_all_ancestors()
        self.assertEqual(len(ancestors), 0)

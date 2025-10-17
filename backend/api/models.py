from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending AbstractUser
    """

    pass


class Project(models.Model):
    """
    Project model for organizing tasks
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#B29632")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tag model for categorizing tasks
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"], name="unique_tag_name_per_user"
            )
        ]

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Task model supporting hierarchical structure (parent-child-grandchild)
    Maximum depth: 3 levels (level 0: parent, level 1: child, level 2: grandchild)

    Key fields:
    - parent: Direct parent task (null for root tasks)
    - root: Root task of the hierarchy (null for root tasks)
    - level: Hierarchy level (0=parent, 1=child, 2=grandchild)
    - project: Project association (user-settable for root tasks only, auto-inherited for children)
    - estimate_minutes: Estimated work time in minutes (user-settable)
    - duration_seconds: Actual completed work time in seconds (auto-calculated from completed TimeEntries)
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Project (user-settable for root tasks, auto-inherited for children)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="tasks"
    )

    # Hierarchy fields
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    root = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="all_descendants",
        editable=False,
    )

    level = models.PositiveSmallIntegerField(default=0, editable=False)

    # Time tracking fields
    estimate_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="タスクの見積もり作業時間(分)",
    )

    duration_seconds = models.IntegerField(
        default=0,
        editable=False,
        help_text="実際の累計作業時間(秒) - 完了したTime Entryの合計",
    )

    tags = models.ManyToManyField(Tag, related_name="tasks", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["user", "project"]),
            models.Index(fields=["parent"]),
            models.Index(fields=["root", "level"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(level__lte=2), name="task_max_level_2"
            )
        ]

    def __str__(self):
        indent = "  " * self.level
        return f"{indent}{self.name}"

    def get_all_descendants(self):
        """全ての子孫タスク（子+孫）"""
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.children.all())
        return descendants

    def get_all_ancestors(self):
        """全ての先祖タスク（parent, grandparent）をリストで返す"""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return ancestors

    def get_completed_duration_seconds(self):
        """
        完了したTime Entryの累計時間(秒)を取得
        自タスク + 子孫タスクのTime Entryの合計
        """
        # 自タスク + 子孫タスクのIDリスト
        task_ids = [self.id]
        task_ids.extend([d.id for d in self.get_all_descendants()])

        # 完了したTime Entryの合計
        result = TimeEntry.objects.filter(
            task_id__in=task_ids, end_time__isnull=False  # 完了したもののみ
        ).aggregate(total=models.Sum("duration_seconds"))
        return result["total"] or 0

    def get_current_duration_seconds(self):
        """
        進行中のTime Entryを含む現在の累計時間(秒)
        完了分(duration_seconds) + 進行中のエントリの経過時間
        """
        from django.utils import timezone

        completed = self.duration_seconds

        # 自タスク + 子孫タスクのIDリスト
        task_ids = [self.id]
        task_ids.extend([d.id for d in self.get_all_descendants()])

        # 進行中のエントリを取得
        ongoing_entries = TimeEntry.objects.filter(
            task_id__in=task_ids, end_time__isnull=True
        )

        ongoing_duration = 0
        now = timezone.now()
        for entry in ongoing_entries:
            delta = now - entry.start_time
            ongoing_duration += int(delta.total_seconds())

        return completed + ongoing_duration

    def clean(self):
        """モデルレベルのバリデーション"""
        super().clean()

        # Projectがuserに紐づいているかチェック
        if self.project and self.project.user_id != self.user_id:
            raise ValidationError(
                {"project": "選択されたプロジェクトはこのユーザーに紐づいていません"}
            )

        # 親がuserに紐づいているかチェック
        if self.parent and self.parent.user_id != self.user_id:
            raise ValidationError(
                {"parent": "選択された親タスクはこのユーザーに紐づいていません"}
            )

        if self.parent:
            # 親が孫タスクの場合はエラー
            if self.parent.level >= 2:
                raise ValidationError({"parent": "孫タスクは子タスクを持てません"})

            # 親と異なるプロジェクトが設定されている場合は警告
            if self.project_id and self.parent.root:
                expected_project = self.parent.root.project_id
                if expected_project and self.project_id != expected_project:
                    raise ValidationError(
                        {
                            "project": "サブタスクのプロジェクトはルートタスクから自動的に設定されます"
                        }
                    )

    def save(self, *args, **kwargs):
        """
        Override save to automatically set level, root, and project
        Also propagate project changes to all descendant tasks
        """
        # 親が設定されている場合
        if self.parent:
            # レベルを計算
            self.level = self.parent.level + 1

            # 最大深度チェック
            if self.level > 2:
                raise ValidationError("タスクの階層は最大3レベル（親、子、孫）までです")

            # ルートタスクを設定
            self.root = self.parent.root if self.parent.root else self.parent

            # プロジェクトをルートから継承（ユーザー設定を上書き）
            self.project = self.root.project

            # 循環参照チェック
            self._check_circular_reference()
        else:
            # ルートタスクの場合
            self.level = 0
            self.root = None
            # projectはユーザーが設定したものを使用

        super().save(*args, **kwargs)

        # 子孫タスクのプロジェクトも更新（ルートタスクのみ）
        if self.pk and self.level == 0:
            self._update_descendants_project()

    def _check_circular_reference(self):
        """循環参照を防ぐ"""
        if not self.pk:
            return

        current = self.parent
        visited = {self.pk}

        while current:
            if current.pk in visited:
                raise ValidationError("循環参照が検出されました")
            visited.add(current.pk)
            current = current.parent

    def _update_descendants_project(self):
        """全ての子孫タスクのプロジェクトを更新"""
        descendants = self.get_all_descendants()
        for descendant in descendants:
            descendant.project = self.project
            descendant.save(update_fields=["project", "updated_at"])


class TimeEntry(models.Model):
    """
    Time entry model for tracking time spent on tasks
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="time_entries"
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_entries",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(editable=False, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["user", "start_time"]),
            models.Index(fields=["user", "task", "start_time"]),
        ]

    def __str__(self):
        task_name = self.name if self.name else "Untitle"
        if self.duration_seconds is None:
            return f"{task_name} - ongoing"

        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{task_name} - {hours:02d}:{minutes:02d}:{seconds:02d}"

    def clean(self):
        """モデルレベルのバリデーション"""
        super().clean()

        # Taskがuserに紐づいているかチェック
        if self.task and self.task.user_id != self.user_id:
            raise ValidationError(
                {"task": "選択されたタスクはこのユーザーに紐づいていません"}
            )

        # Projectがuserに紐づいているかチェック
        if self.project and self.project.user_id != self.user_id:
            raise ValidationError(
                {"project": "選択されたプロジェクトはこのユーザーに紐づいていません"}
            )

    def save(self, *args, **kwargs):
        """
        Override save to automatically calculate duration_seconds
        """
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_seconds = int(delta.total_seconds())
        else:
            self.duration_seconds = None

        if self.task:
            self.project = self.task.project
            self.name = self.task.name

        super().save(*args, **kwargs)

        # Time Entryが完了した場合、関連Taskのduration_secondsを更新
        if self.task and self.end_time:
            self._update_task_duration()

    def _update_task_duration(self):
        """
        関連Taskとその先祖タスクのduration_secondsを更新
        完了したTime Entryの合計を再計算して保存
        """
        # 直接のタスクを更新
        self.task.duration_seconds = self.task.get_completed_duration_seconds()
        self.task.save(update_fields=["duration_seconds", "updated_at"])

        # 先祖タスク全体も更新
        for ancestor in self.task.get_all_ancestors():
            ancestor.duration_seconds = ancestor.get_completed_duration_seconds()
            ancestor.save(update_fields=["duration_seconds", "updated_at"])

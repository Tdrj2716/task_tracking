from rest_framework import serializers

from .models import Project, Tag, Task


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model
    """

    class Meta:
        model = Project
        fields = ["id", "name", "color", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        """
        Validate that name is not empty and doesn't exceed max length
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model
    """

    class Meta:
        model = Tag
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        """
        Validate that name is not empty and doesn't exceed max length
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Tag name cannot be empty.")
        return value

    def validate(self, data):
        """
        Validate that tag name is unique per user
        """
        user = self.context["request"].user
        name = data.get("name")

        # Check for duplicate tag name (excluding current instance for updates)
        queryset = Tag.objects.filter(user=user, name=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                {"name": "A tag with this name already exists."}
            )

        return data


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model
    """

    project_name = serializers.CharField(source="project.name", read_only=True)
    parent_name = serializers.CharField(source="parent.name", read_only=True)
    tag_names = serializers.SerializerMethodField(read_only=True)

    # PrimaryKeyRelatedFieldでquerysetを指定する必要はない（get_queryset_for_fieldで動的に取得）
    # ただし、バリデーションを簡単にするため明示的にqueryset指定
    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "project",
            "project_name",
            "parent",
            "parent_name",
            "tags",
            "tag_names",
            "level",
            "root",
            "estimate_minutes",
            "duration_seconds",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "level",
            "root",
            "duration_seconds",
            "created_at",
            "updated_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # リクエストコンテキストからユーザーを取得してquerysetをフィルタリング
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            # project, parent, tagsをユーザーでフィルタリング
            self.fields["project"].queryset = Project.objects.filter(user=user)
            self.fields["parent"].queryset = Task.objects.filter(user=user)
            self.fields["tags"].queryset = Tag.objects.filter(user=user)

    def get_tag_names(self, obj):
        """タグ名のリストを取得"""
        return [tag.name for tag in obj.tags.all()]

    def validate_name(self, value):
        """
        Validate that name is not empty and doesn't exceed max length
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Task name cannot be empty.")
        return value

    def validate(self, data):
        """
        Validate task hierarchy and relationships
        """
        user = self.context["request"].user
        parent = data.get("parent")
        project = data.get("project")

        # 親タスクがユーザーに紐づいているかチェック
        if parent:
            # parentは既にモデルインスタンスとして渡される（PrimaryKeyRelatedField）
            if parent.user_id != user.id:
                raise serializers.ValidationError(
                    {"parent": "選択された親タスクはこのユーザーに紐づいていません"}
                )

            # 親が孫タスク（level >= 2）の場合はエラー
            if parent.level >= 2:
                raise serializers.ValidationError(
                    {"parent": "孫タスクは子タスクを持てません（最大3階層まで）"}
                )

        # プロジェクトがユーザーに紐づいているかチェック
        if project:
            # projectは既にモデルインスタンスとして渡される（PrimaryKeyRelatedField）
            if project.user_id != user.id:
                raise serializers.ValidationError(
                    {"project": "選択されたプロジェクトはこのユーザーに紐づいていません"}
                )

        return data

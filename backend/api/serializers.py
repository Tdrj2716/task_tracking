from rest_framework import serializers

from .models import Project, Tag


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

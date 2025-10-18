from rest_framework import serializers

from .models import Project


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

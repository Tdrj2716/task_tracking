from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Project, Tag, Task
from .serializers import ProjectSerializer, TagSerializer, TaskSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def unauthorized_test(request):
    """
    Test endpoint to verify authentication is working.
    This should return 401 for unauthenticated requests.
    """
    return Response(
        {"message": "You are authenticated!", "user": request.user.email},
        status=status.HTTP_200_OK,
    )


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations
    """

    serializer_class = ProjectSerializer

    def get_queryset(self):
        """
        Filter projects by the current user
        """
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically set the user when creating a project
        """
        serializer.save(user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Tag CRUD operations
    """

    serializer_class = TagSerializer

    def get_queryset(self):
        """
        Filter tags by the current user
        """
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Automatically set the user when creating a tag
        """
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations
    """

    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["project", "parent", "tags"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Filter tasks by the current user with optimized queries
        """
        return (
            Task.objects.filter(user=self.request.user)
            .select_related("project", "parent", "root")
            .prefetch_related("tags")
        )

    def perform_create(self, serializer):
        """
        Automatically set the user when creating a task
        """
        serializer.save(user=self.request.user)

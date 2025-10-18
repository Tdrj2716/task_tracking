from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Project
from .serializers import ProjectSerializer


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

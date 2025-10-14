from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


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

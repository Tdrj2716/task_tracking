from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"projects", views.ProjectViewSet, basename="project")
router.register(r"tags", views.TagViewSet, basename="tag")

urlpatterns = [
    path("health/", views.health, name="health"),
    path("", include(router.urls)),
]

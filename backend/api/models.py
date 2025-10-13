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
    Maximum depth: 3 levels (parent, child, grandchild)
    """

    HIERARCHY_CHOICES = [
        ("parent", "Parent"),
        ("child", "Child"),
        ("grandchild", "Grandchild"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=100)
    hierarchy = models.CharField(
        max_length=20, choices=HIERARCHY_CHOICES, default="parent"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
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
        ]

    def __str__(self):
        hierarchy_indent = {"parent": "", "child": "  ", "grandchild": "    "}
        return f"{hierarchy_indent.get(self.hierarchy, '')}{self.name}"

    def clean(self):
        """
        Validate hierarchy based on parent's hierarchy
        """
        if self.parent:
            # Set hierarchy based on parent
            if self.parent.hierarchy == "parent":
                self.hierarchy = "child"
            elif self.parent.hierarchy == "child":
                self.hierarchy = "grandchild"
            elif self.parent.hierarchy == "grandchild":
                raise ValidationError(
                    "タスクは最大3階層までです。孫タスク（grandchild）に子タスクを追加することはできません。"
                )
            # Inherit project from parent task
            self.project = self.parent.project
        else:
            # No parent means this is a parent task
            self.hierarchy = "parent"

    def save(self, *args, **kwargs):
        """
        Override save to call full_clean for validation and auto-set hierarchy
        Also propagate project changes to all descendant tasks
        """
        # Check if project has changed (only for existing tasks)
        project_changed = False
        if self.pk:
            try:
                old_task = Task.objects.get(pk=self.pk)
                project_changed = old_task.project != self.project
            except Task.DoesNotExist:
                pass

        self.full_clean()
        super().save(*args, **kwargs)

        # If project changed, update all descendant tasks
        if project_changed:
            self._update_descendants_project()

    def _update_descendants_project(self):
        """
        Update project for all descendant tasks when parent's project changes
        """
        for child in self.children.all():
            child.project = self.project
            # Use update_fields to avoid triggering full save logic and infinite recursion
            Task.objects.filter(pk=child.pk).update(project=self.project)
            # Recursively update grandchildren
            child._update_descendants_project()

    def get_all_children(self):
        """
        Recursively get all descendant tasks
        Returns: QuerySet of all child and grandchild tasks
        """
        children = list(self.children.all())
        for child in list(children):
            children.extend(child.get_all_children())
        return children

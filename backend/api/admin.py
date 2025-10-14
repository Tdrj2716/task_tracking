from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Project, Tag, Task


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin
    """
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at',)


class TaskAdminForm(forms.ModelForm):
    """
    Custom form for Task admin to filter parent, project, and tags by user
    """
    class Meta:
        model = Task
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If task already has a user or user is being set
        if self.instance and self.instance.user_id:
            user = self.instance.user

            # Filter parent choices to only show tasks from the same user
            self.fields['parent'].queryset = Task.objects.filter(user=user)

            # Filter project choices to only show projects from the same user
            self.fields['project'].queryset = Project.objects.filter(user=user)

            # Filter tags choices to only show tags from the same user
            self.fields['tags'].queryset = Tag.objects.filter(user=user)
        elif 'user' in self.data:
            # For new tasks, filter based on selected user
            try:
                user_id = int(self.data.get('user'))
                self.fields['parent'].queryset = Task.objects.filter(user_id=user_id)
                self.fields['project'].queryset = Project.objects.filter(user_id=user_id)
                self.fields['tags'].queryset = Tag.objects.filter(user_id=user_id)
            except (ValueError, TypeError):
                pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('name', 'user', 'project', 'parent', 'level', 'created_at')
    list_filter = ('created_at', 'project', 'level')
    search_fields = ('name', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'level', 'root')

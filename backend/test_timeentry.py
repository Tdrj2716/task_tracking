"""
Test script for TimeEntry model
Tests:
1. duration_seconds auto-calculation
2. SET_NULL behavior when task is deleted
"""

import os
import sys
from datetime import timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django before importing Django models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

# Import Django modules after setup
from django.utils import timezone  # noqa: E402
from api.models import User, Task, TimeEntry  # noqa: E402

# Get or create test user
user, _ = User.objects.get_or_create(
    username="testuser", defaults={"email": "test@example.com"}
)

# Test 1: duration_seconds auto-calculation
print("=== Test 1: duration_seconds auto-calculation ===")
start = timezone.now()
end = start + timedelta(hours=2, minutes=30, seconds=45)

entry = TimeEntry.objects.create(user=user, start_time=start, end_time=end)

expected_duration = 2 * 3600 + 30 * 60 + 45  # 9045 seconds
print(f"Expected duration: {expected_duration} seconds")
print(f"Actual duration: {entry.duration_seconds} seconds")
print(f"Test 1 PASSED: {entry.duration_seconds == expected_duration}")
print(f"String representation: {entry}")
print()

# Test 2: SET_NULL behavior when task is deleted
print("=== Test 2: SET_NULL behavior when task is deleted ===")

# Create a test task
task = Task.objects.create(user=user, name="Test Task for TimeEntry")

# Create a time entry with the task
entry_with_task = TimeEntry.objects.create(
    user=user,
    task=task,
    start_time=timezone.now(),
    end_time=timezone.now() + timedelta(hours=1),
)

print(f"Created TimeEntry with task: {entry_with_task}")
print(f"Task ID before deletion: {entry_with_task.task_id}")

# Delete the task
task_id = task.id
task.delete()

# Refresh the entry from database
entry_with_task.refresh_from_db()

print(f"Task ID after deletion: {entry_with_task.task_id}")
print(f"Test 2 PASSED: {entry_with_task.task_id is None}")
print(f"String representation after task deletion: {entry_with_task}")
print()

# Cleanup
TimeEntry.objects.filter(user=user).delete()
print("Cleanup completed")

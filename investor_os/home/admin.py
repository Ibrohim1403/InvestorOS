from django.contrib import admin
from .models import Task, Startup
from .models import Project, Issue

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "created_at")
    search_fields = ("title", "description")
    list_filter = ("status", "project")

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = ("name", "runway_months", "last_funding_date")
    search_fields = ("name",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "startup", "owner", "priority", "due_date", "ai_score")
    list_filter = ("priority", "status")
    search_fields = ("title", "description", "startup__name", "owner__username")

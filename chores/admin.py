from django.contrib import admin

from .models import Chore, CompletionHistory


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ("name", "due_date", "recurrence", "is_completed", "assigned_to", "created_by")
    list_filter = ("is_completed", "recurrence", "due_date")
    search_fields = ("name", "description", "created_by__username", "assigned_to__username")
    readonly_fields = ("completed_at", "created_at", "updated_at")


@admin.register(CompletionHistory)
class CompletionHistoryAdmin(admin.ModelAdmin):
    list_display = ("chore", "completed_by", "completed_at")
    list_filter = ("completed_at",)
    search_fields = ("chore__name", "completed_by__username")
    readonly_fields = ("completed_at",)

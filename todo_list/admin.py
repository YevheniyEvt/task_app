from django.contrib import admin

from .models import Project, Task


class TaskInLine(admin.TabularInline):
    model = Task
    extra = 0

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [TaskInLine]
    list_display  = ["name", 'id']


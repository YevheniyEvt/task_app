from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    owner = models.ForeignKey(
        User,
        related_name="projects",
        on_delete=models.CASCADE,
        )
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"Project: {self.name}"


class Task(models.Model):
    project = models.ForeignKey(
        Project,
        related_name="tasks",
        on_delete=models.CASCADE,
        )
    content = models.CharField()
    priority = models.IntegerField(default=0)
    completed  = models.BooleanField(default=False)
    deadline = models.DateField(
        auto_created=True,
        default=(datetime.today() + timedelta(days=1)).date(),
        )

    def __str__(self):
        return f"Project: {self.content[:10]}..."
    
    class Meta:
        ordering = ["-priority"]



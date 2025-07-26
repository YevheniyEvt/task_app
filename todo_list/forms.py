from django import forms

from .models import Project, Task


class TaskForm(forms.ModelForm):
        
    class Meta:
        model = Task
        fields = ['content']


class ProjectForm(forms.ModelForm):
        
    class Meta:
        model = Project
        fields = ['name']
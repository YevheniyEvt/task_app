from django import forms

from .models import Project, Task


class SmallTaskForm(forms.ModelForm):
        
    class Meta:
        model = Task
        fields = ['content']


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['content', 'deadline']
        
        widgets = {
            'content': forms.TextInput(attrs={
                'class': "form-control",
                'autocomplete': "off",
                'autofocus': 'true',
                'required': 'true',
            }),
            'deadline': forms.DateInput(attrs={
                'class': "form-control",
                'type': 'date',
            }),
        }


class ProjectForm(forms.ModelForm):
        
    class Meta:
        model = Project
        fields = ['name']


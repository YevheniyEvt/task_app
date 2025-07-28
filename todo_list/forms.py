from django import forms

from .models import Project, Task


class PriorityTaskForm(forms.ModelForm):
    
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = instance

    def clean_priority(self, **kwargs):
        priority_db = self.task.priority
        change_val = self.cleaned_data['priority']
        if  change_val == 1 and priority_db == 10:
            raise forms.ValidationError("Priority is maximum")
        if  change_val == -1 and priority_db == 0:
            raise forms.ValidationError("Priority is minimum")
        return change_val
        

    class Meta:
        model = Task
        fields = ['priority']


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

        widgets = {
            'name': forms.TextInput(attrs={
                'class': "form-control",
                'autocomplete': "off",
                'autofocus': 'true',
                'required': 'true',
                'placeholder': 'Your new project name',
            }),
        }


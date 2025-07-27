from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import F

from .models import Project, Task
from .forms import TaskForm


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TaskForm()
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    fields = ['name']
    model = Project
    success_url = reverse_lazy('projects:projects_list')
    template_name = "partials/empty_project_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        return render(self.request, 'todo_list/project.html', self.get_context_data())


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['name']
    model = Project
    success_url = reverse_lazy('projects:projects_list')
    template_name = 'todo_list/project_form.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        return render(self.request, self.get_template_names(), self.get_context_data())


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    http_method_names = ['post']
    success_url = reverse_lazy('projects:projects_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)
    
    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=200)
    

class TaskCreateView(LoginRequiredMixin, CreateView):
    fields = ['content']
    model = Task
    http_method_names = ['post']
    success_url = reverse_lazy('projects:projects_list')
    template_name = "todo_list/task_list.html"

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.project = project
        self.object = form.save()
        return render(self.request, self.get_template_names(), self.get_context_data())
    
    
class BaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project__owner=self.request.user)
    
    
class TaskUpdateView(BaseUpdateView):
    fields = ['content']
    success_url = reverse_lazy('projects:projects_list')

    def form_valid(self, form):
        super().form_valid(form)
        return HttpResponse(status=200)
    

class TaskCompletedUpdateView(BaseUpdateView):
    http_method_names = ['post']
    fields = ['completed']
    
    def form_valid(self, form):
        task = self.get_object()
        Task.objects.filter(id=task.id).update(completed=~F("completed"))
        return HttpResponse(status=200)
    

class TaskPriorityUpdateView(BaseUpdateView):
    http_method_names = ['post']
    fields = ['priority']
    template_name = 'todo_list/project.html'

    def form_valid(self, form):
        task = self.get_object()
        task.priority = F('priority') + form.cleaned_data['priority']
        task.save()
        return render(self.request, self.get_template_names(), self.get_context_data())
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.get_object().project
        return context

    
class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    http_method_names = ['post']
    success_url = reverse_lazy('projects:projects_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project__owner=self.request.user)

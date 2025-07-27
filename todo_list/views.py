from django.urls import reverse_lazy
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from .models import Project, Task
from .forms import TaskForm, ProjectForm


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
    form_class = ProjectForm
    model = Project
    success_url = reverse_lazy('projects:projects_list')
    template_name = "todo_list/project_form.html"

    def post(self, request, *args, **kwargs):
        if Project.objects.filter(name='').exists():
            return HttpResponseRedirect(reverse('projects:projects_list'))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
        

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProjectForm
    model = Project
    success_url = reverse_lazy('projects:projects_list')
    template_name = "todo_list/project_form.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    success_url = reverse_lazy('projects:projects_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)


class TaskCreateView(LoginRequiredMixin, CreateView):
    form_class = TaskForm
    success_url = reverse_lazy('projects:projects_list')
    # template_name = "todo_list/task_form.html"

    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        form.instance.project = project
        return super().form_valid(form)
    

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('projects:projects_list')
    # template_name = "todo_list/task_form.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project__owner=self.request.user)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    success_url = reverse_lazy('projects:projects_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project__owner=self.request.user)
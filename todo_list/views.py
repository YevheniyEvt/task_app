from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.db.models import F
from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .models import Project, Task
from .forms import PriorityTaskForm, TaskForm, ProjectForm


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    form_class = ProjectForm
    model = Project
    success_url = reverse_lazy('projects:projects_list')
    template_name = "todo_list/partials/project_form.html"
    
    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") == "true":
            return super().get(request, *args, **kwargs)
        else:
            return redirect('projects:projects_list')
        
    def form_valid(self, form):
        form.instance.owner = self.request.user
        if self.request.headers.get("HX-Request") == "true":
            self.object = form.save()
            return render(self.request, 'todo_list/project.html', self.get_context_data())
        else:
            return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProjectForm
    model = Project
    success_url = reverse_lazy('projects:projects_list')
    template_name = 'todo_list/project_title.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)
    
    def get(self, request, *args, **kwargs):
        if request.headers.get("HX-Request") == "true":
            project = Project.objects.filter(
                pk=self.kwargs['pk'],
                owner = self.request.user
                ).first()
            if project is None:
                return HttpResponseNotFound()
            context = {"project": project,
                       "form": ProjectForm(instance=project)
                       }
            return render(self.request, 'todo_list/partials/project_update.html', context)
        else:
            return redirect('projects:projects_list')
    
    def form_valid(self, form):
        if self.request.headers.get("HX-Request") == "true":
            self.object = form.save()
            return render(self.request, self.get_template_names(), self.get_context_data())
        else:
            return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    http_method_names = ['post']
    success_url = reverse_lazy('projects:projects_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)
    
    def form_valid(self, form):
        super().form_valid(form)
        if self.request.headers.get("HX-Request") == "true":
            return HttpResponse(status=200)
        else:
            success_url = self.get_success_url()
            return redirect(success_url)
    

class TaskCreateView(LoginRequiredMixin, CreateView):
    fields = ['content']
    model = Task
    success_url = reverse_lazy('projects:projects_list')
    template_name = "todo_list/task_list.html"
    
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.project = Project.objects.filter(
            pk=self.kwargs['project_id'],
            ).first()
    
    def get(self, request, *args, **kwargs):
        if (self.project is None or
             self.project.owner != self.request.user
             ):
            return HttpResponseNotFound()
        if request.headers.get("HX-Request") == "true":
            context = {
                "project": self.project,
                'form': TaskForm(),
            }
            return render(self.request, "todo_list/partials/full_task_form.html", context)
        else:
            return redirect('projects:projects_list')
    
    def form_valid(self, form):
        if self.project.owner != self.request.user:
            return HttpResponseNotFound()
        form.instance.project = self.project
        if self.request.headers.get("HX-Request") == "true":
            self.object = form.save()
            context = self.get_context_data()
            context['project'] = self.project
            return render(self.request, "todo_list/task_list.html", context)
        else:
            return super().form_valid(form)
    
    
class BaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project__owner=self.request.user)
    
    
class TaskUpdateView(BaseUpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy('projects:projects_list')
    template_name = "todo_list/task_list.html"

    def get(self, request, *args, **kwargs):
        task = Task.objects.filter(
            pk=self.kwargs['pk'],
            project__owner=self.request.user
            ).first()
        if task is None:
            return HttpResponseNotFound()
        if request.headers.get("HX-Request") == "true":
            context = {
                'task': task,
                'form': TaskForm(instance=task),
            }
            return render(self.request, "todo_list/partials/task_update_form.html", context)
        else:
            return redirect('projects:projects_list')
        
    def form_valid(self, form):
        if self.request.headers.get("HX-Request") == "true":
            self.object = form.save()
            context = self.get_context_data()
            context['project'] = self.object.project
            return render(self.request, 'todo_list/partials/one_task.html', context)
        else:
            return super().form_valid(form)
    

class TaskCompletedUpdateView(BaseUpdateView):
    http_method_names = ['post']
    fields = ['completed']
    
    def form_valid(self, form):
        if self.request.headers.get("HX-Request") == "true":
            task = self.get_object()
            Task.objects.filter(id=task.id).update(completed=~F("completed"))
            return HttpResponse(status=200)
        else:
            return HttpResponseNotAllowed(permitted_methods='hx-post')
    

class TaskPriorityUpdateView(BaseUpdateView):
    http_method_names = ['post']
    form_class = PriorityTaskForm
    template_name = "todo_list/task_list.html"

    def form_valid(self, form):
        
        if self.request.headers.get("HX-Request") == "true":
            task = self.get_object()
            task.priority += form.cleaned_data['priority']
            task.save()
            return render(self.request, self.get_template_names(), self.get_context_data())
        else:
            return HttpResponseNotAllowed(permitted_methods='hx-post')

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
    
    def form_valid(self, form):
        super().form_valid(form)
        if self.request.headers.get("HX-Request") == "true":
            return HttpResponse(status=200)
        else:
            success_url = self.get_success_url()
            return redirect(success_url)
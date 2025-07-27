from django.urls import path
from . import views

app_name ='projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='projects_list'),
    
    path('create/', views.ProjectCreateView.as_view(), name='projects_create'),
    path('delete/<int:pk>/', views.ProjectDeleteView.as_view(), name='projects_delete'),
    path('update/<int:pk>/', views.ProjectUpdateView.as_view(), name='projects_update'),

    path('<int:project_id>/task/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('task/delete/<int:pk>/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('task/update/<int:pk>/', views.TaskUpdateView.as_view(), name='task_update'),
    path('task/completed/<int:pk>/', views.TaskCompletedUpdateView.as_view(), name='task_completed'),
    path('task/priority/<int:pk>/', views.TaskPriorityUpdateView.as_view(), name='task_priority'),
]

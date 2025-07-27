"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from allauth.account import views
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.views.generic import RedirectView

from allauth.account.decorators import secure_admin_login

admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)

urlpatterns = [
    path('', RedirectView.as_view(pattern_name="projects:projects_list", permanent=False)),
    path('admin/', admin.site.urls),

    path('accounts/', include('allauth.urls')),
    path('logout/', RedirectView.as_view(pattern_name="account_logout", permanent=False)),
    path('projects/', include('todo_list.urls')),
]

from allauth.account import views
from django.urls import path

from .views import CustomPasswordChangeView


urlpatterns = [
    path("login/", views.login, name="account_login"),
    path("signup/", views.signup, name="account_signup"),
    path("logout/", views.logout, name="account_logout"),
    path("password/change/", CustomPasswordChangeView.as_view(), name="account_change_password"),

]


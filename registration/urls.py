from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "registration"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "<str:username>/",
        views.UserProfileView.as_view(),
        name="user_profile",
    ),
]

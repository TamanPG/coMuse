from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "registration"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("<str:username>/signout/", views.SignoutView.as_view(), name="signout"),
    path(
        "<str:username>/",
        views.UserProfileView.as_view(),
        name="user_profile",
    ),
    path("<str:username>/follow/", views.FollowView.as_view(), name="follow"),
    path("<str:username>/unfollow/", views.UnFollowView.as_view(), name="unfollow"),
    path("<str:username>/following_list/", views.FollowingListView.as_view(), name="following_list"),
    path("<str:username>/follower_list/", views.FollowerListView.as_view(), name="follower_list"),
    path(
        "<str:username>/bookmarklist/",
        views.MyBookmarksView.as_view(),
        name="bookmarkList",
    ),
    path("<str:username>/timeline/", views.TimelineView.as_view(), name="timeline"),
    path("<str:username>/editun/", views.UserNameUpdateView.as_view(), name="editun"),
]

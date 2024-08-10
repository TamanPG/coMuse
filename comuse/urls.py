from django.urls import path

from . import views

app_name = "comuse"

urlpatterns = [
    path("home/", views.HomeView.as_view(), name="home"),
    path("create/", views.PieceCreateView.as_view(), name="create"),
    path("<int:pk>/", views.PieceDetailView.as_view(), name="detail"),
    path("<int:pk>/delete/", views.PieceDeleteView.as_view(), name="delete"),
    path('<int:pk>/like/', views.LikeView, name='like'),
    path('<int:pk>/unlike/', views.UnlikeView, name='unlike'),
    path('<int:pk>/bookmark/', views.BookmarkView, name='bookmark'),
    path('<int:pk>/deletebookmark/', views.DeleteBookmarkView, name='deleteBookmark'),
]
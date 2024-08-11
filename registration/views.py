from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import HttpResponseRedirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from .forms import SignupForm
from .models import Friendship
from comuse.models import Piece, Like, Bookmark

User = get_user_model()


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = "registration/profile.html"
    model = User
    context_object_name = "user"
    slug_url_kwarg = "username"
    slug_field = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context["piece_list"] = Piece.objects.select_related("user").filter(user=user).order_by("-created_at")
        context["is_following"] = Friendship.objects.filter(following=user, follower=self.request.user).exists()
        context["following_num"] = Friendship.objects.filter(follower=user).count()
        context["followers_num"] = Friendship.objects.filter(following=user).count()
        context["user_like_list"] = Like.objects.filter(user=self.request.user).values_list("target", flat=True)
        context["user_bookmark_list"] = Bookmark.objects.filter(user=self.request.user).values_list("target", flat=True)
        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])
        follower = request.user

        if following == follower:
            messages.warning(request, "自分自身はフォローできません。")
            return HttpResponseBadRequest(render(request, "400.html"))

        if Friendship.objects.filter(following=following, follower=follower).exists():
            messages.warning(request, "フォロー済です。")
            return HttpResponseRedirect(reverse("registration:user_profile", kwargs={"username": following.username}))

        Friendship.objects.create(following=following, follower=follower)
        return HttpResponseRedirect(reverse("registration:user_profile", kwargs={"username": following.username}))


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        following = get_object_or_404(User, username=self.kwargs["username"])
        follower = request.user
        unfollow = Friendship.objects.filter(following=following, follower=follower)

        if following == follower:
            messages.warning(request, "自分自身を対象には出来ません。")
            return HttpResponseBadRequest(render(request, "error/400.html"))
        elif unfollow.exists():
            unfollow.delete()
            return HttpResponseRedirect(reverse("registration:user_profile", kwargs={"username": following.username}))
        else:
            messages.warning(request, "無効な操作です。")
            return HttpResponseBadRequest(render(request, "error/400.html"))


class FollowingListView(LoginRequiredMixin, ListView):
    template_name = "registration/following_list.html"
    context_object_name = "following_list"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Friendship.objects.select_related("following").filter(follower=user).order_by("-created_at")


class FollowerListView(LoginRequiredMixin, ListView):
    template_name = "registration/follower_list.html"
    context_object_name = "follower_list"

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs["username"])
        return Friendship.objects.select_related("follower").filter(following=user).order_by("-created_at")


class MyBookmarksView(LoginRequiredMixin, DetailView):
    template_name = "registration/bookmarkList.html"
    model = User
    context_object_name = "user"
    slug_url_kwarg = "username"
    slug_field = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        bookmarked = Piece.objects.select_related("user").prefetch_related("likes", "bookmarks").filter(bookmarks__user=user).order_by("-created_at")
        context["bookmarked_piece_list"] = bookmarked
        context["user_like_list"] = Like.objects.filter(target__in=bookmarked).values_list("target", flat=True)
        context["user_bookmark_list"] = Bookmark.objects.filter(user=user).values_list("target", flat=True)
        return context

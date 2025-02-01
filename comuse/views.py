from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

from .forms import PieceForm, CommentForm
from .models import Piece, Like, Bookmark, Comment
from django.db.models import Q

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    template_name = "comuse/home.html"
    model = Piece
    queryset = model.objects.select_related("user").prefetch_related("likes", "bookmarks").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        likes = Like.objects.select_related("target").filter(user=self.request.user).values_list("target", flat=True)
        bookmarks = Bookmark.objects.select_related("target").filter(user=self.request.user).values_list("target", flat=True)
        context["user_like_list"] = likes
        context["user_bookmark_list"] = bookmarks
        return context


class PieceCreateView(LoginRequiredMixin, CreateView):
    template_name = "comuse/create.html"
    success_url = reverse_lazy("comuse:home")
    form_class = PieceForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PieceDetailView(LoginRequiredMixin, DetailView):
    template_name = "comuse/detail.html"
    model = Piece
    queryset = model.objects.select_related("user").prefetch_related("likes", "bookmarks")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_liked"] = self.object.likes.filter(user=self.request.user, target_id=self.kwargs["pk"]).exists()
        context["liked_count"] = self.object.likes.filter(target_id=self.kwargs["pk"]).count()
        context["is_bookmarked"] = self.object.bookmarks.filter(user=self.request.user, target_id=self.kwargs["pk"]).exists()
        context["bookmarked_count"] = self.object.bookmarks.filter(target_id=self.kwargs["pk"]).count()
        context["comment_form"] = CommentForm
        return context


class PieceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "comuse/delete.html"
    model = Piece
    queryset = model.objects.select_related("user")
    success_url = reverse_lazy("comuse:home")

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        piece = get_object_or_404(Piece, pk=kwargs["pk"])
        Like.objects.get_or_create(target=piece, user=user)
        likes_count = Like.objects.filter(target=piece).count()
        context = {"liked_count": likes_count}
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        piece = get_object_or_404(Piece, pk=kwargs["pk"])
        like = Like.objects.filter(target=piece, user=user)
        like.delete()
        likes_count = Like.objects.prefetch_related("target").filter(target=piece).count()
        context = {"liked_count": likes_count}
        return JsonResponse(context)


class BookmarkView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        piece = get_object_or_404(Piece, pk=kwargs["pk"])
        Bookmark.objects.get_or_create(target=piece, user=user)
        bookmarks_count = Bookmark.objects.filter(target=piece).count()
        context = {"bookmarked_count": bookmarks_count}
        return JsonResponse(context)


class DeleteBookmarkView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        piece = get_object_or_404(Piece, pk=kwargs["pk"])
        bookmark = Bookmark.objects.filter(target=piece, user=user)
        bookmark.delete()
        bookmarks_count = Bookmark.objects.prefetch_related("target").filter(target=piece).count()
        context = {"bookmarked_count": bookmarks_count}
        return JsonResponse(context)


class CommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        piece_pk = self.kwargs.get('pk')
        piece = get_object_or_404(Piece, pk=piece_pk)
        comment = form.save(commit=False)
        comment.target = piece
        comment.save()
        return redirect('comuse:detail', pk=piece_pk)


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment

    def get_object(self):
        return Comment.objects.get(pk=self.kwargs['comment_pk'])

    def test_func(self):
        self.object = self.get_object()
        return self.request.user == self.object.user
    
    def get_success_url(self):
        return reverse_lazy('comuse:detail', kwargs={'pk': self.kwargs['pk']})


class SearchView(ListView):
    template_name = "comuse/result.html"
    model = Piece
    
    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('q')

        if query:
            result = Piece.objects.filter(Q(title__icontains=query) | Q(caption__icontains=query))
        
        return result
    
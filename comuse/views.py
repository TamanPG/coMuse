from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import PieceForm
from .models import Piece

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    template_name = "comuse/home.html"
    model = Piece
    queryset = model.objects.select_related("user").order_by("-created_at")


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
    queryset = model.objects.select_related("user")


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

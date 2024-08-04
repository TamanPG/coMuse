from django.forms import ModelForm

from .models import Piece


class PieceForm(ModelForm):
    class Meta:
        model = Piece
        fields = ("title", "uploadedFile", "comment",)
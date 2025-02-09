import django.forms as forms
from .models import Piece, Comment

class PieceForm(forms.ModelForm):
    class Meta:
        model = Piece
        fields = ("title", "uploadedFile", "caption", "commentAllowance")

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
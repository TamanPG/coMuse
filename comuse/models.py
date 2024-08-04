from django.conf import settings
from django.db import models


class Piece(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField(label="コメント", max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.TextField(label="タイトル", max_length=50)

    def __str__(self):
        return self.comment
    
    def __str__(self):
        return self.title

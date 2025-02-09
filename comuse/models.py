from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
import os
import datetime


def up_dir_path(instance, filename):
    date_time = datetime.datetime.now()
    date_dir = date_time.strftime('%Y/%m/%d')
    time_stamp = date_time.strftime('%H%M%S')
    new_filename = time_stamp + filename
    dir_path = os.path.join("files", date_dir, new_filename)
    return dir_path


class Piece(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    uploadedFile = models.FileField(blank=True, null=True, upload_to=up_dir_path, validators=[FileExtensionValidator(["mp3",])])
    caption = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    commentAllowance = models.BooleanField(default=False)

    def __str__(self):
        return self.caption
    
    def __str__(self):
        return self.title


class Like(models.Model):
    target = models.ForeignKey(Piece, related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="likes", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["target", "user"], name="like_unique"),
        ]


class Bookmark(models.Model):
    target = models.ForeignKey(Piece, related_name="bookmarks", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bookmarks", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["target", "user"], name="bookmark_unique"),
        ]


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=400)
    target = models.ForeignKey(Piece, related_name="comments", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

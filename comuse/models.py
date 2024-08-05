from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
import os
import datetime


def up_dir_path(instance, filename):
    date_time = datetime.datetime.now()
    date_dir = date_time.strftime('%Y/%m/%d')  # 年/月/日
    time_stamp = date_time.strftime('%H%M%S')  # 時分秒(ex: 120101)
    new_filename = time_stamp + filename
    dir_path = os.path.join("files", date_dir, new_filename)  # files/%Y/%m/%d/%H%M%Sファイル名
    return dir_path


class Piece(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    uploadedFile = models.FileField(blank=True, null=True, upload_to=up_dir_path, validators=[FileExtensionValidator(["mp3",])])
    comment = models.TextField(max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment
    
    def __str__(self):
        return self.title

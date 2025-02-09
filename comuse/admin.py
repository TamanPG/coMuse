from django.contrib import admin
from .models import Piece, Like, Bookmark, Comment


admin.site.register(Piece)
admin.site.register(Like)
admin.site.register(Bookmark)
admin.site.register(Comment)

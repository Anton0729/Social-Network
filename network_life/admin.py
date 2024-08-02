from django.contrib import admin
from .models import Post, Image, ProfilePage, Followers

admin.site.register([Post, Image, ProfilePage, Followers,])
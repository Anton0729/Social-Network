from django.db import models
from django.contrib.auth.models import User
import datetime
from cloudinary.models import CloudinaryField
from taggit.managers import TaggableManager


class ProfilePage(models.Model):
    first_name = models.CharField(max_length=50, default='', null=True)
    second_name = models.CharField(max_length=50, default='', null=True)
    username = models.CharField(max_length=50, unique=True)
    bio = models.TextField(default='', null=True)
    register_date = models.DateTimeField(default=datetime.datetime.now(), null=True)
    avatar = CloudinaryField('avatar',
                             transformation={'radius': '50', "width": "32", "quality": "auto", "crop": "scale",
                                             'default_image': 'default_avatar_mduiun.jpg'},
                             folder='/NetworkLife*/avatars')


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    main_image = CloudinaryField('main_image', folder='/NetworkLife*/images')
    preview = CloudinaryField('preview', transformation={"width": "400", "quality": "auto", "crop": "scale"},
                              folder='/NetworkLife*/preview')
    description = models.TextField()
    likes = models.ManyToManyField(User, related_name='post_likes')
    name = models.CharField(max_length=100)
    date_published = models.DateTimeField(default=datetime.datetime.now())

    tags = TaggableManager()


class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    images = CloudinaryField('images', folder='/NetworkLife*/images')
    previews = CloudinaryField('previews', folder='/NetworkLife*/preview')


class Followers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follow_to = models.CharField(max_length=100)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username

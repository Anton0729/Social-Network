from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import ProfilePage, Post, Image


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class PostForm(ModelForm):
    main_image = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Post's description"}), required=False)
    forms.TextInput(attrs={'class': 'form-control', 'data-role': 'tagsinput', 'placeholder': 'Tags'})

    class Meta:
        model = Post
        exclude = ['user', 'date_published', 'likes', 'name', 'preview']


class ImageForm(ModelForm):
    images = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control", "multiple": True}), required=False)

    class Meta:
        model = Image
        fields = ['images', 'previews']


class ProfilePageForm(ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), required=False)
    second_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}), required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control"}), required=False)
    avatar = forms.ImageField(widget=forms.FileInput(attrs={"class": "form-control"}), required=False)

    class Meta:
        model = ProfilePage
        fields = ('first_name', 'second_name', 'bio', 'avatar')

import datetime
import os
from io import BytesIO

from django.contrib.auth import authenticate, get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_network.settings")

import django
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.test.client import Client
from django.urls import reverse, resolve
from django.test.utils import setup_test_environment

setup_test_environment()
django.setup()

from network_life.models import ProfilePage, User
from network_life.forms import CreateUserForm, PostForm, ProfilePageForm, ImageForm
from network_life.views import like_unlike_post, home, create_post

from PIL import Image


class SignInTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='test1', password='password123',
                                                         email='test@gmail.com')
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_correct(self):
        user = authenticate(username='test1', password='password123')
        self.assertTrue(user.is_authenticated)
        self.assertTrue(user is not None)

    def test_wrong_username(self):
        user = authenticate(username='username02', password='password123')
        self.assertFalse(user is not None)

    def test_wrong_password(self):
        user = authenticate(username='test1', password='bad')
        self.assertFalse(user is not None and user.is_authenticated)


class TestForms(TestCase):
    def test_no_data_user_form(self):
        form = CreateUserForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 4)

    def test_no_data_img_form(self):
        form = ImageForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_profile_page_form(self):
        form = ProfilePageForm(data={
            'first_name': 'john',
            'second_name': 'desc',
            'bio': None,
            'avatar': 'avatar_img'
        })
        self.assertTrue(form.is_valid())
        self.assertTrue(form.fields['bio'].label is None)

    def test_post_form(self):
        form = PostForm(data={
            'main_image': 'test/img_url',
            'description': 'test_desc',
            'user': 1,
            'date_published': datetime.datetime.now(),
            'likes': 1,
            'name': 'john',
            'preview': 'test/preview_url'
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.data['main_image'], 'test/img_url')
        self.assertEqual(form.data['name'], 'john')
        self.assertEqual(form.fields['description'].required, False)


class TestUrls(TestCase):
    def test_home_resolves(self):
        url = reverse('network_life:home')
        self.assertEquals(resolve(url).func, home)

    def test_like_resolves(self):
        url = reverse('network_life:like-post-view', kwargs={'post_id': 1})
        self.assertEquals(resolve(url).func, like_unlike_post)

    def test_create_resolves(self):
        url = reverse('network_life:create')
        self.assertEquals(resolve(url).func, create_post)


class TestViews(TestCase):
    def setUp(self):
        # test user 1
        self.user = User.objects.create_user(username='john', password='johnpassword', email='john01@gmail.com')
        self.client = Client()
        self.client.login(username='john', password='johnpassword')
        self.profile = ProfilePage.objects.create(username='john')

        # test user 2
        User.objects.create_user(username='vova', password='vovapassword', email='vova01@gmail.com')
        self.client.login(username='vova', password='vovapassword')
        ProfilePage.objects.create(username='vova')

    def tearDown(self):
        self.user.delete()

    def test_update_profile(self):
        self.client.post('{0}?user=john'.format(reverse('network_life:update_profile')),
                         {'first_name': 'first_name_example', 'bio': 'Autobiography'}, )
        # get the latest info
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'first_name_example')
        self.assertEqual(self.profile.bio, 'Autobiography')

    def test_create_post(self):
        f = BytesIO()
        image = Image.new(mode='RGB', size=(100, 100))
        image.save(f, 'png')
        f.seek(0)
        test_image = SimpleUploadedFile("image.png", f.read(), )
        data = {
            'main_image': test_image,
            'description': 'test_desc',
            'user': 1,
            'date_published': datetime.datetime.now(),
            'likes': 1,
            'name': 'john',
            'tags': 'tag1, tag2',
            'preview': 'test/preview_url'
        }
        response = self.client.post(reverse('network_life:create'), data, format='multipart', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(list(response.context['messages'])[0]), 'Post created successfully')

    def test_like_unlike_post(self):
        # test add like
        response = self.client.post(reverse('network_life:like-post-view', kwargs={'post_id': 1}), follow=True,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # test remove like
        self.client.post(reverse('network_life:like-post-view', kwargs={'post_id': 1}), follow=True,
                         HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        assert b'<form action="/liked/1" method="POST" class=\'like-form\' id=\'1\'>' in response.content

    def test_post_id(self):
        response = self.client.post(reverse('network_life:post', kwargs={'id': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.path, '/post/1')

    def test_logout(self):
        response = self.client.get(reverse('network_life:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response)

    def test_register(self):
        response_is_authenticated = self.client.get(reverse('network_life:register'), follow=True)
        self.assertEqual(response_is_authenticated.status_code, 200)
        data = {'username': 'test_user', 'email': 'test_email@gmail.com', 'password1': 'Partenit14',
                'password2': 'Partenit14'}
        response = self.client.post(reverse('network_life:register'), data=data)
        self.assertEqual(response.request['REQUEST_METHOD'], 'POST')
        self.assertEqual(response_is_authenticated.status_code, 200)

    def test_profile(self):
        response = self.client.get(reverse('network_life:profile', kwargs={'username': 'john'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.kwargs['username'], 'john')
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        assert b'<p style="font-size: 1.75rem;"><b>john</b></p>' in response.content

    def test_following_accounts(self):
        self.client.post(reverse('network_life:follow', kwargs={'follower': 'vova', 'user': 'john'}),
                         follow=True)
        response = self.client.get(reverse('network_life:following_accounts', kwargs={'username': 'john'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.kwargs['username'], 'john')
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        # check that john are following sb (vova)
        assert b'<a href="/profile/vova" class="list-group-item list-group-item-action list-group-item-success">vova</a>' in response.content

    def test_followers_accounts(self):
        self.client.post(reverse('network_life:follow', kwargs={'follower': 'john', 'user': 'vova'}),
                         follow=True)
        response = self.client.get(reverse('network_life:followers_accounts', kwargs={'username': 'john'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.kwargs['username'], 'john')
        self.assertEqual(response.request['REQUEST_METHOD'], 'GET')
        # check that john have followers(vova)
        assert b'<a href="/profile/vova" class="list-group-item list-group-item-action list-group-item-success">vova</a>' in response.content

    def test_follow(self):
        # test follow user
        response_follow = self.client.post(reverse('network_life:follow', kwargs={'follower': 'john', 'user': 'vova'}),
                                           follow=True)
        # test unfollow user
        response_unfollow = self.client.post(
            reverse('network_life:follow', kwargs={'follower': 'john', 'user': 'vova'}),
            follow=True)
        self.assertEqual(response_follow.status_code, 200)
        self.assertEqual(response_unfollow.status_code, 200)
        # check with messages in response
        self.assertEqual(str(list(response_follow.context['messages'])[0]), f'You have just followed with john')
        self.assertEqual(str(list(response_unfollow.context['messages'])[0]), f'You have just unfollowed from john')

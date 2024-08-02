from django.core.management.base import BaseCommand
from network_life.models import ProfilePage, Post, LikePost
from django.contrib.auth import get_user_model
import random
import datetime
from faker import Faker
from PIL import Image

fake = Faker()


def make_pr(name):
    res = Image.open(name)
    MAX_SIZE = (250, 250)
    res.thumbnail(MAX_SIZE)
    res.save(f'network_life/static/files/previews/preview_{name}')
    return f'preview_{name}'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('insert_data')

    def handle(self, *args, **options):
        # create new User
        self.user = get_user_model().objects.create_user(
            username='test01',
            password='password123',
            email='test@gmail.com')
        self.user.save()

        # Create ProfilePage of User
        self.user_profile = ProfilePage(
            first_name=str(fake.name()).split()[0],
            second_name=str(fake.name()).split()[1],
            username=self.user.username,
            bio=fake.text(),
            register_date=datetime.datetime.now(),
            avatar='default_avatar.jpg',
        )
        self.user_profile.save()

        # create Post
        self.new_post = Post(
            main_image='network_life/static/files/images/test_photo.jpg',
            preview='network_life/static/files/previews/test_photo.jpg',
            description=fake.text(),
            tags=str(random.choice(['#sport', '#relax', '#travelling', '#studying'])),
            likes=random.randint(1, 100),
            name=self.user.username,
            date_published=datetime.datetime.now(),
            user_id=self.user.id,
        )
        self.new_post.save()

        # add to a LikePost
        self.add_to_likepost = LikePost(
            post_id=self.new_post.pk,
            username=self.user.username,
        )
        self.add_to_likepost.save()
        self.stdout.write(self.style.SUCCESS('Data were added!'))

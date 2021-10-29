from django.test import TestCase, Client
from django.test.utils import setup_test_environment
import uuid
from django.contrib.auth.models import User
from Author.models import Post, User
from .models import PostLike, PostComment


class TestModels(TestCase):
    def setUp(self):
        Post.objects.create(title='hello',
            contentType='text/plain',
            categories='hahaha',
            description='hello world',
            visibility=1,
            select_user=1,
            id='post_id_1',
            image='C:/temp/test.png')

        User.objects.create(
            id='user_id_1',
            username="username",
            email="user@ualberta.ca",
            first_name="user first",
            last_name="user last",
            is_active=True
        )

    def test_model_PostLike(self):
        PostLike.objects.create(post=Post.objects.get(id='post_id_1'), who_like=User.objects.get(id='user_id_1'))

        post_like = PostLike.objects.all()
        AssertTrue(post_like., "")


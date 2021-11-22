from django.test import TestCase
from django.contrib.auth import get_user_model
# Create your tests here.
from .models import User
from django.test import Client
import uuid
# https://www.youtube.com/watch?v=Ae7nc1EGv-A&t=1112s


class AuthorTestCase(TestCase):
    def setUp(self):
        self.author=User.objects.create(username="testuser101",
                            first_name="test_first",
                            last_name="test_last",
                            password="password",
                            email="testemail@email.ca",
                            github="https://github.com/XZPshaw")

    def test_create_author(self):
        self.assertEqual(self.author.username, "testuser101")
        self.assertEqual(self.author.email, "testemail@email.ca")
        self.assertEqual(self.author.first_name, "test_first")
        self.assertEqual(self.author.last_name, "test_last")
        self.assertEqual(self.github, "https://github.com/XZPshaw")



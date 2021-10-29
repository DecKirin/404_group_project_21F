from django.test import TestCase
from django.contrib.auth import get_user_model
# Create your tests here.
from .models import User
# https://www.youtube.com/watch?v=Ae7nc1EGv-A&t=1112s


class AuthorTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="testuser101",
                            first_name="test_first",
                            last_name="test_last",
                            password="password",
                            email="testemail@email.ca",
                            github="https://github.com/XZPshaw")
        
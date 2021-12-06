# python manage.py test api

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


import base64
import logging
import json

from Author.models import User,Post
from friends.models import FriendRequest



class InboxViewTests(TestCase):

    def setUp(self):
        User.objects.create(username="testuser101",
                            first_name="test_first",
                            last_name="test_last",
                            password="password",
                            email="testemail@email.ca",
                            github="https://github.com/XZPshaw")


    def test_post_local_follow(self):

        User1 = User.objects.create(username="testuser102",
                            first_name="test2",
                            last_name="test_last",
                            password="password",
                            email="test2email@email.ca",
                            github="https://github.com/XZPshaw")

        User2 = User.objects.create(username="testuser103",
                            first_name="test3",
                            last_name="test_last",
                            password="password",
                            email="test3email@email.ca",
                            github="https://github.com/XZPshaw")

        dataFr = {
            "type": "Follow",
            "summary": "test1 wants to follow test2",
            "actor": {
                "type": "author",
                "id": f"api/author/{User1.id}",
                "url": f"api/author/{User1.id}",
                "host": f"api/",
                "displayName": "Greg Johnson",
                "github": "https://github.com/XZPshaw",
                "profileImage": ""
            },
            "object": {
                "type": "author",
                "id": f"api/author/{User2.id}",
                "host": f"api/",
                "displayName": "Lara Croft",
                "url": f"api/author/{User2.id}",
                "github": "https://github.com/XZPshaw",
                "profileImage": ""
            }
        }

        # dataSender = {
        #     "type": "Follow",
        #     "summary": "test1 wants to follow test2",
        #     "sender": {
        #         "type": "author",
        #         "id": f"api/author/{User1.uuid}",
        #         "url": f"api/author/{User1.uuid}",
        #         "host": f"api/",
        #         "displayName": "Greg Johnson",
        #         "github": "https://github.com/XZPshaw",
        #         "profileImage": ""
        #     },
        #     "receiver": {
        #         "type": "author",
        #         "id": f"api/author/{User2.uuid}",
        #         "host": f"api/",
        #         "displayName": "Lara Croft",
        #         "url": f"api/author/{User2.uuid}",
        #         "github": "https://github.com/XZPshaw",
        #         "profileImage": ""
        #     }
        # }
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'testuser101:password').decode("ascii"),
        }

        response = self.client.post(
            reverse("Author:api_inbox", kwargs={"authorId":User2.id}),
            content_type="application/json",
            **auth_headers,
            data=dataFr
        )

        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("Author:api_inbox", kwargs={"authorId":User2.id}),
            content_type="application/json",
            **auth_headers,
        )

        self.assertEqual(response, dataFr)


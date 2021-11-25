from django.test import TestCase
from django.test import Client
from Author.models import Post, User
import uuid

post_id = uuid.uuid4().hex


class PostTestCase(TestCase):
    def setUp(self):
        Post.objects.create(title='hello',
                            contentType='text/plain',
                            categories='hahaha',
                            description='hello world',
                            visibility=1,
                            select_user=1,
                            id=post_id,
                            image='C:/temp/test.png')
        print("setup")

    def test_new_post(self):
        User.objects.create(id=1, username='XZPshaw222', password='123456', is_active=True)
        self.client.post("/Author/login/", {'username': 'XZPshaw', 'password': '12345'})

        info = {
            'title': 'hello',
            'content_type': 'text/plain',
            'categories': 'hahaha',
            'description': 'hello world',
            'visibility': '1',
            'select_user': '1',
            'image': 'C:/temp/test.png'
        }

        resp = self.client.post('/Author/newpost', info)
        print(resp)

    def imagem_model_test(self):
        testobject = Post.objects.get(id=post_id)
        self.assertEqual(testobject.image.url, '/media/post_image/test.png')

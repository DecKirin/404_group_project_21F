from django.test import TestCase, Client
from django.test.utils import setup_test_environment
import uuid
from django.contrib.auth.models import User
from Author.models import Post, User
from .models import PostLike, PostComment

# For testing view
# c = Client()
# c.login(username='fred', password='secret')

class TestModels(TestCase):
    def setUp(self):
        self.user_id = str(uuid.uuid4().hex)
        user = User.objects.create(
            username="username",
            email="user@ualberta.ca",
            first_name="user first",
            last_name="user last",
            id=self.user_id,
            is_active=True
        )

        self.post_id = str(uuid.uuid4().hex)
        Post.objects.create(title='hello',
            contentType='text/plain',
            categories='hahaha',
            description='hello world',
            author=user,
            id=self.post_id)


    def test_model_PostLike(self):
        PostLike.objects.create(post=Post.objects.get(id=self.post_id), who_like=User.objects.get(id=self.user_id))
        post_like = PostLike.objects.all()
        self.assertEqual(len(post_like), 1)
        self.assertEqual(post_like.get().post.id, self.post_id)
        self.assertEqual(str(post_like.get().who_like.id).replace('-', ''), self.user_id)

    def test_model_PostComment(self):
        id_comment = str(uuid.uuid4().hex)
        PostComment.objects.create(id_comment=id_comment,post=Post.objects.get(id=self.post_id), author_comment=User.objects.get(username='username'), comment_content="test for comments", published = "now")
        post_comment = PostComment.objects.get(id_comment=id_comment)
        self.assertEqual(post_comment.comment_content, "test for comments")
        self.assertEqual(str(post_comment.id_comment).replace('-', ''), id_comment)
        self.assertEqual(post_comment.author_comment, User.objects.get(username='username'))

    
   

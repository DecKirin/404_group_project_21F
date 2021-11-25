from django.test import TestCase
from .models import Friend, FriendRequest
from Author.models import User
from Author.serializers import UserSerializer

class FriendTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username="username1",
                                         email="123@gmail.com",
                                         first_name='first_name1',
                                         last_name='last_name1')
        self.user2 = User.objects.create(username="username2",
                                         email="456@gmail.com",
                                         first_name='first_name2',
                                         last_name='last_name2')
        Friend.objects.create(user=self.user1)

    def test_can_add_friend(self):
        friend = Friend.objects.get(user=self.user1)
        self.assertEqual(len(friend.friends), 0)
        friend.add_friend(UserSerializer(self.user2).data)
        self.assertEqual(len(friend.friends), 1)

    def test_can_delete_friend(self):
        friend = Friend.objects.get(user=self.user1)
        friend.add_friend(UserSerializer(self.user2).data)
        self.assertEqual(len(friend.friends), 1)
        friend.delete_friend(UserSerializer(self.user2).data)
        self.assertEqual(len(friend.friends), 0)


class FriendRequestTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="username1",
                                         email="123@gmail.com",
                                         first_name='first_name1',
                                         last_name='last_name1')
        self.user2 = User.objects.create(username="username2",
                                         email="456@gmail.com",
                                         first_name='first_name2',
                                         last_name='last_name2')

    def test_can_accept_friend_request(self):
        friend1 = Friend.objects.create(user=self.user1)
        friend2 = Friend.objects.create(user=self.user2)
        request = FriendRequest.objects.create(sender=UserSerializer(self.user1).data,
                                               receiver=UserSerializer(self.user2).data)
        self.assertEqual(len(friend1.friends), 0)
        self.assertEqual(len(friend2.friends), 0)
        self.assertFalse(request.respond_status)
        request.accept_request()
        self.assertEqual(len(friend1.friends), 1)
        self.assertEqual(len(friend2.friends), 1)
        self.assertTrue(request.respond_status)

    def test_can_decline_friend_request(self):
        friend1 = Friend.objects.create(user=self.user1)
        friend2 = Friend.objects.create(user=self.user2)
        request = FriendRequest.objects.create(sender=UserSerializer(self.user1).data,
                                               receiver=UserSerializer(self.user2).data)
        self.assertEqual(len(friend1.friends), 0)
        self.assertEqual(len(friend2.friends), 0)
        self.assertFalse(request.respond_status)
        request.decline_request()
        self.assertEqual(len(friend1.friends), 0)
        self.assertEqual(len(friend2.friends), 0)
        self.assertTrue(request.respond_status)

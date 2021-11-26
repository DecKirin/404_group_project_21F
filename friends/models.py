import datetime

from django.db import models
from django.conf import settings
import uuid


# Create your models here.
class Friend(models.Model):
    friends = models.JSONField(default=list, max_length=10000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cur_user', on_delete=models.CASCADE, null=True)

    def add_friend(self, new_friend):
        if not new_friend in self.friends:#.all():
            self.friends.append(new_friend)
            self.save()

    def delete_friend(self, delete_friend):
        if delete_friend in self.friends:#.all():
            self.friends.remove(delete_friend)
            self.save()


class Follower(models.Model):
    # followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="followers")
    followers = models.JSONField(default=list, max_length=10000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE, null=True)

    def add_follower(self, new_follower):
        if not new_follower in self.followers:
            self.followers.append(new_follower)
            self.save()

    def delete_follower(self, delete_follower):
        if delete_follower in self.followers:
            self.followers.remove(delete_follower)
            self.save()


class Follow(models.Model):
    follows = models.JSONField(default=list, max_length=10000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='users', on_delete=models.CASCADE, null=True)

    def add_follow(self, new_follow):
        if not new_follow in self.follows:#.all():
            self.follows.append(new_follow)
            self.save()

    def delete_follow(self, delete_follow):
        if delete_follow in self.follows:#.all():
            self.follows.remove(delete_follow)
            self.save()


'''
create new instance when current user trying to send befriend request
'''


class FriendRequest(models.Model):
    type = "follow"
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.JSONField(default=dict, max_length=2000)
    receiver = models.JSONField(default=dict, max_length=2000)

    #sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='req_sender', on_delete=models.CASCADE, null=True)
    #receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='req_receiver', on_delete=models.CASCADE,
    #                             null=True)
    respond_status = models.BooleanField(blank=False, null=False, default=False)
    created = models.DateTimeField(auto_now_add=True)

    def accept_request(self, sender_friend, receiver_friend):
        # sender_friend, create_sender = Friend.objects.get_or_create(user=self.sender)
        # receiver_friend, create_receiver = Friend.objects.get_or_create(user=self.receiver)
        receiver_friend.add_friend(self.sender)
        sender_friend.add_friend(self.receiver)
        self.respond_status = True
        self.save()

    def decline_request(self):
        self.respond_status = True
        self.save()

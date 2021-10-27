from django.db import models
from django.conf import settings
import uuid
# Create your models here.
class Friend(models.Model):

    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cur_user', on_delete=models.CASCADE, null=True)

    def add_friend(self, new_friend):
        if not new_friend in self.friends.all():
            self.friends.add(new_friend)

    def delete_friend(self, delete_friend):
        if delete_friend in self.friends.all():
            self.friends.remove(delete_friend)


class Follower(models.Model):

    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="followers")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE, null=True)

    def add_follower(self, new_follower):
        if not new_follower in self.followers.all():
            self.followers.add(new_follower)

    def delete_follower(self, delete_follower):
        if delete_follower in self.followers.all():
            self.followers.remove(delete_follower)


class Follow(models.Model):

    follows = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="follows")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='users', on_delete=models.CASCADE, null=True)

    def add_follow(self, new_follow):
        if not new_follow in self.follows.all():
            self.follows.add(new_follow)

    def delete_follow(self, delete_follow):
        if delete_follow in self.follows.all():
            self.follows.remove(delete_follow)


'''
create new instance when current user trying to send befriend request
'''
class FriendRequest(models.Model):
    request_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='req_sender', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='req_receiver', on_delete=models.CASCADE, null=True)
    respond_status = models.BooleanField(blank=False, null=False, default=True)

    def accept_request(self):
        sender_friend, create_sender = Friend.objects.get_or_create(user=self.sender)
        receiver_friend, create_receiver = Friend.objects.get_or_create(user=self.receiver)
        receiver_friend.add_friend(self.sender)
        sender_friend.add_friend(self.receiver)
        self.repond_status = True

    def decline_request(self):
        self.repond_status = True
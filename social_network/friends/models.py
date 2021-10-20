from django.db import models
from django.conf import settings
# Create your models here.
class Friend(models.Model):

    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends")
    cur_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='cur_user', on_delete=models.CASCADE, null=True)

    def add_friend(self, new_friend):
        if not new_friend in self.friends.all():
            self.friends.add(new_friend)

    def delete_friend(self, delete_friend):
        if not delete_friend in self.friends.all():
            self.friends.remove(delete_friend)


# class FriendRequest(models.Model):
#     sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender', on_delete=models.CASCADE, null=True)
#     receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver', on_delete=models.CASCADE, null=True)
#     sender_friend = Friend.objects.get(owner=sender)
#     receiver_friend = Friend.objects.get(owner=receiver)
#     respond_status = models.BooleanField(blank=False, null=False, default=True)
#
#     def accept_request(self):
#         self.receiver_friend.add_friend(self.sender, self.receiver)
#         self.sender_friend.add_friend()
#         self.repond_status = True
#
#     def decline_request(self):
#         self.repond_status = True
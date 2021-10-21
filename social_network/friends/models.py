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


'''
create new instance when current user trying to send befriend request
'''
class FriendRequest(models.Model):

    request_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='req_sender', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='req_receiver', on_delete=models.CASCADE, null=True)
    # sender_friend, create_sender = Friend.objects.get_or_create(cur_user=sender)
    # receiver_friend, create_receiver = Friend.objects.get_or_create(cur_user=receiver)

    respond_status = models.BooleanField(blank=False, null=False, default=True)

    def accept_request(self):
        sender_friend, create_sender = Friend.objects.get_or_create(cur_user=self.sender)
        receiver_friend, create_receiver = Friend.objects.get_or_create(cur_user=self.receiver)
        receiver_friend.add_friend(self.sender, self.receiver)
        sender_friend.add_friend(self.sender, self.receiver)
        self.repond_status = True

    def decline_request(self):
        self.repond_status = True
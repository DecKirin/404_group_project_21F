from django.db import models

# Create your models here.

class Inbox(models.Model):
    type = "inbox"
    author = models.ForeignKey(User, related_name='inbox', on_delete=models.CASCADE, null=False)
    items = models.CharField(blank=True, max_length=200)
    requests = models.ForeignKey(FriendRequest, related_name='inbox', on_delete=models.CASCADE, null=False)
    # Todo:Fetch Posts
from django.db import models
from django.contrib.auth.models import User, AbstractUser

# for slug and unique id
# https://www.youtube.com/watch?v=dJqWO-lSgWY
'''
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=20, unique=True)
    profile_image = models.URLField(blank=True)
    #profile_image = models.ImageField(default='',upload_to=)
    email = models.CharField(max_length=20, unique=True)
    # url path of user profile images
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
'''


class RegisterControl(models.Model):
    free_registration = models.BooleanField(default=True)

    def __str__(self):
        return 'free registration'




class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    profile_image = models.URLField(blank=True)
    email = models.CharField(max_length=20, unique=True)
    # url path of user profile images
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    u_phone = models.CharField(max_length=20, verbose_name='phone_number', default='', blank=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    github = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'sys_user_info'
        verbose_name = 'Author'
        verbose_name_plural = verbose_name


# https://www.youtube.com/watch?v=GcqURKYfv00
class Post(models.Model):
    visibility = {
        (1, "PUBLIC"),
        (2, "FRIEND ONLY"),
        (3, "PRIVATE"),
        (4, "UNLISTED"),
    }
    # author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=128)
    content = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    image = models.URLField(blank=True)
    source = models.URLField(blank=True)
    origin = models.URLField(blank=True)
    type = models.SmallIntegerField(default=1, choices=visibility)

    class Meta:
        ordering = ('created',)


class Comment(models.Model):
    # post is a foreign key of comment
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, null=False)
    # the author make this comment
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=80)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


class Like(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE, blank=False)


# https://stackoverflow.com/questions/65055520/django-user-subscribe-user-relation
class FollowAuthor(models.Model):
    # author = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='author_subscription')
    # subscribers = models.ManyToManyField(Author, related_name='subscriptions', blank=True)
    author = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_subscription')
    subscribers = models.ManyToManyField(User, related_name='subscriptions', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# https://medium.com/analytics-vidhya/add-friends-with-689a2fa4e41d
class FriendRequest(models.Model):
    status = [
        (1, "SENT"),
        (2, "ACCEPTED"),
        (3, "DENIED")
    ]
    # sender = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='sender')
    # receiver = models.OneToOneField(Author, on_delete=models.CASCADE, related_name='receiver')
    # sender = models.ForeignKey(
    sender = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='receiver')
    created = models.DateTimeField(auto_now_add=True)


class Friend(models.Model):
    users = models.ManyToManyField(User)
    current_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner", null=True)

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.add(new_friend)

    @classmethod
    def remove_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.remove(new_friend)

    def __str__(self):
        return str(self.current_user)

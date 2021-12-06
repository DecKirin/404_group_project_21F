from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import User, RegisterControl, Post, Node, Inbox
from friends.models import Friend, Follower, Follow, FriendRequest
from Post.models import PostComment, PostLike

# https://www.dothedev.com/blog/django-admin-list_filter/

# https://www.youtube.com/watch?v=djHsh4V79Yo&list=PLOLrQ9Pn6cazhaxNDhcOIPYXt2zZhAXKO&index=2
admin.site.index_title = 'Administration'
admin.site.site_header = 'Social Distribution Admin Page'
admin.site.site_title = 'admin home page'


# @admin.action(description='allow user to be on the server/activate user')
def activate_user(modeladmin, request, queryset):
    queryset.update(is_active=True)


# @admin.action(description='de-activate user')
def deactivate_user(modeladmin, request, queryset):
    queryset.update(is_active=False)


class PostInline(admin.TabularInline):
    model = Post
    extra = 1


# about aggregate information related to child table, like calculating number of posts created by user
# https://realpython.com/customize-django-admin-python/#prerequisites

# list foreign key related objects:
# https://www.py4u.net/discuss/143077
#
# https://www.youtube.com/watch?v=Ae7nc1EGv-A&t=1112s
class UserProfileAdmin(admin.ModelAdmin):
    inlines = [
        PostInline,

    ]

    list_display = (
        "email", "username", "is_active", "created", "view_posts_link", "view_likes_link", "view_comments_link")
    # list_display = ("email", "username", "is_active", "created", "view_posts_link", "view_friends_link",
    #                "view_likes_link", "view_comments_link")

    # list_display = ("email", "username", "is_active", "created", "view_friends_link","view_follows_link", "view_follower_link")
    search_fields = ("username", "id")
    list_filter = ("is_active", "created")
    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name', 'last_name', 'u_phone',)}),
        ('Permissions', {'fields': ('is_active',)}),
        ('links', {'fields': ('github', 'profile_image', 'host', 'url', 'api_url',)}),
        ('date', {'fields': ('created', 'updated',)}),
    )
    readonly_fields = ['created', 'updated']
    actions = [activate_user, deactivate_user]

    def view_posts_link(self, obj):
        count = obj.posts.count()
        url = (
                reverse("admin:Author_post_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Posts</a>', url, count)

    view_posts_link.short_description = "Posts"

    # ----------------------------------not finished yet----------------------------------
    ''''''
    def view_friends_link(self, obj):
        count = obj.curuser.count()
        url = (
                reverse("admin:friends_cur_user_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Friends</a>', url, count)

    view_friends_link.short_description = "Friends"
    '''

'''
    def view_follow_link(self, obj):
        count = obj.follows.count()
        url = (
            reverse("admin:friends_follows_changelist")+"?"+urlencode({"q":f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Follows</a>', url, count)
    view_follow_link.short_description = "follows"

    def view_followers_link(self, obj):
        count = obj.followers.count()
        url = (
            reverse("admin:friends_follower_changelist")+"?"+urlencode({"q":f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Posts</a>', url, count)
    view_followers_link.short_description = "followers"
    ''''''

    def view_likes_link(self, obj):
        count = obj.likes.count()
        url = (
                reverse("admin:Post_postlike_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} likes</a>', url, count)

    view_likes_link.short_description = "likes"

    def view_comments_link(self, obj):
        count = obj.comments.count()
        url = (
                reverse("admin:Post_postcomment_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Comments </a>', url, count)

    view_comments_link.short_description = "comments"


class PostsAdmin(admin.ModelAdmin):
    list_display = ("id", "view_author_link", "title", "published", "view_comments_link", "view_likes_link")
    search_fields = ("id", "title", "author__id", "author__username")
    list_filter = ("published", "author", "visibility")

    def view_author_link(self, obj):
        url = (
                reverse("admin:Author_user_changelist") + "?" + urlencode({"q": f"{obj.author.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.author.username)

    view_author_link.short_description = "Author"

    def view_comments_link(self, obj):
        count = obj.comments.count()
        url = (
                reverse("admin:Post_postcomment_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Comments</a>', url, count)

    view_comments_link.short_description = "comments"

    # view_comments_link.admin_order_field = 'count'

    def view_likes_link(self, obj):
        count = obj.post_like.count()
        url = (
                reverse("admin:Post_postlike_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Likes</a>', url, count)

    view_likes_link.short_description = "likes"


# Register your models here.
class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id_comment", "post", "comment", "published", "api_url")
    search_fields = ("post__id", "author__id", "author__username")
    list_filter = ("published", "author")

    def view_post_link(self, obj):
        url = (
                reverse("admin:Author_post_changelist") + "?" + urlencode({"q": f"{obj.post.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.post.title)

    view_post_link.short_description = "posts"

    def view_author_link(self, obj):
        url = (
                reverse("admin:Author_like_changelist") + "?" + urlencode({"q": f"{obj.author.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.author.username)

    view_author_link.short_description = "Author"


class LikesAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "who_like", "published")

    def view_author_link(self, obj):
        url = (
                reverse("admin:Author_user_changelist") + "?" + urlencode({"q": f"{obj.author.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.author.username)

    view_author_link.short_description = "Author"

    def view_post_link(self, obj):
        url = (
                reverse("admin:Author_post_changelist") + "?" + urlencode({"q": f"{obj.post.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.post.title)

    view_post_link.short_description = "Post"


class RegisterControlAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "user")

    #list_display = ("id", "view_author_link", "show_all_follows")
    search_fields = ("user",)
    '''
    def view_author_link(self, obj):
        url = (
                reverse("admin:Author_user_changelist") + "?" + urlencode({"q": f"{obj.user.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    view_author_link.short_description = "Author"

    def show_all_follows(self, obj):
        return "\n".join([a.username for a in obj.follows.all()])
    '''

class FollowerAdmin(admin.ModelAdmin):
    list_display = ("id", "user")

    #list_display = ("id", "view_author_link", "show_all_followers")
    search_fields = ("user",)
    '''
    def view_author_link(self, obj):
        url = (
                reverse("admin:Author_user_changelist") + "?" + urlencode({"q": f"{obj.user.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    view_author_link.short_description = "Author"

    def show_all_followers(self, obj):
        print("obj:", obj.followers)
        return "\n".join([a for a in obj.followers[0]])
    '''

class FriendAdmin(admin.ModelAdmin):
    list_display = ("id", "user")
    search_fields = ("user",)
    '''
    def view_author_link(self, obj):
        url = (
                reverse("admin:Author_user_changelist") + "?" + urlencode({"q": f"{obj.user.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    def show_all_friends(self, obj):
        return "\n".join([a.username for a in obj.friends.all()])
    '''
class FrRequestAdmin(admin.ModelAdmin):
    list_display = ("request_id", "sender", "receiver")

    search_fields = ("sender",)

class InboxAdmin(admin.ModelAdmin):
    list_display = ("author",)
    search_fields = ("author",)
'''
'''
admin.site.register(User, UserProfileAdmin)
admin.site.register(Post, PostsAdmin)
admin.site.register(PostComment, CommentsAdmin)
admin.site.register(PostLike, LikesAdmin)
admin.site.register(Friend, FriendAdmin)
admin.site.register(RegisterControl, RegisterControlAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Follower, FollowerAdmin)
'''
admin.site.register(Node)
admin.site.register(User)
admin.site.register(Post)
admin.site.register(PostComment)
admin.site.register(PostLike)
admin.site.register(Friend)
admin.site.register(RegisterControl)
admin.site.register(Follow)
admin.site.register(Follower)
'''
admin.site.register(FriendRequest, FrRequestAdmin)
admin.site.register(Inbox, InboxAdmin)
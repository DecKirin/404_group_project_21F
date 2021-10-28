from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from .models import User, RegisterControl
from friends.models import Friend, Follower, Follow

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

'''
class PostInline(admin.TabularInline):
    model = Post
    extra = 1
'''

# about aggregate information related to child table, like calculating number of posts created by user
# https://realpython.com/customize-django-admin-python/#prerequisites

# list foreign key related objects:
# https://www.py4u.net/discuss/143077
#
# https://www.youtube.com/watch?v=Ae7nc1EGv-A&t=1112s
class UserProfileAdmin(admin.ModelAdmin):
    '''
    inlines = [
        PostInline,

    ]
    '''
    list_display = ("email", "username", "is_active", "created")
    #list_display = ("email", "username", "is_active", "created", "view_posts_link", "view_friends_link",
    #                "view_likes_link", "view_comments_link")

    #list_display = ("email", "username", "is_active", "created", "view_friends_link","view_follows_link", "view_follower_link")
    search_fields = ("username",)
    list_filter = ("is_active", "created")
    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name', 'last_name', 'u_phone',)}),
        ('Permissions', {'fields': ('is_active',)}),
        ('links', {'fields': ('github', 'profile_image',)}),
        ('date', {'fields': ('created', 'updated',)}),
    )
    readonly_fields = ['created', 'updated']
    actions = [activate_user, deactivate_user]
    '''
    def view_posts_link(self, obj):
        count = obj.posts.count()
        url = (
                reverse("admin:Author_post_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Posts</a>', url, count)

    view_posts_link.short_description = "Posts"
    '''
    # ----------------------------------not finished yet----------------------------------
    '''
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
    '''
    '''

    def view_likes_link(self, obj):
        count = obj.posts.count()
        url = (
                reverse("admin:Author_like_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Likes</a>', url, count)

    view_likes_link.short_description = "likes"

    def view_comments_link(self, obj):
        count = obj.posts.count()
        url = (
                reverse("admin:Author_comment_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Comments </a>', url, count)

    view_comments_link.short_description = "comments"


class PostsAdmin(admin.ModelAdmin):
    list_display = ("type", "id", "author", "title", "published", "view_comments_link", "view_likes_link")
    search_fields = ("title", "author__id", "author__username")
    list_filter = ("published", "author")

    def view_comments_link(self, obj):
        count = obj.comments.count()
        url = (
                reverse("admin:Author_comment_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Comments</a>', url, count)

    view_comments_link.short_description = "comments"

    # view_comments_link.admin_order_field = 'count'

    def view_likes_link(self, obj):
        count = obj.comments.count()
        url = (
                reverse("admin:Author_like_changelist") + "?" + urlencode({"q": f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Likes</a>', url, count)

    view_likes_link.short_description = "likes"


# Register your models here.

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "created", "view_post_link", "view_author_link")
    search_fields = ("post__id", "author__id", "author__username")
    list_filter = ("created", "author")

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

'''
class RegisterControlAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(User, UserProfileAdmin)
#admin.site.register(Post, PostsAdmin)
#admin.site.register(Comment, CommentsAdmin)
#admin.site.register(Like)
admin.site.register(Friend)
admin.site.register(RegisterControl, RegisterControlAdmin)
admin.site.register(Follow)
admin.site.register(Follower)

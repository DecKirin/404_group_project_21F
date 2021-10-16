from django.contrib import admin
from .models import User, Post, Comment, Like
# Register your models here.
admin.site.register(User)


class UserProfileAdmin(admin.ModelAdmin):
    list_filters = ["is_active"]
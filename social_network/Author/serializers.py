from rest_framework import serializers
from .models import User, Post


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_image', 'email', 'first_name', 'last_name', 'github']


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'type', 'source', 'origin', 'description', 'contentType', 'content', 'author',
                  'categories', 'count', 'published', 'updated', 'visibility', 'image']


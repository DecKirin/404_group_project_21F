from rest_framework import serializers
from .models import User, Post, Inbox
from Post.models import PostComment
from Post.serializers import LikeSerializer, CommentSerializer


class UserSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    uuid = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    displayName = serializers.SerializerMethodField()
    profileImage = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['type', 'id', 'uuid', 'displayName', 'profileImage', 'email', 'github', 'host', 'url']

    def get_profileImage(self,obj):
        return obj.profile_image

    def get_displayName(self, obj):
        return obj.username

    def get_url(self, obj):
        return obj.api_url

    def get_id(self, obj):
        return obj.api_url

    def get_uuid(self, obj):
        return str(obj.id)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    def get_author(self, obj):
        return UserSerializer(User.objects.filter(id=obj.author.id).first()).data

    class Meta:
        model = Post
        fields = ['type', 'id', 'contentType', 'title', 'source', 'origin', 'description', 'content', 'author',
                  'categories', 'count', 'published', 'updated', 'visibility', 'image', 'comments', 'url']

    def get_url(self,obj):
        return obj.api_url
    def get_author(self, obj):
        return UserSerializer(User.objects.filter(id=obj.author.id).first()).data

    def get_comments(self, obj):
        return CommentSerializer(PostComment.objects.filter(post_id=obj.id), many=True).data


class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ['type', 'author_id', 'items']

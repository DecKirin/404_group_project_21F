from rest_framework import serializers
from .models import User, Post, Inbox
from Post.models import PostComment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['type', 'id', 'username', 'profile_image', 'email', 'first_name', 'last_name', 'github', 'host', 'api_url']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['type', 'id', 'contentType','title', 'source', 'origin', 'description', 'content', 'author',
                  'categories', 'count', 'published', 'updated', 'visibility', 'image', 'comments', 'api_url']

    def get_author(self, obj):
        return UserSerializer(User.objects.filter(id=obj.author.id).first()).data

    def get_comments(self, obj):
        return CommentSerializer(PostComment.objects.filter(post_id=obj.id), many=True).data

#### todo:comment type
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    # author_comment = UserSerializer(many=False, read_only= True)
    class Meta:
        model = PostComment
        # fields = ['id_comment', 'author_comment', 'comment_content', 'published','author']
        fields = ['type', 'id_comment', 'author', 'published', 'comment_content']

    def get_author(self, obj):
        return UserSerializer(User.objects.filter(id=obj.author_comment.id).first()).data
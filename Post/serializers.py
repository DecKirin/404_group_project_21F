from rest_framework import serializers
from Author.models import User, Post, Inbox
from .models import PostComment, PostLike


#### todo:comment type

class CommentSerializer(serializers.ModelSerializer):
    # author = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    # author_comment = UserSerializer(many=False, read_only= True)
    class Meta:
        model = PostComment
        # fields = ['id_comment', 'author_comment', 'comment_content', 'published','author']
        fields = ['type', 'id_comment', 'author', 'published', 'comment', 'api_url', 'id']

    # def get_author(self, obj):
    #    return UserSerializer(User.objects.filter(id=obj.author_comment.id).first()).data

    def get_id(self, obj):
        return obj.api_url


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = ['type', 'author', 'object', 'summary', 'post']

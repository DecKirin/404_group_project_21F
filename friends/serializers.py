from rest_framework import serializers
from .models import FriendRequest, Friend, Follow, Follower


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['type', 'request_id', 'sender', 'receiver', 'respond_status']


class FriendsSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    class Meta:
        model = Friend
        fields = ['type', 'items']

    def get_type(self, obj):
        return "friends"

    def get_items(self, obj):
        return obj.friends


class FollowsSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['type', 'items']

    def get_type(self, obj):
        return "follows"

    def get_items(self, obj):
        return obj.follows

class FollowersSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Follower
        fields = ['type', 'items']

    def get_type(self, obj):
        return "followers"

    def get_items(self, obj):
        return obj.followers
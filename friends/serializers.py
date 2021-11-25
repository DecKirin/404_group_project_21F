from rest_framework import serializers
from .models import FriendRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
<<<<<<< Updated upstream
        fields = ['type', 'sender', 'receiver']

=======
        fields = ['type', 'request_id','sender', 'receiver']
>>>>>>> Stashed changes

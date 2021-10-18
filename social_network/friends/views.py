from django.shortcuts import render
from .models import Friend

from django.core.paginator import Paginator

# Create your views here.


def friends_list_view(request, *args, **kwargs):

    context = {}
    user = request.user
    friend, create = Friend.objects.get_or_create(owner=user)  # class friend
    if not create:
        friend.add_friend(user)
    else:
        print(type(friend))
    friend_list = friend.friends.all() #

    context['friends'] = friend_list
    # context = {'friend': 'name'}
    return render(request, 'all_friends_list.html', context=context)

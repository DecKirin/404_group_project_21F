from django.shortcuts import render
from .models import Friend, FriendRequest, Follower, Follow
from Author.models import User
from django.core.paginator import Paginator

# Create your views here.


def friends_list_view(request, *args, **kwargs):

    context = {}
    user = request.user
    friend, create = Friend.objects.get_or_create(user=user)  # class friend
    if create:
        context['friends'] = ['Does not have friend yet']
    else:
        print(type(friend))
    friend_list = friend.friends.all() #

    context['friends'] = friend_list
    # context = {'friend': 'name'}
    return render(request, 'all_friends_list.html', context=context)

def followers_list_view(request, *args, **kwargs):
    context = {}
    user = request.user
    follower, create = Follower.objects.get_or_create(user=user)  # class friend
    if create:
        context['friends'] = ['Does not have follow yet']
    else:
        friend_list = follower.followers.all() #
        context['friends'] = friend_list
    # context = {'friend': 'name'}
    return render(request, 'all_friends_list.html', context=context)

def follows_list_view(request, *args, **kwargs):
    context = {}
    user = request.user
    follower, create = Follow.objects.get_or_create(user=user)  # class friend
    if create:
        context['friends'] = ['Does not have follower yet']
    else:
        friend_list = follower.follows.all() #
        context['friends'] = friend_list
    # context = {'friend': 'name'}
    return render(request, 'all_friends_list.html', context=context)

# todo: add user to tobefriend's follower
def send_friend_request(request, id, *args, **kwargs):
    context = {}
    user = request.user
    to_befriend = User.objects.get(id=id)
    friend_request = FriendRequest.objects.create(sender=user, receiver=to_befriend)
    cur_request_id = friend_request.request_id
    # add user to the follower list of to_befriend
    follower, create_follower = Follower.objects.get_or_create(user=to_befriend)
    follower.add_follower(user)
    # add to_befriend to the follower list of user
    follow, create_follow = Follow.objects.get_or_create(user=user)
    follow.add_follow(to_befriend)
    friend_request.respond_states = False
    context['request_user'] = user.username
    context['request_tobe'] = to_befriend.username
    return render(request, 'request_send.html', context=context)


'''
come after click on inbox message
'''
def process_friend_request(request, id):
    context = {}
    user = request.user
    friend_request_id = FriendRequest.objects.get(id=id)
    # to_befriend = User.objects.get(id=id)
    friend_request = FriendRequest.objects.get(request_id=friend_request_id)
    friend_tobe = friend_request.sender
    if request.POST['submit'] == 'accept':
        friend_request.accept_request()
        context['choice'] = f"You've now {friend_tobe.username}'s friend"

    elif request.POST['submit'] == 'remove':
        friend_request.decline_request()
        context['choice'] = f"You've declined {friend_tobe.username}'s request"
    return render(request, 'request_send.html', context=context)
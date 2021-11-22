from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from Author.serializers import UserSerializer
from .models import Friend, FriendRequest, Follower, Follow
from Author.models import User
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import Paginator
import logging


# Create your views here.

def un_befriend(request, id, delete):
    context = {}
    user = request.user
    to_del_friend = User.objects.get(id=id)
    if delete == 'Un-befriend':
        friend = Friend.objects.get(user=user)
        del_friend = Friend.objects.get(user=to_del_friend)
        friend.delete_friend(to_del_friend)
        del_friend.delete_friend(user)
        context['type'] = 'friend'
    elif delete == 'Un-follower':
        follower = Follower.objects.get(user=user)
        follower.delete_follower(to_del_friend)
        context['type'] = 'follower'
    elif delete == 'Un-follow':
        follow = Follow.objects.get(user=user)
        follow.delete_follow(to_del_friend)
        context['type'] = 'follow'
    context['user'] = user
    context['to_del_friend'] = to_del_friend
    return render(request, 'delete_friend.html', context=context)


def friends_list_view(request, id, *args, **kwargs):
    context = {}
    user = request.user
    view_user = User.objects.get(id=id)
    friend, create = Friend.objects.get_or_create(user=view_user)  # class friend
    if create:
        context['friends'] = ['Does not have friend yet']
    else:
        friend_list = friend.friends.all()  #
        context['friends'] = friend_list
    context['delete'] = 'Un-befriend'
    context['type'] = 'Friend'
    return render(request, 'all_friends_list.html', context=context)


'''
URL: ://service/author/{AUTHOR_ID}/followers
GET: get a list of authors who are their followers
'''


def followers_list_view(request, id, *args, **kwargs):
    context = {}
    user = request.user
    view_user = User.objects.get(id=id)
    follower, create = Follower.objects.get_or_create(user=view_user)  # class friend
    if create:
        context['friends'] = ['Does not have follow yet']
    else:
        friend_list = follower.followers.all()  #
        context['friends'] = friend_list
    context['delete'] = 'Un-follow'
    context['type'] = 'Follower'
    return render(request, 'all_friends_list.html', context=context)


def follows_list_view(request, id, *args, **kwargs):
    context = {}
    user = request.user
    view_user = User.objects.get(id=id)
    follower, create = Follow.objects.get_or_create(user=view_user)  # class friend
    if create:
        context['friends'] = ['Does not have follower yet']
    else:
        friend_list = follower.follows.all()  #
        context['friends'] = friend_list
    context['delete'] = 'Un-follow'
    context['type'] = 'Follow'
    return render(request, 'all_friends_list.html', context=context)


@login_required(login_url='/author/login/')
def my_list(request, relationship):
    context = {}
    user = request.user
    if relationship == 'follows':
        follower, create = Follow.objects.get_or_create(user=user)  # class friend
        if create:
            context['friends'] = ['Does not have follower yet']
        else:
            friend_list = follower.follows.all()  #
            context['friends'] = friend_list
        context['delete'] = 'Un-follow'
        context['type'] = 'Follow'
    elif relationship == 'followers':
        user = request.user
        follower, create = Follower.objects.get_or_create(user=user)  # class friend
        if create:
            context['friends'] = ['Does not have follow yet']
        else:
            friend_list = follower.followers.all()  #
            context['friends'] = friend_list
        context['delete'] = 'Un-follow'
        context['type'] = 'Follower'

    elif relationship == 'friends':
        user = request.user
        friend, create = Friend.objects.get_or_create(user=user)  # class friend
        if create:
            context['friends'] = ['Does not have friend yet']
        else:
            friend_list = friend.friends.all()  #
            context['friends'] = friend_list
        context['delete'] = 'Un-befriend'
        context['type'] = 'Friend'
    return render(request, 'my_friends_list.html', context=context)


'''
URL: ://service/author/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
DELETE: remove a follower
PUT: Add a follower (must be authenticated)
GET check if follower
'''


class follower_view(View):
    def get(self, request, id, foreign_id):
        context = {}
        cur_user = User.objects.get(id=id)
        view_user = User.objects.get(id=foreign_id)
        follower, create = Follower.objects.get_or_create(user=cur_user)
        # check if foreign key is follower of author_id
        exists = False
        if not create:
            if view_user in follower.followers.all():
                exists = True
                context['author'] = cur_user
                context['follower'] = view_user
        context['exists'] = exists
        return render(request, 'follower.html', context=context)

    def put(self, request, id, foreign_id):
        cur_user = User.objects.get(id=id)
        view_user = User.objects.get(id=foreign_id)
        follower, create = Follower.objects.get_or_create(user=cur_user)
        if cur_user.is_authenticated:
            follower.add_follower(view_user)

    def delete(self, request, id, foreign_id):
        cur_user = User.objects.get(id=id)
        view_user = User.objects.get(id=foreign_id)
        follower, create = Follower.objects.get_or_create(user=cur_user)
        follower.delete_follower(view_user)


# todo: add user to tobefriend's follower
def send_friend_request(request, foreign_id, *args, **kwargs):
    context = {}
    user = request.user
    to_befriend = User.objects.get(id=foreign_id)
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
    context['request_id'] = cur_request_id
    return render(request, 'request_send.html', context=context)


'''
come after click on inbox message
#todo: what happened after making decision
'''


class process_friend_request(View):

    def get(self, request, request_id):
        context = {}
        friend_request = FriendRequest.objects.get(request_id=request_id)
        request_user = friend_request.sender
        to_befriend = friend_request.receiver
        context['request_user'] = request_user.username
        context['request_tobe'] = to_befriend.username
        return render(request, 'request_process.html', context=context)

    def post(self, request, request_id):
        # logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
        context = {}
        user = request.user
        friend_request = FriendRequest.objects.get(request_id=request_id)
        request_user = friend_request.sender
        to_befriend = friend_request.receiver
        context['request_user'] = request_user.username
        context['request_tobe'] = to_befriend.username
        logging.debug(request.method)
        if request.POST.get("status") == 'Accept':
            friend_request.accept_request()
            # logging.debug(request.POST.get("status"))
            context['choice'] = f"You've now {request_user.username}'s friend"

        elif request.POST.get('status') == 'Decline':
            friend_request.decline_request()
            # logging.debug('Decline')
            context['choice'] = f"You've declined {request_user.username}'s request"

        # logging.debug('Nothing')
        return HttpResponseRedirect(reverse('Author:index'))

class APIFriendsByIdView(APIView):
    def get(self, request, id):
        # alternative approach, just use username

        view_user = User.objects.get(id=id)

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        # something like only showing active user
        # user_status = int(request.GET.get("user_status",1))
        friend, create = Friend.objects.get_or_create(user=view_user)  # class friend
        if create:
            response = Response()
            response.status_code = 200
            response.data = None
        else:
            friend_list = friend.friends.all().order_by()  #
            paginator = Paginator(friend_list, per_page)
            page_object = paginator.page(page)
            serializer = UserSerializer(page_object, many=True)
            response = Response()
            response.status_code = 200
            response.data = serializer.data
        return response


class APIFollowersByIdView(APIView):
    def get(self, request, id):
        # alternative approach, just use username

        view_user = User.objects.get(id=id)

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))

        follower, create = Follower.objects.get_or_create(user=view_user)  # class friend
        if create:
            response = Response()
            response.status_code = 200
            response.data = None
        else:
            follower_list = follower.followers.all().order_by()  #
            paginator = Paginator(follower_list, per_page)
            page_object = paginator.page(page)
            serializer = UserSerializer(page_object, many=True)
            response = Response()
            response.status_code = 200
            response.data = serializer.data
        return response


class APIFollowsByIdView(APIView):
    def get(self, request, id):
        # alternative approach, just use username

        view_user = User.objects.get(id=id)

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))

        follows, create = Follow.objects.get_or_create(user=view_user)  # class friend
        if create:
            response = Response()
            response.status_code = 200
            response.data = None
        else:
            follows_list = follows.follows.all().order_by()#
            paginator = Paginator(follows_list, per_page)
            page_object = paginator.page(page)
            serializer = UserSerializer(page_object, many=True)
            response = Response()
            response.status_code = 200
            response.data = serializer.data
        return response
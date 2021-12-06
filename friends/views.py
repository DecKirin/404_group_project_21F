import json
import logging
import requests
import urllib
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from Author.models import User, Inbox
from Author.serializers import UserSerializer
from Author.views import make_api_get_request, get_remote_authors
from Post.views import make_api_post_request
from .models import Friend, FriendRequest, Follower, Follow
from .serializers import FriendRequestSerializer, FollowsSerializer, FollowersSerializer, FriendsSerializer


# Create your views here.

def un_befriend(request, id, delete):
    context = {}
    user = request.user
    to_del_friend = User.objects.get(id=id)
    if delete == 'Un-befriend':
        friend = Friend.objects.get(user=user)
        del_friend = Friend.objects.get(user=to_del_friend)
        friend.delete_friend(UserSerializer(to_del_friend).data)
        del_friend.delete_friend(UserSerializer(user).data)
        context['type'] = 'friend'
    elif delete == 'Un-follower':
        follower = Follower.objects.get(user=user)
        follower.delete_follower(UserSerializer(to_del_friend).data)
        context['type'] = 'follower'
    elif delete == 'Un-follow':
        follow = Follow.objects.get(user=user)
        follow.delete_follow(UserSerializer(to_del_friend).data)
        context['type'] = 'follow'
    context['user'] = user
    context['to_del_friend'] = to_del_friend
    return redirect(reverse('Author:my_list', kwargs={'relationship': context['type']}))


def friends_list_view(request, id, *args, **kwargs):
    context = {}
    user = request.user
    view_user = User.objects.get(id=id)
    friend, create = Friend.objects.get_or_create(user=view_user)  # class friend
    if create:
        context['friends'] = ['Does not have friend yet']
    else:
        friend_list = friend.friends #
        context['friends'] = friend_list
    context['delete'] = 'Un-befriend'
    context['type'] = 'Friend'
    context['current_host'] = request.META['HTTP_HOST']
    return render(request, 'all_friends_list.html', context=context)


'''
URL: ://service/author/{AUTHOR_ID}/followers
GET: get a list of authors who are their followers
'''

class followers_list_view(APIView):
    def get(self, request, id):
        context = {}
        user = request.user
        view_user = User.objects.get(id=id)
        follower, create = Follower.objects.get_or_create(user=view_user)  # class friend
        if create:
            context['friends'] = ['Does not have follow yet']
        else:
            friend_list = follower.followers  #
            context['friends'] = friend_list
        context['current_author'] = user
        context['delete'] = 'Un-follow'
        context['type'] = 'Follower'
        context['current_host'] = request.META['HTTP_HOST']
        return render(request, 'all_friends_list.html', context=context)


def follows_list_view(request, id, *args, **kwargs):
    context = {}
    user = request.user
    view_user = User.objects.get(id=id)
    follower, create = Follow.objects.get_or_create(user=view_user)  # class friend
    if create:
        context['friends'] = ['Does not have follower yet']
    else:
        friend_list = follower.follows#
        context['friends'] = friend_list
    context['current_author'] = user
    context['delete'] = 'Un-follow'
    context['type'] = 'Follow'
    context['current_host'] = request.META['HTTP_HOST']
    return render(request, 'all_friends_list.html', context=context)


@login_required(login_url='/author/login/')
def my_list(request, relationship):
    context = {}
    user = request.user
    context['current_host'] = request.META['HTTP_HOST']
    logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
    if relationship == 'follows':

        follow, create = Follow.objects.get_or_create(user=user)  # class friend
        if create:
            context['friends'] = ['Does not have follower yet']
        else:
            friend_list = follow.follows# .all()  #
            # follow.delete_follow(user)
            context['friends'] = friend_list
            logging.debug(friend_list)
        context['delete'] = 'Un-follow'
        context['type'] = 'Follow'

    elif relationship == 'followers':
        user = request.user
        follower, create = Follower.objects.get_or_create(user=user)  # class friend
        if create:
            context['friends'] = ['Does not have follow yet']
        else:
            friend_list = follower.followers# .all()  #
            context['friends'] = friend_list
        context['delete'] = 'Un-follow'
        context['type'] = 'Follower'

    elif relationship == 'friends':
        user = request.user
        friend, create = Friend.objects.get_or_create(user=user)  # class friend
        if create:
            context['friends'] = ['Does not have friend yet']
        else:
            friend_list = friend.friends#.all()  #
            context['friends'] = friend_list

        context['delete'] = 'Un-befriend'
        context['type'] = 'Friend'
    context['current_author'] = user
    return render(request, 'my_friends_list.html', context=context)


# todo: add user to tobefriend's follower
def send_friend_request(request, foreign_id, *args, **kwargs):
    context = {}
    user = request.user
    to_befriend = User.objects.get(id=foreign_id)
    # friend_request = FriendRequest.objects.create(sender=user, receiver=to_befriend)
    friend_request = FriendRequest.objects.create(sender=UserSerializer(user).data,
                                                  receiver=UserSerializer(to_befriend).data)

    ##if send friend_request to a local author
    if to_befriend.host == request.META['HTTP_HOST']:
        # logging.basicConfig(filename='requestlog.log', level=logging.DEBUG)

        to_befriend = User.objects.get(id=foreign_id)
        # friend_request = FriendRequest.objects.create(sender=user, receiver=to_befriend)
        friend_request = FriendRequest.objects.create(sender=UserSerializer(user).data,
                                                      receiver=UserSerializer(to_befriend).data)
        cur_request_id = friend_request.request_id
        # add user to the follower list of to_befriend
        follower, create_follower = Follower.objects.get_or_create(user=to_befriend)
        follower.add_follower(UserSerializer(user).data)
        # add to_befriend to the follower list of user
        '''
        inbox_info = {
            "type": "Follow",
            "summary": "%s wants to follow %s" % (user.username, to_befriend.username),
            "actor": UserSerializer(user).data,
            "object": UserSerializer(to_befriend).data,
            "send_at": datetime.now
        }
        inbox_info = dict()
        inbox_info["type"] = "Follow"
        inbox_info["summary"] = "%s wants to follow %s" % (user.username, to_befriend.username)
        inbox_info["actor"] = UserSerializer(user).data
        inbox_info["object"] = UserSerializer(to_befriend).data
        inbox_info["send_at"] = datetime.now
        '''
        inbox_to_befriend, created = Inbox.objects.get_or_create(author=to_befriend)
        inbox_to_befriend.items.append(FriendRequestSerializer(friend_request).data)
        inbox_to_befriend.save()

        follow, create_follow = Follow.objects.get_or_create(user=user)
        follow.add_follow(UserSerializer(to_befriend).data)
        friend_request.respond_states = False
        context['request_user'] = user.username
        context['request_tobe'] = to_befriend.username
        context['request_id'] = cur_request_id
        context['current_author'] = user

    ##if foriegn author todo:deal with api of remore author
    else:
        pass

    return render(request, 'request_send.html', context=context)

class remote_sent_request(APIView):

    def get(self, request):
        context = {}
        user = request.user
        authorAPIUrl = request.GET.get("url")
        authorAPIUrl = urllib.parse.unquote(authorAPIUrl)
        author_request = make_api_get_request(authorAPIUrl)
        to_befriend = author_request.json()

        inbox_info = dict()
        inbox_info["type"] = "follow"
        logging.basicConfig(filename='another.log', level=logging.DEBUG)
        logging.debug(to_befriend)
        inbox_info["summary"] = "%s wants to follow %s" % (user.username, to_befriend['displayName'])
        # inbox_info["actor"] = UserSerializer(user).data
        author_json = {'type': 'author'}
        author_json['id'] = UserSerializer(user).data['uuid']
        author_json['displayName'] = UserSerializer(user).data['displayName']
        author_json['url'] = UserSerializer(user).data['id']
        author_json['host'] = UserSerializer(user).data['host']
        author_json['github'] = UserSerializer(user).data['github']
        author_json['avatar'] = None
        inbox_info["actor"] = author_json
        inbox_info["object"] = to_befriend
        # inbox_info["send_at"] = datetime.now
        follow, create_follow = Follow.objects.get_or_create(user=user)
        follow.add_follow(to_befriend)
        logging.basicConfig(filename='requestlog.log', level=logging.DEBUG)
        logging.debug(inbox_info)

        inbox_url = authorAPIUrl + "/inbox"
        logging.debug(inbox_url)
        logging.debug(json.dumps(inbox_info))
        request = make_api_post_request(inbox_url, inbox_info)
       
        return redirect(reverse('Author:my_list', kwargs={'relationship':'follows'}))

class remote_un_befriend(APIView):

    def get(self, request, delete):
        # logging.basicConfig(filename='requestlog.log', level=logging.DEBUG)
        user = request.user
        context = {}
        authorAPIUrl = request.GET.get("url")
        # logging.debug(authorAPIUrl)
        authorAPIUrl = urllib.parse.unquote(authorAPIUrl)
        response = Response()
        response.status_code = 200
        response.data = authorAPIUrl
        # return response
        author_request = make_api_get_request(authorAPIUrl)
        print(author_request)

        to_del_friend = author_request.json()
        if delete == 'Un-follow':
            follow = Follow.objects.get(user=user)
            follow.delete_follow(to_del_friend)
            context['type'] = 'follows'
        elif delete == 'Un-befriend':
            friend = Friend.objects.get(user=user)
            del_friend = Friend.objects.get(user=to_del_friend)
            friend.delete_friend(to_del_friend)
            del_friend.delete_friend(UserSerializer(user).data)
            context['type'] = 'friends'
        elif delete == 'Un-follower':
            follower = Follower.objects.get(user=user)
            follower.delete_follower(to_del_friend)
            context['type'] = 'followers'
        context['user'] = user
        context['to_del_friend'] = to_del_friend
        return redirect(reverse('Author:my_list', kwargs={'relationship':context['type']}))


'''
come after click on inbox message
#todo: what happened after making decision
'''


class process_friend_request(View):

    def get(self, request, request_id):
        context = {}
        # logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
        friend_request = FriendRequest.objects.get(request_id=request_id)
        request_user = friend_request.sender
        to_befriend = friend_request.receiver
        context['request_user'] = request_user['displayName']
        context['request_tobe'] = to_befriend['displayName']
        return render(request, 'request_process.html', context=context)

    def post(self, request, request_id):
        # logging.basicConfig(filename='mylog.log', level=logging.DEBUG)
        context = {}
        user = request.user
        friend_request = FriendRequest.objects.get(request_id=request_id)
        request_user = friend_request.receiver
        to_befriend = friend_request.sender

        context['request_user'] = request_user['displayName']
        context['request_tobe'] = to_befriend['displayName']
        # logging.debug(request.method)
        if request.POST.get("status") == 'Accept':
            if request_user.get('uuid') is not None:
                uuid = request_user.get('uuid')
            else:
                uuid = request_user.get('id').split('/')[-1]
            print(uuid)
            request_user_type = User.objects.get(id=uuid)
            request_friend, request_create = Friend.objects.get_or_create(user=request_user_type)

            if to_befriend['host'] == request.META['HTTP_HOST']:
                to_befriend_id = to_befriend['uuid']
                print(to_befriend_id)
                to_befriend_user = User.objects.get(id=to_befriend_id)
                to_befriend_friend, to_be_create = Friend.objects.get_or_create(user=to_befriend_user)
                friend_request.accept_request(request_friend, to_befriend_friend)
            else:
                to_befriend_id = to_befriend.get('id').split('/')[-1]
                request_friend.add_friend(to_befriend)

            context['choice'] = f"You've now {request_user['displayName']}'s friend"

        elif request.POST.get('status') == 'Decline':
            friend_request.decline_request()
            # logging.debug('Decline')
            context['choice'] = f"You've declined {request_user['displayName']}'s request"

        # logging.debug('Nothing')
        return render(request, 'mystream.html')
        # return HttpResponseRedirect(reverse('Author:index'))


''''''''''''''''''''''''''''''''''''''''follower/follows/friends related api'''''''''''''''''''''''''''''''''''''''''''''''


class APIFriendsByIdView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        view_user = User.objects.get(id=id)

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))

        friend, create = Friend.objects.get_or_create(user=view_user)  # class friend
        response = Response()
        response.status_code = 200
        serializer = FriendsSerializer(friend)
        response.data = serializer.data

        return response


class APIFollowersByIdView(APIView):

    def get(self, request, id):
        # alternative approach, just use username

        try:
            view_user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        #page = int(request.GET.get("page", 1))
        #per_page = int(request.GET.get("size", 10))

        follower, create = Follower.objects.get_or_create(user=view_user)  # class friend
        response = Response()
        response.status_code = 200
        serializer = FollowersSerializer(follower)
        response.data = serializer.data

        return response


class APIFollowsByIdView(APIView):
    def get(self, request, id):
        # alternative approach, just use username

        view_user = User.objects.get(id=id)

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))

        follows, create = Follow.objects.get_or_create(user=view_user)  # class friend
        response = Response()
        response.status_code = 200
        serializer = FollowsSerializer(follows)
        response.data = serializer.data

        return response


'''
URL: ://service/author/{AUTHOR_ID}/followers/{FOREIGN_AUTHOR_ID}
DELETE: remove a follower
PUT: Add a follower (must be authenticated)
GET check if follower
'''


class API_follower_view(APIView):
    # http_method_names = ['GET', 'PUT', 'DELETE']

    def get(self, request, id, foreign_id):
        try:
            cur_user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        context = {}

        follower, create = Follower.objects.get_or_create(user=cur_user)
        # check if foreign key is follower of author_id
        exists = False
        view_user = None

        if not create and len(follower.followers) > 0:
            for f in follower.followers:
                # logging.debug(f['id'])
                if f is not None:
                    if f.get('id') is not None:
                        uuid = f.get('id').split('/')[-1]
                    elif f.get('uuid') is not None:
                        uuid = f.get('uuid')
                    else:
                        continue
                    if str(foreign_id) == str(uuid):
                        exists = True
                        context['author'] = UserSerializer(cur_user).data
                        context['follower'] = f
                        view_user = f
                        break
        context['exists'] = exists
        response = Response()
        response.status_code = 200
        check_info = {
            'status': exists,
            'author': cur_user.username
            # 'follower': view_user['displayName']
        }
        response.data = json.dumps(check_info)
        return response
        # return render(request, 'follower.html', context=context)

    def put(self, request, id, foreign_id):
        cur_user = User.objects.get(id=id)
        response = Response()
        if cur_user.is_authenticated:
            follower, create = Follower.objects.get_or_create(user=cur_user)
            view_user = None
            try:
                view_user = User.objects.get(id=foreign_id)
                view_user = UserSerializer(view_user).data
            except User.DoesNotExist:
                exists = False
                authors = get_remote_authors()
#                 logging.basicConfig(filename='another.log', level=logging.DEBUG)
#                 logging.debug(authors)
                for f in follower.followers:
                    if f is not None:
                        if f.get('id') is not None:
                            uuid = f.get('id').split('/')[-1]
                        elif f.get('uuid') is not None:
                            uuid = f.get('uuid')
                        else:
                            continue
                        if str(foreign_id) == str(uuid):
                            response.status_code = 200
                            return response
                for author in authors:
                    if author.get('id') is not None:
                        uuid = author.get('id').split('/')[-1]
                    elif author.get('uuid') is not None:
                        uuid = author.get('uuid')
                    else:
                        continue
                    if str(foreign_id) == str(uuid):

                        exists = True
                        view_user = author
                if not exists:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            finally:
                if view_user is not None:
                    follower.add_follower(view_user)
                    response.status_code = 200
                    response.data = json.dumps(follower.followers)
                    return response
                
        return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id, foreign_id):
        cur_user = User.objects.get(id=id)
        follower, create = Follower.objects.get_or_create(user=cur_user)
        # view_user = User.objects.get(id=foreign_id)
        for f in follower.followers:
            if f is not None:
                if f.get('id') is not None:
                    uuid = f.get('id').split('/')[-1]
                elif f.get('uuid') is not None:
                    uuid = f.get('uuid')
                else:
                    continue
                if str(foreign_id) == str(uuid):
                    follower.delete_follower(f)
                    response = Response()
                    response.status_code = 200
                    response.data = json.dumps(follower.followers)
                    return response
        # author to be deleted does not exists in user's follower lists
        return Response(status=status.HTTP_404_NOT_FOUND)


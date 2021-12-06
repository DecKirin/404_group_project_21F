import re
import json
import base64
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites import requests
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import renderer_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.db import models
from rest_framework.renderers import TemplateHTMLRenderer
import urllib
from Author.serializers import UserSerializer, PostSerializer, CommentSerializer, InboxSerializer
from friends.models import FriendRequest, Follower, Friend
from Post.serializers import LikeSerializer
from Author.models import User, RegisterControl, Inbox, Post, Node
from Post.models import PostComment, PostLike
# Create your views here.
from django.views import View
from django.contrib.auth import authenticate, login, logout
import requests
from requests.auth import HTTPBasicAuth
from friends.serializers import FriendRequestSerializer
from social_network.settings import SECRET_KEY

"""during test stage, use this instead of manually adding node using admin pannel"""

"""in case vpn issues, modify based on your own vpn"""

'''
# if proxy is needed, change the proxies according to your proxy setting
def make_api_get_request(api_url):
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    # uname = "team11"
    # pas = "secret11"
    print("api_request:", api_url)
    request = requests.get(api_url, proxies=proxies, auth=HTTPBasicAuth("team11", "secret11"), verify=True)
    print("code:", request.status_code)
    if request.status_code in [403, 401, 500]:

        request = requests.get(api_url, proxies=proxies, auth=HTTPBasicAuth("7c70c1c8-04fe-46e0-ae71-8969061adac0", "123456"), verify=True)
    return request
'''


def process_categories(categories):
    categories = categories.split(',')
    for i in range(len(categories)):
        categories[i] = categories[i].strip()
    return str(categories)


# if proxy is not needed
def make_api_get_request(api_url):
    if "https://cmput404f21t17.herokuapp.com" in api_url:
        request = requests.get(api_url, auth=HTTPBasicAuth("7c70c1c8-04fe-46e0-ae71-8969061adac0", "123456"),
                               verify=True)
    else:
        request = requests.get(api_url, auth=HTTPBasicAuth("team11", "secret11"), verify=True)
    # if request.status_code in [403, 401, 500]:
    #    request = requests.get(api_url, auth=HTTPBasicAuth("7c70c1c8-04fe-46e0-ae71-8969061adac0", "123456"), verify=True)
    return request


# check if validation by admin is required to activate an author account
def check_if_confirmation_required():
    try:
        confirm = RegisterControl.objects.all()
        assert confirm != None and list(confirm) != [], "raise"

    except Exception:
        registerControl = RegisterControl()
        registerControl.save()
        return registerControl.free_registration
    else:
        return list(confirm)[0].free_registration


def get_remote_nodes():
    nodes = Node.objects.all()
    nodes = Node.objects.filter(allow_connection=True)
    all_host = [node.host for node in nodes]
    print(all_host)
    # to test with team17

    #all_host = ["https://cmput404f21t17.herokuapp.com", "https://social-distribution-fall2021.herokuapp.com","https://cmput404-team13-socialapp.herokuapp.com"]
    all_host = ["https://cmput404f21t17.herokuapp.com"]
    return all_host


def get_remote_authors():
    all_remote_host = get_remote_nodes()

    authors = []
    for host in all_remote_host:
        api_uri = host + '/api' + '/authors/'
        if host == "https://cmput404f21t17.herokuapp.com":
            api_uri = host + '/service/authors/'
        print("api_uri:", api_uri)
        ####todo:authentication information
        ####request = requests.get(api_uri, auth=HTTPBasicAuth(auth_user, auth_pass))
        try:
            # proxies = {"http": None, "https": None}66
            request = make_api_get_request(api_uri)
            print("request", request.json())
            if request.status_code == 200:
                try:
                    authors_in_host = request.json()["items"]
                except Exception:
                    authors_in_host = request.json()
                authors = authors + authors_in_host
            else:
                continue
        except Exception:
            continue
    print(authors)
    return authors


def get_team_flag():
    all_remote_host = get_remote_nodes()
    flag = 0
    for host in all_remote_host:
        if host == "https://social-distribution-fall2021.herokuapp.com/api/":
            flag = 4
        elif host == "https://cmput404f21t17.herokuapp.com/":
            flag = 17
        elif host == "http://cmput404-team13-socialapp.herokuapp.com":
            flag = 13
        else:
            flag = 1
    return flag


def get_remote_public_posts():
    all_remote_host = get_remote_nodes()

    posts = []
    for host in all_remote_host:
        api_uri = host + '/api' + '/posts/'

        if host == "https://cmput404f21t17.herokuapp.com":
            api_uri = host + '/service/authors/'

        request = requests.get(api_uri)
        if request.status_code == 200:
            posts_in_host = request.json()
            posts += posts_in_host
    return posts


def get_all_remote_public_posts_through_remote_authors():
    remote_authors = get_remote_authors()
    all_remote_posts = []

    for author in remote_authors:
        post_url = ""
        if author["url"][-1] == "/":
            post_url = author["url"] + "posts"
        else:
            post_url = author["url"] + "/posts"
        print(post_url)
        try:
            request = make_api_get_request(post_url)
            print("request.data:", request)
            if request.status_code == 200:
                try:
                    posts = request.json()["items"]
                except Exception:
                    posts = request.json()
            else:
                continue
            all_remote_posts += posts
        except Exception:
            continue
    print(all_remote_posts)
    return all_remote_posts


class baseView(View):
    def get(self, request):
        return HttpResponseRedirect(reverse("Author:login"))


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        json_data = []
        error_msg_dic = {
            "data": "",
            "msg": "",
            "code": ""
        }
        username = request.POST.get('user_name')
        userfname = request.POST.get('user_fname')
        userlname = request.POST.get('user_lname')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        github = request.POST.get('github')
        # allow = request.POST.get('allow')
        if not all([username, password, email, userfname, userlname]):
            # missing data
            error_msg_dic["code"] = "400"
            error_msg_dic["msg"] = "data missing"
            json_data.append(error_msg_dic)
            return HttpResponse(json.dumps(json_data))
        # check if user name already exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # User name does not exist
            user = None
        if user:
            # username exists
            error_msg_dic["code"] = "400"
            error_msg_dic["msg"] = "The Username is already taken."
            json_data.append(error_msg_dic)
            return HttpResponse(json.dumps(json_data))

        is_active = True
        if not check_if_confirmation_required():
            is_active = False

        user = User.objects.create_user(username=username, email=email, password=password, first_name=userfname,
                                        last_name=userlname, is_active=is_active, github=github)
        # user.is_active = 1
        user.host = request.META['HTTP_HOST']
        user.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(user.id) + "/"
        user.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(user.id) + "/"
        user.save()
        Inbox.objects.create(author=user)
        error_msg_dic["code"] = "200"
        error_msg_dic["msg"] = "Successfully register"
        json_data.append(error_msg_dic)
        return HttpResponse(json.dumps(json_data))


'''
URL: ://service/author/login
GET: visit login page
POST: send verification information to login
'''


class LoginView(View):
    def get(self, request):
        username = ''
        remember = False
        if 'username' in request.COOKIES:
            # username = request.COOKIES.get('username')
            username = request.get_signed_cookie('username', '', SECRET_KEY)
            remember = request.get_signed_cookie('remember', 'checked', SECRET_KEY)
            print(username, remember)
        return render(request, 'login.html', {'username': username, 'remember': remember})

    def post(self, request):
        json_data = []
        error_msg_dic = {
            "data": "",
            "msg": "",
            "code": ""
        }

        # receive data
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')

        # validate data
        if not all([username, password]):
            error_msg_dic["code"] = "500"
            error_msg_dic["msg"] = "data missing"
            json_data.append(error_msg_dic)
            return HttpResponse(json.dumps(json_data))
        # login authentication
        user = authenticate(username=username, password=password)
        if user is not None:
            # username and password correct
            '''
            if user.is_delete:
                error_msg_dic["code"] = "401"
                error_msg_dic["msg"] = "not active user"
                json_data.append(error_msg_dic)
                return HttpResponse(json.dumps(json_data))
            '''
            if user.is_active:
                # user account is an active one
                # keep user login
                login(request, user)

                # acquire next page
                # by default, go to index page
                next_url = request.GET.get('next', reverse('Author:mystream'))
                # # direct to next page
                # response = redirect(next_url)  # HttpResponseRedirect

                error_msg_dic["code"] = "200"
                error_msg_dic["msg"] = "User verified"
                json_data.append(error_msg_dic)
                print(json_data)
                request.session["username"] = username
                response_index = HttpResponse(json.dumps(json_data))

                # check if remember user
                remember = request.POST.get('remember')

                # request.set_signed_cookie('username', username, max_age=7 * 24 * 3600)
                if remember == 'true':
                    # remember user name
                    response_index.set_signed_cookie('username', username, SECRET_KEY, max_age=7 * 24 * 3600)
                    response_index.set_signed_cookie('remember', 'checked', SECRET_KEY, max_age=7 * 24 * 3600)
                else:
                    response_index.delete_cookie('username')
                    response_index.delete_cookie('remember')

                # return response
                return response_index
            else:
                # User account is not active
                error_msg_dic["code"] = "403"
                error_msg_dic["msg"] = "Not An Active Account,Please Contact Administrator"
                json_data.append(error_msg_dic)
                print(json_data)
                return HttpResponse(json.dumps(json_data))
        else:
            # Username or Password not correct
            # return render(request, 'login.html', {'errmsg': 'Username or Password not correct'})
            error_msg_dic["code"] = "401"
            error_msg_dic["msg"] = "Username or Password not correct"
            json_data.append(error_msg_dic)
            print(json_data)
            return HttpResponse(json.dumps(json_data))


# the main page after user logining in,
# probably should be stream page later!!!!!
class IndexView(LoginRequiredMixin, View):

    def get(self, request):
        # current logged in user
        curr_user = request.user

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        posts = Post.objects.filter(author_id=curr_user.id).filter(visibility=1)
        # inbox = Inbox.objects.filter(requests=friReqs)

        paginator = Paginator(posts, per_page)
        page_object = paginator.page(page)

        try:
            github = curr_user.github
            githubUname = github.split("/")[-1]
        except Exception:
            githubUname = None

        context = {
            'id': id,
            'current_author': curr_user,
            'githubName': githubUname,
            'myPosts': posts,
            'page_object': page_object,
            'page_range': paginator.page_range,
        }

        # used for testing
        return render(request, 'mystream.html', context=context)


'''
URL: ://service/author/logout
GET: logout account
'''


class LogoutView(View):
    def get(self, request):
        request.session.delete()  # delete session ，but not cookie
        logout(request)
        return redirect(reverse('Author:login'))


class UserInfoView(LoginRequiredMixin, View):
    pass


'''
URL: ://service/author/<id>
GET: retrieve a user's profile
'''


class UserProfileView(View):
    def get(self, request, id):
        # current logged in user
        curr_user = request.user
        # the author who is viewed
        view_user = User.objects.get(id=id)

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))

        try:
            github = view_user.github
            githubUname = github.split("/")[-1]
        except Exception:
            githubUname = None

        posts = Post.objects.filter(author_id=view_user.id).filter(visibility=1)

        paginator = Paginator(posts, per_page)
        page_object = paginator.page(page)

        context = {
            'id': id,
            'current_author': curr_user,
            'githubName': githubUname,
            'myPosts': posts,
            'page_object': page_object,
            'page_range': paginator.page_range,
            'view_author': view_user,
        }

        return render(request, 'author_profile.html', context=context)


'''
URL: ://service/author/authors/
GET: Read a list of all user using a given paginator
page: how many pages
size: how big is a page
'''


class AllUserProfileView(View):
    def get(self, request):
        curr_user = request.user
        # alternative approach, just use username
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        # something like only showing active user
        # user_status = int(request.GET.get("user_status",1))
        currentUser = request.user

        local_authors = User.objects.all()
        remote_authors = get_remote_authors()
        print("remote_authors:", remote_authors)
        authors = list(local_authors) + remote_authors

        paginator = Paginator(authors, per_page)
        page_object = paginator.page(page)
        serializer = UserSerializer(page_object, many=True)

        # time.sleep(5)
        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
            'page_size': per_page,
            'current_page': page,
            'current_author': currentUser,
            'current_host': request.META['HTTP_HOST']

        }
        print(currentUser.host)
        response = render(request, 'temp_for_all_authors_list.html', context=context)
        # response = render(request, 'all_authors_list.html', context=context)
        return response


# https://www.youtube.com/watch?v=-Vu7Kh-SxEA
# https://docs.djangoproject.com/en/3.2/topics/db/search/
# the view to list all searched user

'''
URL: ://service/author/logout
GET: search
q: (part of) intended username
page: how many pages
size: how big is a page
'''


class SearchUserView(View):
    def get(self, request):
        authorName = request.GET.get("q")
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        get_users_by_uname = User.objects.filter(username__icontains=authorName)
        currentUser = request.user

        paginator = Paginator(get_users_by_uname, per_page)
        page_object = paginator.page(page)

        # time.sleep(5)
        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
            'q': authorName,
            'page_size': per_page,
            'current_page': page,
            'current_author': currentUser,
        }
        return render(request, "temp_for_search_authors_list.html", context=context)


class UserPostsView(View):
    def get(self, request):
        pass


'''
URL: ://service/author/editProfile/
GET: visit edit profile page(need login)
POST: change profile by send post data of editable fields
'''


class UserEditProfileImageView(LoginRequiredMixin, View):
    def get(self, request):
        # current logged in user
        curr_user = request.user

        context = {
            'current_author': curr_user,
        }

        # used for testing

        return render(request, 'profile_img_edit.html', context=context)

    def post(self, request):
        json_data = []
        error_msg_dic = {
            "data": "",
            "msg": "",
            "code": ""
        }
        current_user = request.user
        image = request.FILES.get('img')
        if image:
            print("image:", image)
            name, fileformat = image.name.split('.')

            image64 = base64.b64encode(image.read())

            image64 = 'data:image/%s;base64,%s' % (fileformat, image64.decode('utf-8'))

            User.objects.filter(username=current_user.username).update(profile_image=image64)
            error_msg_dic["code"] = "200"
            error_msg_dic["msg"] = "Successfully update profile image"
            json_data.append(error_msg_dic)
            print("message OK")
        else:
            error_msg_dic["code"] = "400"
            error_msg_dic["msg"] = "Fail to upload the image, please try to upload again"
            json_data.append(error_msg_dic)
            print("fail to upload")
        return HttpResponse(json.dumps(json_data))


class UserEditInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # current logged in user
        curr_user = request.user

        context = {
            'current_author': curr_user,
        }

        # used for testing

        return render(request, 'profile_edit.html', context=context)

    def post(self, request):
        json_data = []
        error_msg_dic = {
            "data": "",
            "msg": "",
            "code": ""
        }
        current_user = request.user
        '''
        image = request.FILES.get('img')
        if image:
            print("image:", image)
            name, fileformat = image.name.split('.')

            image64 = base64.b64encode(image.read())

            image64 = 'data:image/%s;base64,%s' % (fileformat, image64.decode('utf-8'))

            User.objects.filter(username=current_user.username).update(profile_image=image64)
            error_msg_dic["code"] = "200"
            error_msg_dic["msg"] = "Successfully update profile image"
            json_data.append(error_msg_dic)
            print("message OK")
            return HttpResponse(json.dumps(json_data))

        else:
        '''
        username = request.POST.get('username')
        # username = request.POST['username']
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        github = request.POST.get('github')

        print("receive edit profile information")

        if not all([username, first_name, last_name, email]):
            error_msg_dic["code"] = "400"
            error_msg_dic["msg"] = "data missing"
            json_data.append(error_msg_dic)
            return HttpResponse(json.dumps(json_data))

        print(username)
        print(first_name)
        print(last_name)
        print(github)
        print(email)
        old_username = current_user.username

        try:
            exist_user = User.objects.get(username=username)
        except User.DoesNotExist:
            # new username is unique
            exist_user = None

        if exist_user is None or exist_user.id == current_user.id:
            update_user = User.objects.get(id=current_user.id)
            # update_user.username = username
            update_user.email = email
            update_user.first_name = first_name
            update_user.last_name = last_name
            update_user.github = github
            # update_user.update(username=username, email=email, first_name=first_name,last_name=last_name, github=github)
            update_user.save()
            error_msg_dic["code"] = "200"
            error_msg_dic["msg"] = "Successfully update"
            json_data.append(error_msg_dic)

        else:
            error_msg_dic["code"] = "403"
            error_msg_dic["msg"] = "Cannot update cause the username is already taken"
            json_data.append(error_msg_dic)
        return HttpResponse(json.dumps(json_data))


# Lagacy inbox
class InboxView(View):

    def get(self, request, id):
        curr_user = request.user
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        friReqs = FriendRequest.objects.filter(receiver_id=curr_user.id)

        # inbox = Inbox.objects.filter(requests=friReqs)

        paginator = Paginator(friReqs, per_page)
        page_object = paginator.page(page)

        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
        }

        response = render(request, 'temp_inbox.html', context=context)

        return response


# Intergrated inbox to sidebars for friend request
class InterFRInboxView(View):

    def get(self, request):
        curr_user = request.user
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        inbox = Inbox.objects.filter(author_id=curr_user.id)
        item_list = []
        for inb in inbox:
            for item in inb.items:
                if item["type"] == "follow":
                    try:
                        if item['request_id']:
                            item_list.append(item)
                    except:
                        continue
        print(item_list)
        # inbox = Inbox.objects.filter(requests=friReqs)
        paginator = Paginator(item_list, per_page)
        page_object = paginator.page(page)

        context = {
            'current_author': curr_user,
            'page_object': page_object,
            'page_range': paginator.page_range,
        }

        response = render(request, 'temp_inbox.html', context=context)

        return response


# Intergrated inbox to sidebars for posts part
class InterPostInboxView(View):
    def get(self, request):
        curr_user = request.user
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        inbox = Inbox.objects.filter(author_id=curr_user.id)
        item_list = []
        for inb in inbox:
            print(inb.author_id)
            for item in inb.items:
                print(item)
                if item['type'] == 'post':
                    item_list.append(item)

        paginator = Paginator(item_list, per_page)
        page_object = paginator.page(page)
        print(item_list)
        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
            'page_size': per_page,
            'current_page': page,
            'current_author': curr_user,
        }

        response = render(request, 'temp_inbox_posts.html', context=context)

        return response


class InterLikeInboxView(View):
    def get(self, request):
        curr_user = request.user
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        inbox = Inbox.objects.filter(author_id=curr_user.id)
        item_list = []
        for inb in inbox:
            for item in inb.items:
                if item["type"] == "like":
                    try:
                        if item['post']:
                            item_list.append(item)
                    except:
                        pass

        print(item_list)
        paginator = Paginator(item_list, per_page)
        page_object = paginator.page(page)

        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
            'page_size': per_page,
            'current_page': page,
            'current_author': curr_user,
        }

        response = render(request, 'temp_inbox_likes.html', context=context)

        return response


'''
URL: ://service/author/myposts
GET: retrive all posts made by current author, could be filtered by post type and patched by paginator
status: the status code of post, 0 for all, 1 for public 2 for private....
page: number of page
'''


class UserPostsView(View):
    def get(self, request):
        username = request.session.get('username', '')
        if not username:
            return HttpResponseRedirect(reverse('Author:login'))
        else:
            # list_item_insert = []
            # for i in range(100):
            #     list_item_insert.append(
            #         List(list_title="test title" + str(i), list_context="test content" + str(i), wxu_openid="15639616556"))
            #     print(list_item_insert)
            # List.objects.bulk_create(list_item_insert)
            # return HttpResponse("ok")
            curr_user = request.user

            list_send_num = Post.objects.filter(author_id=curr_user.id).filter(visibility=1).count()
            list_receive_num = Post.objects.filter(author_id=curr_user.id).filter(visibility=2).count()
            list_solve_num = Post.objects.filter(author_id=curr_user.id).filter(visibility=3).count()
            list_max = Post.objects.filter(author_id=curr_user.id).count()

            page_num_int = int(request.GET.get('page', 1))
            question_list = []
            list_status = int(request.GET.get('status', 0))

            if list_status > 0:
                question_list = Post.objects.filter(author_id=curr_user.id).filter(visibility=list_status).order_by(
                    'visibility')
            else:
                question_list = Post.objects.filter(author_id=curr_user.id).order_by('visibility')
            paginator = Paginator(question_list, 10)

            # if paginator.num_pages > 11:
            #
            #     if page_num_int - 5 < 1:
            #         page_range = range(1, 11)
            #     elif page_num_int + 5 > paginator.num_pages:
            #         page_range = range(paginator.num_pages - 10, paginator.num_pages + 1)
            #     else:
            #         page_range = range(page_num_int - 5, page_num_int + 5)
            # else:
            #     page_range = paginator.page_range

            page = paginator.page(page_num_int)
            # for list_item in page:
            #     list_item["timespan"] = get_timespan(list_item.create_time)
            data = {
                'status': list_status,
                'list_send_num': list_send_num,
                'list_receive_num': list_receive_num,
                'list_solve_num': list_solve_num,
                'list_max': list_max,
                'page': page,
                'recordset_max': question_list.count(),
                'page_num_int': page_num_int,
                'page_count_start': 10 * (page_num_int - 1) + 1,
                'page_count_end': 10 * (page_num_int - 1) + 10,
                'current_author': curr_user,
            }
            return render(request, 'myposts.html', data)


'''
URL: ://service/author/mystream
GET: retrive github pages and all posts that are accessble by current author
page:number of pages
size: # of posts each page
'''


class MyStreamView(LoginRequiredMixin, View):
    def get(self, request):
        # current logged in user
        curr_user = request.user

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        posts = Post.objects.filter(visibility=1)
        # inbox = Inbox.objects.filter(requests=friReqs)

        paginator = Paginator(posts, per_page)
        page_object = paginator.page(page)

        try:
            github = curr_user.github
            githubUname = github.split("/")[-1]
        except Exception:
            githubUname = None

        context = {
            'id': id,
            'current_author': curr_user,
            'githubName': githubUname,
            'myPosts': posts,
            'page_object': page_object,
            'page_range': paginator.page_range,
        }

        # used for testing
        return render(request, 'mystream.html', context=context)


'''
URL: ://service/author/allPublicPosts
GET: retrive all public posts
page:number of pages
size: # of posts each page
'''


class AllPublicPostsView(View):
    def get(self, request):
        curr_user = request.user
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        currentUser = request.user

        local_public_posts = Post.objects.filter(visibility=1)

        # remote_posts = get_remote_public_posts()
        remote_posts = get_all_remote_public_posts_through_remote_authors()

        all_pub_posts = list(local_public_posts) + remote_posts

        paginator = Paginator(all_pub_posts, per_page)
        page_object = paginator.page(page)

        context = {
            'curr_host': request.META['HTTP_HOST'],
            'page_object': page_object,
            'page_range': paginator.page_range,
            'page_size': per_page,
            'current_page': page,
            'current_author': currentUser,
        }

        response = render(request, 'all_public_posts_list.html', context=context)
        return response


# https://www.shuzhiduo.com/A/Ae5R8BeMzQ/

'''API views below'''
# http://127.0.0.1:8000/author/api/authors?page=1&size=1
'''
[{
    "id": "53e061a9-d963-4565-9c70-6f7fc4095712",
    "username": "XZPshaw",
    "profile_image": "",
    "email": "123123123@123.com",
    "first_name": "Ze",
    "last_name": "Xiao",
    "github": "https://github.com/zqq66"
}]
'''

'''''''''''''''                                author/author's post related API                      '''''''''''''''


class APIAllProfileView(APIView):
    def get(self, request):
        # alternative approach, just use username
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        # something like only showing active user
        # user_status = int(request.GET.get("user_status",1))
        authors = User.objects.all().order_by("created")

        paginator = Paginator(authors, per_page)
        page_object = paginator.page(page)
        serializer = UserSerializer(page_object, many=True)
        response = Response()
        response.status_code = 200
        data = {
            "types": "authors",
            "items": serializer.data
        }
        response.data = data
        # response = render(request, 'temp_for_all_authors_list.html', context=context)
        # response = render(request, 'all_authors_list.html', context=context)
        return response


'''
GET http://127.0.0.1:8000/author/api/53e061a9-d963-4565-9c70-6f7fc4095712/
{
    "id": "53e061a9-d963-4565-9c70-6f7fc4095712",
    "username": "XZPshaw",
    "profile_image": "",
    "email": "123123123@123.com",
    "first_name": "Ze",
    "last_name": "Xiao",
    "github": "https://github.com/zqq66"
}
'''


class APIAuthorProfileView(APIView):
    def get(self, request, id):
        # the author who is viewed
        try:
            view_user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(view_user)
        response = Response()
        response.status_code = 200
        response.data = serializer.data
        return response

    ##update user info

    def post(self, request, id):
        try:
            update_user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user_serializer = UserSerializer(update_user, data=request.data, partial=True)
        if user_serializer.is_valid():
            update_user = user_serializer.save()

            update_user.host = request.META['HTTP_HOST']
            update_user.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(
                update_user.id) + "/"
            update_user.api_url = request.build_absolute_uri()
            update_user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# the posts of this particular author
class APIAuthorPostsView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        view_user = User.objects.get(id=id)
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 5))

        posts = Post.objects.filter(author_id=view_user.id).order_by("published")

        paginator = Paginator(posts, per_page)
        page_object = paginator.page(page)
        serializer = PostSerializer(page_object, many=True)

        response = Response()
        response.status_code = 200
        data = {
            "types": "posts",
            "items": serializer.data
        }
        response.data = data

        # response = render(request, 'temp_for_all_authors_list.html', context=context)
        # response = render(request, 'all_authors_list.html', context=context)
        return response


'''''''''''''''                                Post related API                      '''''''''''''''


# todo:determine wether or not only return public posts
class APIAllPosts(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        # something like only showing active user
        # user_status = int(request.GET.get("user_status",1))
        posts = Post.objects.all().order_by("-published")
        # posts = Post.objects.filter(visibility="PUBLIC")

        paginator = Paginator(posts, per_page)
        page_object = paginator.page(page)
        serializer = PostSerializer(page_object, many=True)
        response = Response()
        response.status_code = 200

        data = {
            "type": "posts",
            "items": serializer.data
        }

        response.data = data

        # response = render(request, 'temp_for_all_authors_list.html', context=context)
        # response = render(request, 'all_authors_list.html', context=context)
        return response


class APIPostByIdView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId, postId):
        view_user = User.objects.get(id=authorId)
        view_post = Post.objects.get(id=postId)
        post_comments = view_post.comments

        user_serializer = UserSerializer(view_user)
        post_serializer = PostSerializer(view_post)
        comments_serializer = CommentSerializer(post_comments)

        response = Response()
        response.status_code = 200
        response.data = post_serializer.data

        return response

    def post(self, request, authorId, postId):
        pass

    def put(self, request, authorId, postId):

        author = User.objects.get(id=authorId)
        response = Response()
        data = json.loads(request.body)
        print(data)
        try:
            post = Post.objects.get(id=postId)
        except Exception:
            pass
        else:
            response.status_code = 404  # the post_id is occupied and cannot create post
            response.data = 'the post id is occupied, please try with a different id'
            return response

        if data['type'] != 'post':
            response.status_code = 404
            response.data = 'type is not post'
            return response

        author = request.user
        try:
            title = data['title']
            content_type = data['content_type']
            content = data['content']
            categories = data['categories']
            categories = process_categories(categories)
            description = data['description']
            visibility = int(data['visibility'])
        except Exception:
            response.status_code = 404
            response.data = 'required info missing'
            return response

        if 'source' in data:
            source = data['source']
        else:
            source = request.build_absolute_uri(request.path)
        if 'origin' in data:
            origin = data['origin']
        else:
            origin = request.build_absolute_uri(request.path)
        unlisted = False  # TODO

        if 'select_user' in data:
            select_user = data['select_user']
        else:
            select_user = ''
        if select_user != '' and visibility == 3:
            try:
                user = User.objects.get(username=select_user)  # TODO: might be foreign author
            except Exception:
                return HttpResponse("Failed: No such user.")
        try:
            image = request.FILES['img']
        except Exception:
            image64 = ''
        else:
            name, fileformat = image.name.split('.')
            image64 = base64.b64encode(image.read())
            image64 = 'data:image/%s;base64,%s' % (fileformat, image64.decode('utf-8'))
            print(image64)
        post = Post.objects.create(title=title, id=postId, source=source, origin=origin, description=description,
                                   contentType=content_type, content=content, author=request.user,
                                   categories=categories,
                                   visibility=visibility, unlisted=unlisted, select_user=select_user, image=image64)

        if post.author.url != "":
            post.url = post.author.url + "posts/" + post.id + "/"
            post.api_url = post.author.api_url + "posts/" + post.id + "/"
        else:
            post.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(
                post.author.id) + "/posts/" + post.id + "/"
            post.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(
                post.author.id) + "/posts/" + post.id + "/"

        if visibility == 3:
            user = User.objects.get(username=select_user)
            inbox, status = Inbox.objects.get_or_create(author=user)
            inbox.items.append(PostSerializer(post).data)
            inbox.save()
        elif visibility == 2:
            try:
                friends = Friend.objects.get(user=author)
                for friend in friends.friends:
                    print(friend)
                    fri_obj = User.objects.get(id=friend['uuid'])
                    inbox, status = Inbox.objects.get_or_create(author=fri_obj)
                    print(inbox.items)
                    inbox.items.append(PostSerializer(post).data)
                    inbox.save()
            except:
                pass
        post.save()
        response.status_code = 200
        return response


'''''''''''''''                                Comment/Like related API                      '''''''''''''''


class APICommentsByPostId(APIView):
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request, authorId, postId):
        view_user = User.objects.get(id=authorId)
        view_post = Post.objects.get(id=postId)
        post_comments = view_post.comments

        user_serializer = UserSerializer(view_user)
        post_serializer = PostSerializer(view_post)
        comments_serializer = CommentSerializer(post_comments, many=True)

        response = Response()
        response.status_code = 200
        data = {
            "types": "comments",
            "items": comments_serializer.data
        }
        response.data = data
        return response

    def post(self, request, authorId, postId):
        print("author:", authorId)
        data = request.data
        print("data", data)
        author_comment1 = data["author"]
        comment_content = data["comment"]
        comment_contentType = data["contentType"]  # TODO: add contentType to Comment and add md
        author_post = User.objects.get(id=authorId)
        local_post = Post.objects.get(id=postId)
        print("postId", postId)

        comment = PostComment.objects.create(post=local_post, author_comment=author_post, author=author_comment1,
                                             comment=comment_content)
        api_url1 = "http://" + request.scheme + request.META["HTTP_HOST"] + '/api' + '/author/' + str(
            authorId) + "/posts/" + str(postId) + "/comments/" + str(comment.id_comment)
        comment.api_url = api_url1
        comment.save()
        local_post.count = local_post.count + 1
        local_post.save()

        response = Response()
        response.status_code = 200
        response.data = data
        return response


class APIComment(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId, postId, commentId):
        comment = PostComment.objects.get(id_comment=commentId)
        comment_serializer = CommentSerializer(comment)
        response = Response()
        response.status_code = 200
        response.data = comment_serializer.data
        return response


class APICommentsByAuthorId(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId):
        pass


class APILikesByAuthorId(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId):
        pass


'''''''''''''''                                Inbox related API                      '''''''''''''''


class APIInbox(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId):
        try:
            inbox, created = Inbox.objects.get_or_create(author_id=authorId)
        except Inbox.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = InboxSerializer(inbox)
        response = Response()
        response.status_code = 200
        response.data = serializer.data
        return response

    def post(self, request, authorId):
        ##the inbox data sent by other servers
        data = request.data
        local_author = User.objects.get(id=authorId)

        inbox, created = Inbox.objects.get_or_create(author_id=authorId)
        if data['type'].lower() == "follow":
            try:
                remote_author = data["actor"]
            except Exception:
                remote_author = data["sender"]

            # local_author = data["receiver"]
            try:
                local_author = data["receiver"]["uuid"]
                local_author = User.objects.get(id=local_author)
            except Exception:
                local_author = User.objects.get(api_url=data["object"]["url"])

            friend_request = FriendRequest.objects.create(sender=remote_author,
                                                          receiver=UserSerializer(local_author).data)
            inbox.items.append(FriendRequestSerializer(friend_request).data)
            inbox.save()
            # add remote author to follower list of local author
            #             follower, create_follower = Follower.objects.get_or_create(user=local_author)

            # follower.add_follower(UserSerializer(remote_author).data)
            #             follower.add_follower(remote_author)
            response = Response()
            response.data = data
            response.status_code = 200
            return response
        # todo:handle post api for like from remote author
        elif data['type'].lower() == "like":

            print("here")
            remote_author = data['author']
            like_object = data['object']

            liked_post = Post.objects.get(api_url=like_object)
            try:
                like = PostLike.objects.create(post=liked_post, author=remote_author, object=like_object)
                inbox.items.append(LikeSerializer(like).data)
                inbox.save()
                response = Response()
                response.status_code = 200
            except:
                response=Response()
                response.status_code = 222
            return response

        # todo:handle post api for friend post/private post from remote author
        elif data['type'].lower() == "post":
            '''
            remote_author = data['author']
            post_object = data['object']
            this_post = Post.objects.get(api_url=post_object)
            inbox.items.append(PostSerializer(this_post).data)
            '''
            inbox.items.append(data)
            inbox.save()
            response = Response()
            response.status_code = 200
            return response

    def delete(self, request, authorId):
        Inbox.objects.get(author_id=authorId).delete()
        response = Response()
        response.status_code = 200
        return response


"""remote author related view"""


class Remote_Author_Profile_View(View):
    def get(self, request):
        curr_user = request.user

        authorAPIUrl = request.GET.get("url")
        authorAPIUrl = urllib.parse.unquote(authorAPIUrl)
        author_request = make_api_get_request(authorAPIUrl)
        print("author_request", author_request)
        remote_author = author_request.json()

        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))

        try:
            github = remote_author.github
            githubUname = github.split("/")[-1]
        except Exception:
            githubUname = None

        posts_url = authorAPIUrl + "/posts"
        posts_request = make_api_get_request(posts_url)

        print(posts_request.json())
        try:
            remote_posts = posts_request.json()["items"]
        except Exception:
            if type(posts_request.json()) == list:
                remote_posts = posts_request.json()

            else:
                remote_posts = posts_request.json()["item"]
        paginator = Paginator(remote_posts, per_page)
        page_object = paginator.page(page)

        context = {
            'current_author': curr_user,
            'githubName': githubUname,
            'myPosts': remote_posts,
            'page_object': page_object,
            'page_range': paginator.page_range,
            'view_author': remote_author,
        }
        print(context)
        return render(request, 'remote_author_profile.html', context=context)

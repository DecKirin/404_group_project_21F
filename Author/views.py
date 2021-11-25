import re
import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites import requests
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import renderer_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from rest_framework.renderers import TemplateHTMLRenderer
import urllib
from Author.serializers import UserSerializer, PostSerializer, CommentSerializer, InboxSerializer
from friends.models import FriendRequest
from Post.serializers import LikeSerializer
from Author.models import User, RegisterControl, Inbox, Post, Node
from Post.models import PostComment,PostLike
# Create your views here.
from django.views import View
from django.contrib.auth import authenticate, login, logout
import requests
from requests.auth import HTTPBasicAuth
from friends.serializers import FriendRequestSerializer
from social_network.settings import SECRET_KEY

def make_api_get_request(api_url):
    proxies = {
        "http": "http://192.168.1.4",
        "https": "http://127.0.0.1:7890"
    }
    request = requests.get(api_url, proxies=proxies, verify=True)
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
    all_host = [node.host for node in nodes]
    print(all_host)
    return all_host


def get_remote_authors():
    all_remote_host = get_remote_nodes()

    authors = []
    for host in all_remote_host:
        api_uri = host + '/api' + '/authors/'
        print(api_uri)
        ####todo:authentication information
        ####request = requests.get(api_uri, auth=HTTPBasicAuth(auth_user, auth_pass))
        request = requests.get(api_uri)
        if request.status_code == 200:
            authors_in_host = request.json()
            authors += authors_in_host
    # print(authors)
    return authors


def get_remote_public_posts():
    all_remote_host = get_remote_nodes()

    posts = []
    for host in all_remote_host:
        api_uri = host + '/api' + '/posts/'
        request = requests.get(api_uri)
        if request.status_code == 200:
            posts_in_host = request.json()
            posts += posts_in_host
    return posts


'''
URL: ://service/author/register
GET: visit register page
POST: submit an author account registeration
'''


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
                                        last_name=userlname, is_active=is_active)
        # user.is_active = 1
        user.host = request.META['HTTP_HOST']
        user.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(user.id) + "/"
        user.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(user.id) + "/"

        user.save()
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
        }

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
        username = request.POST.get('username')
        # username = request.POST['username']
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        github = request.POST.get('github')

        '''
        old_username = current_user.username

        try:
            exist_user = User.objects.get(username=username)
        except User.DoesNotExist:
            # new username is unique
            exist_user = None


        if exist_user is None or exist_user.id == current_user.id:
            User.objects.filter(username=current_user.username).update(username=username, email=email, first_name=first_name,last_name=last_name, github=github)
            messages.success(request, "Your change has been saved!")
            return HttpResponseRedirect(reverse("Author:index"))

        else :
            error_msg_dic["code"] = "403"
            error_msg_dic["msg"] = "Cannot update cause the username is already taken"
            json_data.append(error_msg_dic)
            messages.error(request, "This username is taken by someone else")
            return render(request, 'profile_edit.html', context=json_data)
        '''
        User.objects.filter(username=current_user.username).update(email=email,
                                                                   first_name=first_name, last_name=last_name,
                                                                   github=github)
        return HttpResponseRedirect(reverse("Author:mystream"))

#Lagacy inbox
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

        # inbox = Inbox.objects.filter(requests=friReqs)
        paginator = Paginator(item_list, per_page)
        page_object = paginator.page(page)

        context = {
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
            for item in inb.items:
                if item["type"] == "post":
                    item_list.append(item)

        paginator = Paginator(item_list, per_page)
        page_object = paginator.page(page)

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
                if item["type"] == "post":
                    item_list.append(item)

        paginator = Paginator(item_list, per_page)
        page_object = paginator.page(page)

        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
            'page_size': per_page,
            'current_page': page,
            'current_author': curr_user,
        }

        response = render(request, 'temp_inbox_posts.html', context=context)

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

        remote_posts = get_remote_public_posts()

        all_pub_posts = list(local_public_posts) + remote_posts

        paginator = Paginator(all_pub_posts, per_page)
        page_object = paginator.page(page)

        context = {
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
        response.data = serializer.data
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


# the posts of this particular author
class APIAuthorPostsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
        response.data = serializer.data
        # response = render(request, 'temp_for_all_authors_list.html', context=context)
        # response = render(request, 'all_authors_list.html', context=context)
        return response


'''''''''''''''                                Post related API                      '''''''''''''''


# todo:determine wether or not only return public posts
class APIAllPosts(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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
        response.data = serializer.data
        # response = render(request, 'temp_for_all_authors_list.html', context=context)
        # response = render(request, 'all_authors_list.html', context=context)
        return response


class APIPostByIdView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
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


'''''''''''''''                                Comment/Like related API                      '''''''''''''''


class APICommentsByPostId(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId, postId):
        view_user = User.objects.get(id=authorId)
        view_post = Post.objects.get(id=postId)
        post_comments = view_post.comments

        user_serializer = UserSerializer(view_user)
        post_serializer = PostSerializer(view_post)
        comments_serializer = CommentSerializer(post_comments, many=True)

        response = Response()
        response.status_code = 200
        response.data = comments_serializer.data
        return response

    def post(self, request, authorId, postId):
        pass


class APIComment(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId, postId, commentId):
        comment = PostComment.objects.get(id_comment=commentId)
        comment_serializer = CommentSerializer(comment)
        response = Response()
        response.status_code = 200
        response.data = comment_serializer.data
        return response


class APICommentsByAuthorId(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId):
        pass


class APILikesByAuthorId(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId):
        pass


'''''''''''''''                                Inbox related API                      '''''''''''''''


class APIInbox(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, authorId):
        try:
            inbox = Inbox.objects.get(author_id=authorId)
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
            remote_author = data['sender']
            friend_request = FriendRequest.objects.create(sender=remote_author,
                                                          receiver=UserSerializer(local_author).data)
            inbox.items.append(FriendRequestSerializer(friend_request).data)
            inbox.save()
            response = Response()
            response.status_code = 200
            return response
        # todo:handle post api for like from remote author
        elif data['type'].lower() == "like":
            remote_author = data['author']
            like_object = data['object']
            liked_post = Post.objects.get(api_url=like_object)
            like = PostLike.objects.create(post=liked_post, author=remote_author, object=like_object)
            inbox.items.append(LikeSerializer(like).data)
            inbox.save()
            response = Response()
            response.status_code = 200
            return response

        # todo:handle post api for friend post/private post from remote author
        elif data['type'].lower() == "post":
            remote_author = data['author']
            post_object = data['object']
            this_post = Post.objects.get(api_url=post_object)
            inbox.items.append(PostSerializer(this_post).data)
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
        remote_posts = posts_request.json()["items"]

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


import re
import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from friends.models import FriendRequest
import Author
from Author.models import User, RegisterControl, Inbox
# Create your views here.
from django.views import View
from django.contrib.auth import authenticate, login, logout

from social_network.settings import SECRET_KEY


def check_if_confirmation_required():
    try:
        confirm = RegisterControl.objects.all()
        assert confirm!=None and list(confirm)!=[],"raise"

    except Exception:
        registerControl = RegisterControl()
        registerControl.save()
        return registerControl.free_registration
    else:
        return list(confirm)[0].free_registration


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
            is_active= False
        user = User.objects.create_user(username=username, email=email, password=password, first_name=userfname,
                                        last_name=userlname, is_active=is_active)
        # user.is_active = 1
        user.save()
        error_msg_dic["code"] = "200"
        error_msg_dic["msg"] = "Successfully register"
        json_data.append(error_msg_dic)
        return HttpResponse(json.dumps(json_data))


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
            # return render(request, 'login.html', {'errmsg': '数据不完整'})
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
                error_msg_dic["code"] = "700"
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
                next_url = request.GET.get('next', reverse('Author:index'))

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
        username = request.session.get('username', '')
        if not username:
            return HttpResponseRedirect('author:login')
        else:
            curr_user = User.objects.get(username=username)
            #curr_user = request.user
            context = {
                'id': id,
                'current_author': curr_user,
            }

        return render(request, 'base_index.html', context=context)

    def post(self, request):
        return render(request, 'base_index.html')


class LogoutView(View):
    def get(self, request):
        request.session.delete()  # delete session ，but not cookie
        logout(request)
        return redirect(reverse('Author:login'))



class UserInfoView(LoginRequiredMixin, View):
    pass


class UserProfileView(View):
    def get(self, request, id):
        # current logged in user
        curr_user = request.user

        # the author who is viewed
        view_user = User.objects.get(id=id)
        # alternative approach, just use username
        #
        try:
            github = view_user.github
            githubUname = github.split("/")[-1]
        except Exception:
            githubUname=None

        context = {
            'id': id,
            'current_author': curr_user,
            'view_user': view_user,
            'githubName': githubUname,
        }

        # used for testing
        #return render(request, 'index2.html', context=context)
        return render(request, 'author_profile.html', context=context)


class AllUserProfileView(View):
    def get(self, request):
        curr_user = request.user
        # alternative approach, just use username
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        # something like only showing active user
        # user_status = int(request.GET.get("user_status",1))
        currentUser = request.user

        authors = User.objects.all()

        paginator = Paginator(authors, per_page)
        page_object = paginator.page(page)

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
            'current_page':page,
            'current_author': currentUser,
        }
        return render(request, "temp_for_search_authors_list.html", context=context)


class UserPostsView(View):
    def get(self, request):
        pass


class UserEditInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # current logged in user
        curr_user = request.user

        context = {
            'current_author': curr_user,
        }

        # used for testing
        # return render(request, 'index2.html', context=context)
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
        #username = request.POST['username']
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
        return HttpResponseRedirect(reverse("Author:index"))

class InboxView(View):

    def get(self, request, id):
        curr_user = request.user
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        friReqs = FriendRequest.objects.filter(receiver_id=curr_user.id)

        #inbox = Inbox.objects.filter(requests=friReqs)

        paginator = Paginator(friReqs, per_page)
        page_object = paginator.page(page)


        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
        }

        response = render(request, 'temp_inbox.html', context=context)

        return response


class UserPostsView(View):
    pass

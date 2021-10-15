import re
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

import Author
from Author.models import User
# Create your views here.
from django.views import View
from django.contrib.auth import authenticate, login, logout

from social_network.settings import SECRET_KEY


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
        # 校验用户名是否重复
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

        user = User.objects.create_user(username=username, email=email, password=password, first_name=userfname,
                                        last_name=userlname)
        user.is_active = 1
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

        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            # return render(request, 'login.html', {'errmsg': '数据不完整'})
            error_msg_dic["code"] = "500"
            error_msg_dic["msg"] = "data missing"
            json_data.append(error_msg_dic)
            return HttpResponse(json.dumps(json_data))
        # 业务处理:登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            '''
            if user.is_delete:
                error_msg_dic["code"] = "700"
                error_msg_dic["msg"] = "用户未开通"
                json_data.append(error_msg_dic)
                return HttpResponse(json.dumps(json_data))
            '''
            if user.is_active:
                # user account is an active one
                # 记录用户的登录状态
                login(request, user)

                # 获取登录后所要跳转到的地址
                # 默认跳转到首页
                next_url = request.GET.get('next', reverse('Author:index'))

                # # 跳转到next_url
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

                # 返回response
                return response_index
                # return response
            else:
                # User account is not active
                error_msg_dic["code"] = "700"
                error_msg_dic["msg"] = "Not An Active Account,Please Contact Administrator"
                json_data.append(error_msg_dic)
                print(json_data)
                return HttpResponse(json.dumps(json_data))
        else:
            # Username or Password not correct
            # return render(request, 'login.html', {'errmsg': 'Username or Password not correct'})
            error_msg_dic["code"] = "700"
            error_msg_dic["msg"] = "Username or Password not correct"
            json_data.append(error_msg_dic)
            print(json_data)
            return HttpResponse(json.dumps(json_data))


# /user/
class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        username = request.session.get('username', '')
        if not username:
            return HttpResponseRedirect('author:login')
        else:
            user = User.objects.get(username=username)
        return render(request, 'index.html', {'username': username})

    def post(self, request):
        return render(request, 'index.html')


class LogoutView(View):
    def get(self, request):
        request.session.delete()  # delete session ，but not cookie
        logout(request)
        return redirect(reverse('Author:login'))


class UserPostsView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(request, '')


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
        context = {
            'id': id,
            'curr_user': curr_user,
            'view_user': view_user,
        }
        return render(request, 'author_profile.html', context=context)


class AllUserProfileView(View):
    def get(self, request):
        curr_user = request.user
        # alternative approach, just use username
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("size", 10))
        # something like only showing active user
        # user_status = int(request.GET.get("user_status",1))

        authors = User.objects.all()

        paginator = Paginator(authors, per_page)
        page_object = paginator.page(page)

        # time.sleep(5)
        context = {
            'page_object': page_object,
            'page_range': paginator.page_range,
        }

        response = render(request, 'all_authors_list.html', context=context)
        return response

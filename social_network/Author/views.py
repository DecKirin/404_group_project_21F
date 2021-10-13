import re
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from Author.models import User
# Create your views here.
from django.views import View
from django.contrib.auth import authenticate, login

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
        #allow = request.POST.get('allow')
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
        user = User.objects.create_user(username, email, password, first_name=userfname, last_name=userlname)
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
            error_msg_dic["msg"] = "数据不完整"
            json_data.append(error_msg_dic)
            return HttpResponse(json.dumps(json_data))
        # 业务处理:登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_delete:
                error_msg_dic["code"] = "700"
                error_msg_dic["msg"] = "用户未开通"
                json_data.append(error_msg_dic)
                return HttpResponse(json.dumps(json_data))
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)

                # 获取登录后所要跳转到的地址
                # 默认跳转到首页
                next_url = request.GET.get('next', reverse('web:index'))

                # # 跳转到next_url
                # response = redirect(next_url)  # HttpResponseRedirect

                error_msg_dic["code"] = "200"
                error_msg_dic["msg"] = "用户验证成功"
                json_data.append(error_msg_dic)
                print(json_data)
                request.session["username"] = username
                response_index = HttpResponse(json.dumps(json_data))

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')

                # request.set_signed_cookie('username', username, max_age=7 * 24 * 3600)
                if remember == 'true':
                    # 记住用户名
                    response_index.set_signed_cookie('username', username, SECRET_KEY, max_age=7 * 24 * 3600)
                    response_index.set_signed_cookie('remember', 'checked', SECRET_KEY, max_age=7 * 24 * 3600)
                else:
                    response_index.delete_cookie('username')
                    response_index.delete_cookie('remember')

                # 返回response
                return response_index
                # return response
            else:
                # 用户未激活
                error_msg_dic["code"] = "700"
                error_msg_dic["msg"] = "用户暂未激活,请联系管理员"
                json_data.append(error_msg_dic)
                print(json_data)
                return HttpResponse(json.dumps(json_data))
        else:
            # 用户名或密码错误
            # return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
            error_msg_dic["code"] = "700"
            error_msg_dic["msg"] = "用户名或密码不正确"
            json_data.append(error_msg_dic)
            print(json_data)
            return HttpResponse(json.dumps(json_data))

# /user/
class UserInfoView(View):
    def get(self, request):
        return render(request, 'user_center_info.html', {'page': 'user'})

class LogoutView(View):
    def get(self,request):
        return render(request, '')


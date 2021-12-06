import json
import urllib
from urllib.parse import urlparse
from django.utils import timezone

import requests
from django.core.paginator import Paginator
from django.views import View
from requests.auth import HTTPBasicAuth
from rest_framework.views import APIView

from Author.models import User, Inbox, Post
from Author.serializers import PostSerializer, UserSerializer
from Post.serializers import CommentSerializer, LikeSerializer
from friends.models import Friend
from rest_framework.response import Response
import uuid
from rest_framework import serializers
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from Post.models import PostLike, PostComment
from Author.views import make_api_get_request
import base64
from PIL import Image
from io import BytesIO
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

'''
# use this one if you need to connect with vpn
def make_api_post_request(api_url, json_object):
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
    request = requests.post(api_url, data=json_object, auth=HTTPBasicAuth("team11", "secret11"), proxies=proxies)
    if request.status_code in [403, 401]:
        request = requests.get(api_url, data=json_object, proxies=proxies, auth=HTTPBasicAuth("7c70c1c8-04fe-46e0-ae71-8969061adac0", "123456"), verify=True)
    return request
'''


# use this one if you do not need vpn

def make_api_post_request(api_url, json_object):
    request = requests.post(api_url, data=json_object, auth=HTTPBasicAuth("team11", "secret11"))
    if request.status_code in [403, 401]:
        request = requests.get(api_url, data=json_object,
                               auth=HTTPBasicAuth("7c70c1c8-04fe-46e0-ae71-8969061adac0", "123456"), verify=True)
    return request


def make_api_put_request(api_url, json_object):
    print("im mamking put request")
    request = requests.put(api_url, data=json_object, auth=HTTPBasicAuth("team11", "secret11"))
    if request.status_code in [403, 401]:
        request = requests.get(api_url, data=json_object,
                               auth=HTTPBasicAuth("7c70c1c8-04fe-46e0-ae71-8969061adac0", "123456"), verify=True)
    return request


# return relative path
def get_path(old_path):
    new_path = 'https://{' + urlparse(old_path) + '.hostname}'
    return new_path


def get_author_id(request, auth_id):
    ab_path = request.build_absolute_uri()
    re_path = get_path(ab_path)
    return f"{re_path}/author/{auth_id}"


def process_categories(categories):
    categories = categories.split(',')
    for i in range(len(categories)):
        categories[i] = categories[i].strip()
    return str(categories)


class NewPostView(View):
    def get(self, request):
        return render(request, 'new_post.html', None)

    def post(self, request):
        author = request.user
        title = request.POST.get('title', '')
        content_type = request.POST.get('content_type', '')
        content = request.POST.get('content', '')

        categories = request.POST.get('categories', '')
        categories = process_categories(categories)

        description = request.POST.get('description', '')
        unlisted = False  # TODO
        post_id = uuid.uuid4().hex
        post_id = str(post_id)
        visibility = int(request.POST.get('visibility', ''))

        select_user = request.POST.get('select_user', '')
        if select_user != '' and visibility == 3:
            try:
                user = User.objects.get(username=select_user)
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
            # print(image64)

        post = Post.objects.create(title=title, id=post_id, description=description,
                                   contentType=content_type, content=content, author=request.user,
                                   categories=categories,
                                   visibility=visibility, unlisted=unlisted, select_user=select_user, image=image64)
        # image_url = post.image.url
        # print(image_url)
        #
        # with open(image_url, "rb") as image_file:
        #     data = base64.b64encode(image_file.read())

        if post.author.url != "":
            post.url = post.author.url + "posts/" + post.id + "/"
            post.api_url = post.author.api_url + "posts/" + post.id + "/"
        else:
            post.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(
                post.author.id) + "/posts/" + post.id + "/"
            post.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(
                post.author.id) + "/posts/" + post.id + "/"
        post.source = post.url
        post.origin = post.url
        if visibility == 3:
            user = User.objects.get(username=select_user)
            inbox, status = Inbox.objects.get_or_create(author=user)
            inbox.items.append(PostSerializer(post).data)
            inbox.save()
        elif visibility == 2:
            try:
                friends = Friend.objects.get(user=author)
                for friend in friends.friends:
                    if friend['host'] == author.host:
                        fri_obj = User.objects.get(id=friend['uuid'])
                        inbox, status = Inbox.objects.get_or_create(author=fri_obj)
                        print(inbox.items)
                        inbox.items.append(PostSerializer(post).data)
                        inbox.save()
                    else:
                        # author_serilized = UserSerializer(author).data
                        data = PostSerializer(post).data
                        inbox_url = ''
                        try:
                            remote_author_api_url = friend["url"]

                        except Exception:
                            remote_author_api_url = friend["id"]

                        if remote_author_api_url[-1] == '/':
                            inbox_url = remote_author_api_url + 'inbox'
                        else:
                            inbox_url = remote_author_api_url + '/inbox'

                        request = requests.post(inbox_url, json.dumps(data), auth=HTTPBasicAuth("team11", "secret11"))

            except Exception:
                pass
        post.save()
        return redirect(reverse('Author:index'))

    def select_private(self, request):  # TODO
        return None


# with post_id
class PostsView(View):
    # GET
    def get_id_post(self, request, *args, **kwargs):
        post_id = request.get('id', '')
        posts = Post.objects.get(id=post_id)
        inf_ret = PostSerializer(posts)
        return Response(inf_ret.data)

    def get_author_posts(self, request, *args, **kwargs):
        author_id = request.user
        author_posts = Post.objects.filter(author=author_id)
        inf_ret = PostSerializer(author_posts, many=True)
        return Response(inf_ret.data)

    def get_valid_post(self, request, *args, **kwargs):
        author_id = request.user.id
        inf_ret = []
        all_posts = Post.objects.all()
        for post in all_posts:
            if post.visibility == "1":
                inf_ret.append(post)
            elif post.visibility == "2":
                if Friend.objects.filter(friends=author_id):
                    inf_ret.append(post)
            elif post.visibility == "3":
                if self.check_private_spe(request, post, author_id):
                    inf_ret.append(post)
        return Response(inf_ret)

    def check_private_spe(self, request, post, author_id):  # TODO
        return True

    '''
    def put_post(self,request,*args, **kwargs):
        author_id = request.user
        post_id = request.get('id', '')
        posts = Post.objects.get(id=post_id)
        title = request.data.get('title', '')
        contentType = request.data.get('contentType', '')
        content =request.data.get('content', '')
        
        categories = request.data.get('categories', '')
    
        #comments = request.data.get('comments', '')
        description = request.data.get('description ', '')
        visibility = request.data.get('visibility', '')
        if title is not None:
            posts.title = title
        if contentType is not None:
            posts.contentType = contentType
        if content is not None:
            posts.content = content
        if categories is not None:
            posts.categories = categories
        if description_update is not None:
            posts.description = description_update
        if visibilitye is not None:
            posts.visibility = visibility
        posts.save()
        
        if visibility=="2":
            inf_ret = Friend.objects.filter(friends=author_id)
            if inf_ret is not None:
                all_friend = Friend.objects.get(friends=author_id)
                for friend in all_friend:
                    inbox = Inbox.objects.get(author=friend)
                    inbox.items.append(data1)
                    inbox.save()
        #TODO: select 3

        return Response(inf_store.data)

    # DELETE
    '''


class EditPostView(View):
    def get(self, request, author_id, post_id):
        cur_post = Post.objects.get(id=post_id)  # TODO: find the post
        categories = cur_post.categories[1:-1].split(',')
        print(categories)
        for i in range(len(categories)):
            categories[i] = categories[i].strip()[1:-1]
        print(categories)
        categories = ','.join(categories)
        context = {
            'cur_post': cur_post,
            'categories': categories
        }
        return render(request, 'edit_post.html', context=context)

    def post(self, request, *args, **kwargs):
        post_id = kwargs['post_id']
        author_id = kwargs['author_id']
        cur_post = Post.objects.get(id=post_id)
        title_update = request.POST.get('title', '')
        content_update = request.POST.get('content', '')
        categories_update = request.POST.get('categories', '')
        categories_update = process_categories(categories_update)
        description_update = request.POST.get('description ', '')
        if description_update is not None:
            cur_post.description = description_update
        if title_update is not None:
            cur_post.title = title_update
        if content_update is not None:
            cur_post.content = content_update
        if categories_update is not None:
            cur_post.categories = categories_update
        if description_update is not None:
            cur_post.description = description_update

        try:
            image = request.FILES['img']
            name, fileformat = image.name.split('.')
            image64 = base64.b64encode(image.read())
            image64 = 'data:image/%s;base64,%s' % (fileformat, image64.decode('utf-8'))
            cur_post.image = image64
        except Exception:
            image64 = ''

        cur_post.save()
        return redirect(reverse('Author:specific_post', args=(author_id, post_id)))


def delete_post(request, author_id, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return redirect(reverse('Author:index'))


class CreatePostComment(View):
    def get(self, request, author_id, post_id):
        return render(request, 'comment.html', None)

    def post(self, request, author_id, post_id):
        post = Post.objects.get(id=post_id)
        author_for_comment = request.user
        comment_content = request.POST.get('newcomment', '')

        comment = PostComment.objects.create(post=post, author_comment=author_for_comment, comment=comment_content,
                                             author=UserSerializer(author_for_comment).data)
        post.count = post.count + 1
        comment.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(
            author_id) + "/posts/" + str(post_id) + "/comments/" + str(comment.id_comment) + "/"
        comment.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(
            author_id) + "/posts/" + str(post_id) + "/comments/" + str(comment.id_comment) + "/"
        comment.save()
        post.save()
        return redirect(reverse('Author:specific_post', args=(author_id, post_id)))


class SpecificPostView(View):
    def get(self, request, author_id, post_id):
        my_id = request.user.id
        current_user = request.user
        post = Post.objects.get(id=post_id)
        postlikes = PostLike.objects.filter(post=post)
        like_usernames = ""

        isPublic = False
        if str(post.visibility) == "1":
            isPublic = True

        isFriend = False
        if str(post.visibility) == "2":
            isFriend = True

        liked = False
        for postlike in postlikes:
            if isFriend:
                like_usernames += str(postlike.who_like)
            if postlike.who_like == current_user:
                liked = True
        im_author = False

        if str(my_id) == str(author_id):
            im_author = True
        if str(post.author.id) != str(author_id):
            return HttpResponse("The author id and post id does not match!")

        comments = PostComment.objects.filter(post=post).order_by('-published')
        hasComments = False
        if comments:
            hasComments = True
        if post.origin == post.url:
            is_shared = False
        else:
            is_shared = True

        context = {
            'current_author': current_user,
            'author': current_user,
            'isPublic': isPublic,
            'isFriend': isFriend,
            'post': post,
            'liked': liked,
            'author__id': author_id,
            'isAuthor': im_author,
            'hasComments': hasComments,
            'comments': comments,
            'likes_usernames': like_usernames,
            'isShared': is_shared,
        }
        return render(request, 'post_legal.html', context=context)


def like_post(request, author_id, post_id):
    post = Post.objects.get(id=post_id)
    who_like = request.user
    like = PostLike.objects.create(post=post, who_like=who_like, author=UserSerializer(request.user).data,
                                   object=post.api_url)
    inbox_to_send = Inbox.objects.get(author_id=post.author.id)
    inbox_to_send.items.append(LikeSerializer(like).data)
    inbox_to_send.save()

    return redirect(reverse('Author:specific_post', args=(author_id, post_id)))


def share_local_post(request, author_id, post_id):
    source_post = Post.objects.get(id=post_id)
    visibility = source_post.visibility
    if visibility != 1 and visibility != 2:
        return redirect(reverse('Author:specific_post', args=(author_id, post_id)))
    title = source_post.title
    post_id = uuid.uuid4().hex
    post_id = str(post_id)
    source = source_post.url
    origin = source_post.origin
    description = source_post.description
    content_type = source_post.contentType
    content = source_post.content
    categories = source_post.categories
    image = source_post.image
    post = Post.objects.create(visibility=visibility, title=title, id=post_id, source=source,
                               origin=origin, description=description, contentType=content_type,
                               content=content, author=request.user, categories=categories,
                               image=image)
    if post.author.url != "":
        post.url = post.author.url + "posts/" + post.id + "/"
        post.api_url = post.author.api_url + "posts/" + post.id + "/"
    else:
        post.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(
            post.author.id) + "/posts/" + post.id + "/"
        post.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(
            post.author.id) + "/posts/" + post.id + "/"
    if visibility == 2:
        try:
            friends = Friend.objects.get(user=author)
            for friend in friends.friends:
                if friend['host'] == author.host:
                    fri_obj = User.objects.get(id=friend['uuid'])
                    inbox, status = Inbox.objects.get_or_create(author=fri_obj)
                    print(inbox.items)
                    inbox.items.append(PostSerializer(post).data)
                    inbox.save()
                else:
                    # author_serilized = UserSerializer(author).data
                    data = PostSerializer(post).data
                    inbox_url = ''
                    try:
                        remote_author_api_url = friend["url"]
                    except Exception:
                        remote_author_api_url = friend["id"]
                    if remote_author_api_url[-1] == '/':
                        inbox_url = remote_author_api_url + 'inbox'
                    else:
                        inbox_url = remote_author_api_url + '/inbox'
                    request = requests.post(inbox_url, json.dumps(data), auth=HTTPBasicAuth("team11", "secret11"))
        except:
            pass

    post.save()
    return redirect(reverse('Author:specific_post', args=(post.author.id, post.id)))


def share_remote_post(request):
    postAPIURL = request.GET.get("post_url")
    postAPIURL = urllib.parse.unquote(postAPIURL)
    postRequest = make_api_get_request(postAPIURL)
    post = postRequest.json()
    print(post)

    team_flag = 0

    try:
        author_413 = post["author"]
        host_413 = author_413["host"]
        if host_413 == "http://cmput404-team13-socialapp.herokuapp.com":
            team_flag = 13
            source = post["url"]
        elif host_413 == "https://social-distribution-fall2021.herokuapp.com/api/":
            team_flag = 4
            source = post["id"]
    except Exception:  # TODO
        print("Wrong")
        '''
        all_info = post["items"]
        author_17 = all_info["author"]
        host_17 = author_17["host"]
        if host_17 == "https://cmput404f21t17.herokuapp.com/":
            team_flag = 17 '''

    if team_flag == 0:
        print("The host is not in our connected group")
        return redirect(reverse('Author:remote_specific_post') + "?post_url=%s" % postAPIURL)

    # image = post['contentType'] + post['content']

    isPublic = False
    isFriend = False
    try:
        if str(post.visibility).lower() == "pb" or str(post.visibility).lower() == "public":
            isPublic = True
        if str(post.visibility).lower() == "fr" or str(post.visibility).lower() == "friends only":
            # T13: FRIENDS
            isFriend = True
    except Exception:
        if str(post["visibility"]).lower() == "pb" or str(post["visibility"]).lower() == "public":
            isPublic = True
        if str(post["visibility"]).lower() == "fr" or str(post["visibility"]).lower() == "friends only":
            isFriend = True

    if isPublic:
        visibility = 1
    elif isFriend:
        visibility = 2
    else:
        # It will be a private post and we can't share it, do nothing
        return redirect(reverse('Author:remote_specific_post') + "?post_url=%s" % postAPIURL)

    title = post["title"]
    post_id = uuid.uuid4().hex
    post_id = str(post_id)

    origin = post["origin"]
    description = post["description"]
    content_type = post["contentType"]
    content = post["content"]
    try:
        categories = post["categories"]
    except Exception:
        categories = ''
    try:
        image = post["image"]
    except Exception:
        image = ''
    post = Post.objects.create(visibility=visibility, title=title, id=post_id, source=source,
                               origin=origin, description=description, contentType=content_type,
                               content=content, author=request.user, categories=categories,
                               image=image)
    if post.author.url != "":
        post.url = post.author.url + "posts/" + post.id + "/"
        post.api_url = post.author.api_url + "posts/" + post.id + "/"
    else:
        post.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(
            post.author.id) + "/posts/" + post.id + "/"
        post.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(
            post.author.id) + "/posts/" + post.id + "/"
    if visibility == 2:
        try:
            friends = Friend.objects.get(user=author)
            for friend in friends.friends:
                if friend['host'] == author.host:
                    fri_obj = User.objects.get(id=friend['uuid'])
                    inbox, status = Inbox.objects.get_or_create(author=fri_obj)
                    print(inbox.items)
                    inbox.items.append(PostSerializer(post).data)
                    inbox.save()
                else:
                    # author_serilized = UserSerializer(author).data
                    data = PostSerializer(post).data
                    inbox_url = ''
                    try:
                        remote_author_api_url = friend["url"]
                    except Exception:
                        remote_author_api_url = friend["id"]
                    if remote_author_api_url[-1] == '/':
                        inbox_url = remote_author_api_url + 'inbox'
                    else:
                        inbox_url = remote_author_api_url + '/inbox'
                    request = requests.post(inbox_url, json.dumps(data), auth=HTTPBasicAuth("team11", "secret11"))
        except Exception:
            pass
    post.save()

    return redirect(reverse('Author:remote_specific_post') + "?post_url=%s" % postAPIURL)


class like_remote_post_view(View):
    def get(self, request):
        post_url = request.GET.get("post_url")
        current_author = request.user
        post = make_api_get_request(post_url).json()

        post_author_url = post["author"]["url"]
        data = {
            "summary": "%s likes your post" % current_author.username,
            "type": "like",
            "author": UserSerializer(current_author).data,
            "object": post["id"]
        }
        print(data)
        if post_author_url[-1] == '/':
            inbox_url = post_author_url + "inbox"
        else:
            inbox_url = post_author_url + "/inbox"
        print("inbox_url", inbox_url)
        try:
            request = make_api_post_request(inbox_url, json.dumps(data))
            print(json.dumps(data))
            print("inbox post request:!!!!!", request)
            return redirect(reverse('Author:remote_specific_post') + "?post_url=%s" % post_url)

        except Exception:
            return HttpResponse("failed to like the post")


# class CommentRemotePostView(View):
#     def get(self, request, author_id, post_id):
#         return render(request, 'comment.html', None)
#
#     def post(self, request, author_id, post_id):
#         post_url = request.GET.get("post_url")
#         post = make_api_get_request(post_url).json()
#
#         author_for_comment = request.user
#         comment_content = request.POST.get('newcomment', '')
#
#         data = {
#             "type": "comment",
#             "author": UserSerializer(author_for_comment).data,
#             "comment": comment_content,
#             "contentType": "text/plain",  # TODO: add markdown option
#         }
#
#         comment.url = request.scheme + "://" + request.META['HTTP_HOST'] + "/author/" + str(
#             author_id) + "/posts/" + str(post_id) + "/comments/" + str(comment.id_comment) + "/"
#         comment.api_url = request.scheme + "://" + request.META['HTTP_HOST'] + "/api/author/" + str(
#             author_id) + "/posts/" + str(post_id) + "/comments/" + str(comment.id_comment) + "/"
#         make_api_post_request(comment_url, json.dumps(data))
#         print(json.dumps(data))
#         # return redirect(reverse('Author:specific_post', args=(author_id, post_id)))
#         return redirect(reverse('Author:remote_specific_post') + "?post_url=%s" % post_url)


def unlike_post(request, author_id, post_id):
    post = Post.objects.get(id=post_id)
    who_like = request.user
    postlikes = PostLike.objects.filter(post=post)
    for postlike in postlikes:
        if postlike.who_like == who_like:
            postlike.delete()
    return redirect(reverse('Author:specific_post', args=(author_id, post_id)))


class APIComment(APIView):
    def get(self, request, authorId, postId, commentId):
        comment = PostComment.objects.get(id_comment=commentId)
        comment_serializer = CommentSerializer(comment)
        response = Response()
        response.status_code = 200
        response.data = comment_serializer.data
        return response


class APILikesByPost(APIView):
    def get(self, request, authorId, postId):
        like = PostLike.objects.filter(post_id=postId)
        like_serializer = LikeSerializer(like, many=True)
        response = Response()
        data = {
            "type": "likes",
            "items": like_serializer.data
        }
        response.status_code = 200
        response.data = data
        return response


class APICommentsByAuthorId(APIView):
    def get(self, request, authorId):
        pass


class APILikesByAuthorId(APIView):
    def get(self, request, authorId):
        pass


class Remote_Specific_Post_View(View):
    def get(self, request, author_id=None):

        my_id = request.user.id
        current_user = request.user
        # post = Post.objects.get(id=post_id)
        # postlikes = PostLike.objects.filter(post=post)
        postAPIURL = request.GET.get("post_url")
        print(postAPIURL)
        postAPIURL = urllib.parse.unquote(postAPIURL)
        postRequest = make_api_get_request(postAPIURL)
        post = postRequest.json()
        print("remote post be like:", post)
        team_flag = 0

        try:
            author_413 = post["author"]
            host_413 = author_413["host"]
            if host_413 == "http://cmput404-team13-socialapp.herokuapp.com":
                team_flag = 13
            elif host_413 == "https://social-distribution-fall2021.herokuapp.com/api/":
                team_flag = 4
        except Exception:  # TODO
            team_flag = 17
            '''
            all_info = post["items"]
            author_17 = all_info["author"]
            host_17 = author_17["host"]
            if host_17 == "https://cmput404f21t17.herokuapp.com/":
                team_flag = 17 '''

        if team_flag == 0:
            print("The host is not in our connected group")
            return None

        if postAPIURL[-1] == "/":
            postLikesAPIURL = postAPIURL + "likes"
            postCommentsAPIURL = postAPIURL + "comments"
        else:
            postLikesAPIURL = postAPIURL + "/likes"
            postCommentsAPIURL = postAPIURL + "/comments"

        postLikesRequest = make_api_get_request(postLikesAPIURL)

        try:
            postlikes = postLikesRequest.json()["items"]
        except Exception:
            postlikes = None
        print("postlikes:", postlikes)
        postCommentsRequest = make_api_get_request(postCommentsAPIURL)
        comments = None
        if postCommentsRequest.status_code == 200:
            comments_request = postCommentsRequest.json()
            if team_flag == 4:
                comments = comments_request["comments"]
            elif team_flag == 13:
                comments = comments_request

        print("postcomments:", comments)

        image = post['contentType'] + post['content']

        liked = False
        '''
        for postlike in postlikes:
            if postlike["url"] == current_user.api_url:
                liked = True
        '''
        im_author = False

        '''
        if str(my_id) == str(author_id):
            im_author = True
        if str(post.author.id) != str(author_id):
            return HttpResponse("The author id and post id does not match!")
        '''

        hasComments = False
        if comments:
            hasComments = True

        isPublic = False
        try:
            if str(post.visibility).lower() == "pb" or str(post.visibility).lower() == "public":
                isPublic = True
        except Exception:
            if str(post["visibility"]).lower() == "pb" or str(post["visibility"]).lower() == "public":
                isPublic = True

        context = {
            'author': current_user,
            'isPublic': isPublic,
            'post': post,
            'liked': liked,
            'author__id': author_id,
            'isAuthor': im_author,
            'image': image,
            'hasComments': hasComments,
            'comments': comments,  # return render(request, 'posts/comments.html', context=context)
            'flag': team_flag
        }
        print(context)
        return render(request, 'remote_public_post.html', context=context)

    def post(self, request):
        postAPIURL = request.GET.get("post_url")
        print(postAPIURL)
        postAPIURL = urllib.parse.unquote(postAPIURL)
        postRequest = make_api_get_request(postAPIURL)
        post = postRequest.json()
        print("remote post be like:", post)
        team_flag = 0

        try:
            author_413 = post["author"]
            host_413 = author_413["host"]
            if host_413 == "http://cmput404-team13-socialapp.herokuapp.com":
                team_flag = 13
            elif host_413 == "https://social-distribution-fall2021.herokuapp.com/api/":
                team_flag = 4
            
        except Exception:  # TODO
                team_flag = 17

        json_data = []
        error_msg_dic = {
            "data": "",
            "msg": "",
            "code": ""
        }
        author_for_comment = request.user
        comment_content = request.POST.get('newcommentremote', '')
        comment_type = request.POST.get('typeremote', '')
        comment_id = uuid.uuid4().hex
        postAPIURL = request.GET.get("post_url")
        commentAPIURL = urllib.parse.unquote(postAPIURL) + "comments/"
        if team_flag == 13:
            data = {
                "type": "comment",
                "author": UserSerializer(author_for_comment).data,
                "comment": comment_content,
                "contentType": comment_type, 

            }

            if data:
                error_msg_dic["code"] = "200"
                error_msg_dic["msg"] = "Successfully comment the post"
                json_data.append(error_msg_dic)
                # print("message OK")

                # print(commentAPIURL, "\n\n\n")
                request = make_api_post_request(commentAPIURL, json.dumps(data))
                # return redirect(reverse('Author:remote_specific_post') + "?post_url=%s" % postAPIURL )

            else:
                error_msg_dic["code"] = "400"
                error_msg_dic["msg"] = "Fail to comment the post, please try  again"
                json_data.append(error_msg_dic)
                print("fail to comment")

        elif team_flag == 4:
            current_author = request.user
            post_author_url = post["author"]["url"]
            actor_author = User.objects.get(id=current_author.id)
            data = {
                "summary": "%s commented on your post" % current_author.username,
                "type": "comment",
                "author": UserSerializer(actor_author).data,
                "comment":comment_content,
                "contentType": comment_type,
                "object": post["id"],
            }
            print("data:",data)
            if post_author_url[-1] == '/':
                inbox_url = post_author_url + "inbox"
            else:
                inbox_url = post_author_url + "/inbox"

            if data:
                error_msg_dic["code"] = "200"
                error_msg_dic["msg"] = "Successfully comment the post"
                json_data.append(error_msg_dic)

                request = make_api_post_request(inbox_url, json.dumps(data))

                #return HttpResponse(json.dumps(data))

            else:
                error_msg_dic["code"] = "400"
                error_msg_dic["msg"] = "Fail to comment the post, please try  again"
                json_data.append(error_msg_dic)
                print("fail to comment")

        return redirect(reverse('Author:remote_specific_post') + "?post_url=%s" % postAPIURL)

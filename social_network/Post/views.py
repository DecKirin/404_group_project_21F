from django.shortcuts import render
from urllib.parse import urlparse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView
from Author.models import User, Inbox, Post
from friends.models import Follower
from rest_framework.response import Response
import uuid
from rest_framework import serializers


class PostRest(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author',
                  'categories', 'count', 'size', 'published', 'visibility', 'unlisted']


# return relative path
def get_path(old_path):
    new_path = 'https://{' + urlparse(old_path) + '.hostname}'
    return new_path


def get_author_id(request,auth_id):
    ab_path = request.build_absolute_uri()
    re_path = get_path(ab_path)
    return f"{re_path}/author/{auth_id}"


class NewPostView(View):
    def get(self, request):
        return render(request, 'new_post.html')

    def post(self, request):
        author_id = request.user
        title = request.get('title', '')
        content_type = request.get('content_type', '')
        content = request.get('content', '')
        categories = request.get('categories', '')  # TODO
        # source = request.get('source', '')
        # origin = request.get('origin', '')
        source = ''  # TODO
        origin = ''  # TODO
        comments = ''  # TODO

        # unlisted = request.get('unlisted', False)
        unlisted = ''   # TODO
        post_id = uuid.uuid4().hex
        post_id = str(post_id)
        description = request.get('description ', '')
        visibility = request.get('visibility', '')
        data1 = {'title': title, 'id': f"{author_id}/posts/{post_id}",
                 'source': source, 'origin': origin, 'description': description,
                 'contentType': content_type, 'content': content, 'author': author_id,
                 'categories': categories, 'count': 0,
                 'comments': comments, 'visibility': visibility, 'unlisted': unlisted}
        inf_store = PostRest(data=data1)
        inf_store.save()
        return Response(inf_store.data, 200)


# Creation URL
class URLPostsView(View):
    # # POST
    # def create_post(self, request,*args, **kwargs):
    #     json_data = []
    #     author_id = request.user
    #     title = request.get('title', '')
    #     contentType = request.get('contentType', '')
    #     content = request.get('content', '')
    #     source = request.get('source', '')
    #     origin = request.get('origin', '')
    #     categories = request.get('categories', '')
    #     size = request.get('size', '')
    #     count = request.get('count', '')
    #     comments = request.get('comments', '')
    #     unlisted = request.get('unlisted', False)
    #     post_id = uuid.uuid4().hex
    #     post_id = str(post_id)
    #     description = request.get('description ', '')
    #     visibility = request.get('visibility', '')
    #     data1 = {'title': title, 'id': f"{author_id}/posts/{post_id}",
    #              'source': source, 'origin': origin, 'description': description,
    #              'contentType': contentType, 'content': content, 'author': author_id,
    #              'categories': categories, 'count': count, 'size': size,
    #              'comments': comments, 'visibility': visibility, 'unlisted': unlisted}
    #     inf_store = PostRest(data=data1)
    #     inf_store.save()
    #     return Response(inf_store.data, 200)

    # GET all posts
    def get_author_posts(self, request,*args, **kwargs):
        author_id = request.user
        author_posts = Post.objects.filter(author=author_id)
        inf_ret = PostRest(author_posts, many=True)
        return Response(inf_ret.data)


# with post_id
class PostsView(View):
    # GET
    def get_id_post(self, request,*args, **kwargs):
        post_id = request.get('id', '')
        posts = Post.objects.get(id=post_id)
        inf_ret = PostRest(posts)
        return Response(inf_ret.data)

    # POST
    def update_post(self, request,*args, **kwargs):
        post_id = request.get('id', '')
        posts = Post.objects.get(id=post_id)
        title_update = request.get('title', '')
        contentType_update = request.get('contentType', '')
        content_update = request.get('content', '')
        source_update = request.get('source', '')
        origin_update = request.get('origin', '')
        categories_update = request.get('categories', '')
        size_update = request.get('size', '')
        count_update = request.get('count', '')
        comments_update = request.get('comments', '')
        unlisted_update = request.get('unlisted', False)
        description_update = request.get('description ', '')
        visibility_update = request.get('visibility', '')
        if title_update is not None:
            posts.title = title_update
        if contentType_update is not None:
            posts.contentType = contentType_update
        if content_update is not None:
            posts.content = content_update
        if source_update is not None:
            posts.source = source_update
        if origin_update is not None:
            posts.origin = origin_update
        if categories_update is not None:
            posts.categories = categories_update
        if size_update is not None:
            posts.size = size_update
        if count_update is not None:
            posts.count = count_update
        if comments_update is not None:
            posts.comments = comments_update
        if unlisted_update is not None:
            posts.unlisted = unlisted_update
        if description_update is not None:
            posts.description = description_update
        if visibility_update is not None:
            posts.visibility = visibility_update
        posts.save()
        return Response("Posts Update")

    # PUT
    def put_post(self,request,*args, **kwargs):
        author_id = request.user
        post_id = request.get('id', '')
        title = request.get('title', '')
        contentType = request.get('contentType', '')
        content = request.get('content', '')
        source = request.get('source', '')
        origin = request.get('origin', '')
        categories = request.get('categories', '')
        size = request.get('size', '')
        count = request.get('count', '')
        comments = request.get('comments', '')
        unlisted = request.get('unlisted', False)
        description = request.get('description ', '')
        visibility = request.get('visibility', '')
        data1 = {'title': title, 'id': f"{author_id}/posts/{post_id}",
                 'source': source, 'origin': origin, 'description': description,
                 'contentType': contentType, 'content': content, 'author': author_id,
                 'categories': categories, 'count': count, 'size': size,
                 'comments': comments, 'visibility': visibility, 'unlisted': unlisted}
        inf_ret = Follower.objects.filter(followers=author_id)
        if inf_ret is not None:
            all_follower = Follower.objects.get(followers=author_id)
            for follower in all_follower:
                inbox = Inbox.objects.get(author=follower)
                inbox.items.append(data1)
                inbox.save()
        inf_store = PostRest(data=data1)
        inf_store.save()
        return Response(inf_store.data)

    # DELETE
    def delete_post(self, request,*args, **kwargs):
        author_id = request.user
        post_id = request.get('id', '')
        post_id = author_id + post_id
        post = Post.objects.get(id=post_id)
        post.delete()
        return Response("Post Deleted")


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
from django.shortcuts import render, redirect
from django.urls import reverse


# class PostSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Post
#         fields = ['type', 'title', 'id', 'source', 'origin', 'description', 'contentType', 'content', 'author',
#                   'categories', 'count', 'comments', 'published', 'visibility', 'unlisted']
#

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
        return render(request, 'new_post.html', None)

    def post(self, request):
        author_id = request.user.id
        title = request.POST.get('title', '')
        content_type = request.POST.get('content_type', '')
        content = request.POST.get('content', '')
        categories = request.POST.get('categories', '')  # TODO
        description = request.POST.get('description', '')
        # source = request.get('source', '')
        # origin = request.get('origin', '')
        source = request.build_absolute_uri()  # TODO
        origin = request.build_absolute_uri()  # TODO
        #comments = ''  # TODO

        # unlisted = request.get('unlisted', False)
        unlisted = False   # TODO
        post_id = uuid.uuid4().hex
        post_id = str(post_id)
        visibility = int(request.POST.get('visibility', ''))
        data1 = {'title': title, 'id': f"{author_id}/posts/{post_id}",
                'source': source, 'origin': origin, 'description': description,
                'contentType': content_type, 'content': content, 'author': request.user,
                'categories': categories,
                'visibility': visibility, 'unlisted': unlisted}
        print(data1)
        # inf_store = PostSerializer(data=data1)
        Post.objects.create(title=title, id=f"{author_id}/posts/{post_id}", source=source, origin=origin, description=description,
                            contentType=content_type, content=content, author=request.user, categories=categories,
                            visibility=visibility, unlisted=unlisted)
        # if inf_store.is_valid():
        #     inf_store.save()
        return redirect(reverse('Author:index'))
        #     # return Response(inf_store.data, 200) TODO:
        # else:
        #     return Response(inf_store.data, 400)  # TODO


# Creation URL
class URLPostsView(View):
    # # POST
    # def create_post(self, request,*args, **kwargs):
    #    
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
    #     inf_store = PostSerializer(data=data1)
    #     inf_store.save()
    #     return Response(inf_store.data, 200)

    # GET all posts
    def get_author_posts(self, request,*args, **kwargs):
        author_id = request.user
        author_posts = Post.objects.filter(author=author_id)
        inf_ret = PostSerializer(author_posts, many=True)
        return Response(inf_ret.data)


# with post_id
class PostsView(View):
    # GET
    def get_id_post(self, request,*args, **kwargs):
        post_id = request.get('id', '')
        posts = Post.objects.get(id=post_id)
        inf_ret = PostSerializer(posts)
        return Response(inf_ret.data)

    # POST
    def update_post(self, request,*args, **kwargs):
        post_id = request.get('id', '')
        posts = Post.objects.get(id=post_id)
        title_update = request.data.get('title', '')
        contentType_update = request.data.get('contentType', '')
        content_update = request.data.get('content', '')
        source_update = request.data.get('source', '')
        origin_update = request.data.get('origin', '')
        categories_update = request.data.get('categories', '')
        size_update = request.data.get('size', '')
        count_update = request.data.get('count', '')
        comments_update = request.data.get('comments', '')
        unlisted_update = request.data.get('unlisted', False)
        description_update = request.data.get('description ', '')
        visibility_update = request.data.get('visibility', '')
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
        title = request.data.get('title', '')
        contentType = request.data.get('contentType', '')
        content =request.data.get('content', '')
        source = request.data.get('source', '')
        origin = request.data.get('origin', '')
        categories = request.data.get('categories', '')
        size = request.data.get('size', '')
        count = request.data.get('count', '')
        comments = request.data.get('comments', '')
        unlisted = request.data.get('unlisted', False)
        description = request.data.get('description ', '')
        visibility = request.data.get('visibility', '')
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
        inf_store = PostSerializer(data=data1)
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


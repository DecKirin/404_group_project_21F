from django.shortcuts import render
from urllib.parse import urlparse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView
from Author.models import User, Inbox, Post
from friends.models import Friend
from rest_framework.response import Response
import uuid
from rest_framework import serializers
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from json import loads
from Post.models import Postlike, Postcomment


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


def process_categories(categories):
    categories = categories.split(',')
    for i in range(len(categories)):
        categories[i] = categories[i].strip()
    return str(categories)


class NewPostView(View):
    def get(self, request):
        return render(request, 'new_post.html', None)

    def post(self, request):
        author_id = request.user.id
        title = request.POST.get('title', '')
        content_type = request.POST.get('content_type', '')
        content = request.POST.get('content', '')

        categories = request.POST.get('categories', '')  # TODO
        categories = process_categories(categories)

        description = request.POST.get('description', '')
        source = request.build_absolute_uri(request.path)  
        origin = request.build_absolute_uri(request.path)
        unlisted = False   # TODO
        post_id = uuid.uuid4().hex
        post_id = str(post_id)
        visibility = int(request.POST.get('visibility', ''))
        select_user = int(request.POST.get('select_user', ''))  # TODO: id要改成选user

        Post.objects.create(title=title, id=post_id, source=source, origin=origin, description=description,
                            contentType=content_type, content=content, author=request.user, categories=categories,
                            visibility=visibility, unlisted=unlisted, select_user=select_user)
        return redirect(reverse('Author:index'))

    def select_private(self, request): #TODO
        return None


# with post_id
class PostsView(View):
    # GET
    def get_id_post(self, request,*args, **kwargs):
        post_id = request.get('id', '')
        posts = Post.objects.get(id=post_id)
        inf_ret = PostSerializer(posts)
        return Response(inf_ret.data)

    def get_author_posts(self, request,*args, **kwargs):
        author_id = request.user
        author_posts = Post.objects.filter(author=author_id)
        inf_ret = PostSerializer(author_posts, many=True)
        return Response(inf_ret.data)

    def get_valid_post(self, request,*args, **kwargs):
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
                if self.check_private_spe(request,post,author_id):
                    inf_ret.append(post)
        return Response(inf_ret)

    def check_private_spe(self,request,post,author_id):#TODO
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
        #post_id = request.get('post_id', '')
        cur_post = Post.objects.get(id=post_id)
        description_update = request.POST.get('description', '')
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
        cur_post.save()
        return HttpResponse("Post Updated")


def delete_post(request, author_id, post_id):
    post = Post.objects.get(id=post_id)
    post.delete()
    return HttpResponse("Post Deleted")


class SpecificPostView(View):
    def get(self, request, author_id, post_id):
        my_id = request.user.id
        post = Post.objects.get(id=post_id)
        liked = False  # TODO
        im_author = False
        if str(my_id) == str(author_id):
            im_author = True
        if post.author.id != int(author_id):  # TODO: not int later
            print(post.author.id, author_id)
            return HttpResponse("The author id and post id does not match!")

        context = {
            'post': post,
            'liked': liked,
            'author__id': author_id,
            'isAuthor': im_author

        }
        return render(request, 'post_legal.html', context=context)

      
def createLikePost(request,post_id1):
    cur_post = Post.objects.get(id=post_id)
    author_like = request.user
    likes = Postlike.objects.filter(post_id=post_id1)
    context = {
        'author': author_like,
        'post': cur_post,
        'likes': likes
    }
    return redirect(reverse('Author:index'))
    

def createCommentPost(request,post_id):
    author_comment = request.user
    cur_post = Post.objects.get(id=post_id)
    comments = Postcomment.objects.filter(post=cur_post).order_by('-published')
    context = {
        'author': author_comment,
        'post': cur_post,
        'comments': comments
    }
    
    return render(request, 'posts/comments.html', context=context)
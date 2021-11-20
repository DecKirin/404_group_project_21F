from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from Author.views import RegisterView, LoginView, UserInfoView, LogoutView, UserPostsView, IndexView, InterFRInboxView, InterPostInboxView, InboxView, \
    UserProfileView, AllUserProfileView, SearchUserView, UserEditInfoView, MyStreamView, AllPublicPostsView
from friends.views import friends_list_view, send_friend_request, process_friend_request, followers_list_view, \
    follows_list_view, follower_view, un_befriend, my_list , APIFollowsByIdView, APIFollowersByIdView, APIFriendsByIdView
from Post.views import NewPostView, SpecificPostView, EditPostView, delete_post, like_post, unlike_post, CreatePostComment

from Author.views import APIAllProfileView, APIAuthorProfileView

app_name = 'Author'
urlpatterns = [

    path('newpost/', NewPostView.as_view(), name='newpost'),
    path('searchAuthor/', SearchUserView.as_view(), name='search_user'),
    path('<uuid:id>/friends/', friends_list_view, name='friend'),
    path('<uuid:id>/followers/', followers_list_view, name='follower'),
    path('<uuid:id>/followers/<foreign_id>', follower_view.as_view(), name='foreign_follower'),
    path('<uuid:id>/follows/', follows_list_view, name='follow'),
    path('<uuid:author_id>/posts/<post_id>/', SpecificPostView.as_view(), name='specific_post'),
    path('<uuid:author_id>/posts/<post_id>/edit/', EditPostView.as_view(), name='edit_post'),
    path('<uuid:author_id>/posts/<post_id>/delete/', delete_post, name='delete_post'),
    path('<uuid:author_id>/posts/<post_id>/like/', like_post, name='like_post'),
    path('<uuid:author_id>/posts/<post_id>/unlike/', unlike_post, name='unlike_post'),
    path('<uuid:author_id>/posts/<post_id>/comment/', CreatePostComment.as_view(), name='post_comment'),
    # author successfully send the friend request
    path('friendrequest/<foreign_id>', send_friend_request, name='friend_request'),
    path('accept/<request_id>', process_friend_request.as_view(), name='accept'),
    # show current user's list
    path('my<relationship>list/', my_list, name='my_list'),
    # check inbox to get sent request
    path('sentrequest/<request_id>', process_friend_request.as_view(), name='process_request'),
    path('authors/', AllUserProfileView.as_view(), name='all_authors'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # home page after logging in
    path('index/', IndexView.as_view(), name='index'),
    # account page of logged in user
    path('account/', login_required(UserInfoView.as_view()), name='info'),
    # view a my posts as login in user in a list
    path('myposts/', login_required(UserPostsView.as_view()), name='myposts'),
    path('myStream/', login_required(MyStreamView.as_view()), name='mystream'),

    path('editProfile/', login_required(UserEditInfoView.as_view()), name='edit_profile'),
    # display all user profiles
    # page to view other user's profile

    path('<uuid:id>/', UserProfileView.as_view(), name='profile'),
    # Inboxes
    path('<uuid:id>/inbox/', login_required(InboxView.as_view()), name='inbox'),
    path('inbox/fr', login_required(InterFRInboxView.as_view()), name='inter_FRinbox'),
    path('inbox/posts', login_required(InterPostInboxView.as_view()), name='inter_postinbox'),

    path('posts/allPublicPosts/', AllPublicPostsView.as_view(), name='all_public_posts'),
    # Un-befriend
    path('<uuid:id>/<delete>', un_befriend, name='un_befriend'),


    # below are URLs for API only
    path('api/authors/', APIAllProfileView.as_view(), name="api_authors"),
    path('api/<uuid:id>/', APIAuthorProfileView.as_view(), name="api_author_by_id"),
    path('api/<uuid:id>/follows', APIFollowsByIdView.as_view(), name="api_follows_by_id"),
    path('api/<uuid:id>/followers', APIFollowersByIdView.as_view(), name="api_followers_by_id"),
    path('api/<uuid:id>/friends', APIFriendsByIdView.as_view(), name="api_friends_by_id"),


]

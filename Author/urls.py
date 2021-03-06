from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from Author.views import baseView, RegisterView, LoginView, UserInfoView, LogoutView, UserPostsView, IndexView, InterFRInboxView, \
    InterPostInboxView, InboxView, \
    UserProfileView, AllUserProfileView, SearchUserView, UserEditInfoView, MyStreamView, AllPublicPostsView, \
    APIAuthorPostsView, APIPostByIdView, APIInbox, InterLikeInboxView, UserEditProfileImageView
from friends.views import friends_list_view, send_friend_request, process_friend_request, followers_list_view, \
    follows_list_view, API_follower_view, un_befriend, my_list, APIFollowsByIdView, APIFollowersByIdView, \
    APIFriendsByIdView, remote_sent_request, remote_un_befriend
from Post.views import NewPostView, SpecificPostView, EditPostView, delete_post, like_post, unlike_post, \
    CreatePostComment, APICommentsByAuthorId, APILikesByAuthorId, APIComment, APILikesByPost, \
    like_remote_post_view, share_local_post, share_remote_post

from Author.views import APIAllProfileView, APIAuthorProfileView, APIAllPosts, APICommentsByPostId

from Author.views import Remote_Author_Profile_View
from Post.views import Remote_Specific_Post_View

app_name = 'Author'
urlpatterns = [
    path('', baseView.as_view(), name='index'),
    path('newpost/', NewPostView.as_view(), name='newpost'),
    path('searchAuthor/', SearchUserView.as_view(), name='search_user'),
    path('author/<uuid:id>/friends/', friends_list_view, name='friend'),
    path('author/<uuid:id>/followers/', followers_list_view.as_view(), name='follower'),
    # path('author/<uuid:id>/followers/<foreign_id>', follower_view.as_view(), name='foreign_follower'),
    path('author/<uuid:id>/follows/', follows_list_view, name='follow'),
    path('author/<uuid:author_id>/posts/<post_id>/', SpecificPostView.as_view(), name='specific_post'),
    path('author/<uuid:author_id>/posts/<post_id>/edit/', EditPostView.as_view(), name='edit_post'),
    path('author/<uuid:author_id>/posts/<post_id>/delete/', delete_post, name='delete_post'),
    path('author/<uuid:author_id>/posts/<post_id>/like/', like_post, name='like_post'),
    path('author/<uuid:author_id>/posts/<post_id>/sharelocal/', share_local_post, name='share_local_post'),
    path('author/<uuid:author_id>/posts/<post_id>/unlike/', unlike_post, name='unlike_post'),
    path('author/<uuid:author_id>/posts/<post_id>/comment/', CreatePostComment.as_view(), name='post_comment'),
    # author successfully send the friend request
    path('friendrequest/<foreign_id>', send_friend_request, name='friend_request'),
    path('accept/<request_id>', process_friend_request.as_view(), name='accept'),
    # show current user's list
    path('my<relationship>list/', my_list, name='my_list'),
    # check inbox to get sent request
    path('sentrequest/<request_id>', process_friend_request.as_view(), name='process_request'),
    path('authors/', AllUserProfileView.as_view(), name='all_authors'),
    path('author/register/', RegisterView.as_view(), name='register'),
    path('author/login/', LoginView.as_view(), name='login'),
    path('author/logout/', LogoutView.as_view(), name='logout'),
    # home page after logging in
    path('index/', IndexView.as_view(), name='index'),
    # account page of logged in user
    path('account/', login_required(UserInfoView.as_view()), name='info'),
    # view a my posts as login in user in a list
    path('myposts/', login_required(UserPostsView.as_view()), name='myposts'),
    path('author/myStream/', login_required(MyStreamView.as_view()), name='mystream'),

    path('editProfile/', login_required(UserEditInfoView.as_view()), name='edit_profile'),
    path('editImage/', UserEditProfileImageView.as_view(), name='edit_profile_image'),
    # display all user profiles
    # page to view other user's profile

    path('author/<str:id>/', UserProfileView.as_view(), name='profile'),
    # Inboxes
    path('<uuid:id>/inbox/', login_required(InboxView.as_view()), name='inbox'),
    path('inbox/fr', login_required(InterFRInboxView.as_view()), name='inter_FRinbox'),
    path('inbox/posts', login_required(InterPostInboxView.as_view()), name='inter_postinbox'),
    path('inbox/likes', login_required(InterLikeInboxView.as_view()), name='inter_likeinbox'),

    path('posts/allPublicPosts/', AllPublicPostsView.as_view(), name='all_public_posts'),
    # Un-befriend
    path('<uuid:id>/<delete>', un_befriend, name='un_befriend'),
    # remote Un-befriend
    path('remote/<delete>', remote_un_befriend.as_view(), name='remote_un_befriend'),
    # below are URLs for API only
    path('api/authors/',  APIAllProfileView.as_view(), name="api_authors"),
    path('api/author/<uuid:id>/', APIAuthorProfileView.as_view(), name="api_author_by_id"),
    path('api/author/<uuid:id>/follows/', APIFollowsByIdView.as_view(), name="api_follows_by_id"),
    path('api/author/<uuid:id>/followers/', APIFollowersByIdView.as_view(), name="api_followers_by_id"),
    path('api/author/<uuid:id>/friends/', APIFriendsByIdView.as_view(), name="api_friends_by_id"),
    path('api/author/<uuid:id>/followers/<uuid:foreign_id>', API_follower_view.as_view(), name="api_followers_check"),
    path('api/author/<uuid:id>/posts/', APIAuthorPostsView.as_view(), name="api_posts_by_authorId"),
    path('api/author/<uuid:authorId>/posts/<postId>/', APIPostByIdView.as_view(), name="api_post_by_postId"),

    path('api/author/<uuid:authorId>/comments/', APICommentsByAuthorId.as_view(), name="api_comments_by_authorId"),
    path('api/author/<uuid:authorId>/likes/', APILikesByAuthorId.as_view(), name="api_likes_by_authorId"),
    path('api/author/<uuid:authorId>/inbox/', APIInbox.as_view(), name="api_inbox"),


    path('api/author/<uuid:authorId>/posts/<postId>/comments/', APICommentsByPostId.as_view(), name="api_comments_by_postId"),
    path('api/author/<authorId>/posts/<postId>/comments/<commentId>/', APIComment.as_view(), name="api_comment"),
    path('api/author/<authorId>/posts/<postId>/likes/', APILikesByPost.as_view(), name="api_comment"),

    path('api/posts/', APIAllPosts.as_view(), name="api_all_posts"),

    path('remote_author/', Remote_Author_Profile_View.as_view(), name="remote_author_profile"),
    path('remote_post/', Remote_Specific_Post_View.as_view(), name="remote_specific_post"),
    path('remote_post/like', like_remote_post_view.as_view(), name="like_remote_post"),
    path('remote_post/shareremote', share_remote_post, name="share_remote_post"),
    path('remote_author/befriend', remote_sent_request.as_view(), name="remote_friend_request"),

]

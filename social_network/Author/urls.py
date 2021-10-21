from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from Author.views import RegisterView, LoginView, UserInfoView, LogoutView, UserPostsView, IndexView, UserProfileView,AllUserProfileView
from friends.views import friends_list_view, send_friend_request
app_name = 'Author'
urlpatterns = [
    path('friend/', friends_list_view, name='friend'),
    path('<id>srequest/', send_friend_request, name='friend_request'),
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
    # display all user profiles
    # page to view other user's profile
    path('<id>/', UserProfileView.as_view(), name='profile'),
]
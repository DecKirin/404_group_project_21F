from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from Author.views import RegisterView, LoginView, UserInfoView, LogoutView, UserPostsView, IndexView

app_name = 'Author'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('index/', IndexView.as_view(), name='index'),
    path('account/', login_required(UserInfoView.as_view()), name='info'),
    path('myposts/', login_required(UserPostsView.as_view()), name='myposts'),
]
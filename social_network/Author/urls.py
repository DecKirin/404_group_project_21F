from django.urls import path, re_path
from django.contrib.auth.decorators import login_required
from Author.views import RegisterView, LoginView, UserInfoView, LogoutView

app_name = 'Author'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/', login_required(UserInfoView.as_view()), name='info'),
]
from django.urls import path
from .views import RegisterAPI, LoginAPI, UserProfileAPI, LogoutAPI

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('profile/', UserProfileAPI.as_view(), name='profile'),
    path('logout/', LogoutAPI.as_view(), name='logout'),
]

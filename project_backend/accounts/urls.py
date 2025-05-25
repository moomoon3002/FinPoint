from django.urls import path
from . import views

urlpatterns = [
    path('check-nickname/', views.CheckNicknameView.as_view(), name='check-nickname'),
    path('user/', views.UserProfileUpdateView.as_view(), name='user-profile'),
] 
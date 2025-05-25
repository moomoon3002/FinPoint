from django.urls import path
from . import views

urlpatterns = [
    path('check-nickname/', views.CheckNicknameView.as_view(), name='check-nickname'),
] 
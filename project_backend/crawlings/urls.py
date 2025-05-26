from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='stock-voice'),
    path('delete-comment/', views.delete_comment, name='delete-comment'),
] 
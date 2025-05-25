from django.urls import path
from . import views

# articles/url.py

urlpatterns = [
    path('', views.article_list),
    path('<int:article_id>/', views.article_detail),
    path('<int:article_id>/comments/', views.article_comments),
    path('<int:article_id>/comments/<int:comment_id>/', views.comment_detail),
]

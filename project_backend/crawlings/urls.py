from django.urls import path
from . import views

app_name = 'crawlings'

urlpatterns = [
    path('', views.index, name='stock-voice'),
    path('delete-comment/', views.delete_comment, name='delete-comment'),
    path('stock/history/<str:period>/', views.get_stock_history, name='stock_history'),
    path('stock-voice/', views.get_stock_voice, name='stock-voice'),
    path('interests/', views.user_stock_interests, name='user-stock-interests'),
    path('interests/<str:stock_code>/', views.delete_stock_interest, name='delete-stock-interest'),
] 
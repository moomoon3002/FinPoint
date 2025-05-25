from django.urls import path
from . import views

urlpatterns = [
    path('info', views.get_stock_info, name='stock_info'),
] 
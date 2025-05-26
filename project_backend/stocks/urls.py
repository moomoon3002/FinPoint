from django.urls import path
from . import views
from .views import StockDataView

urlpatterns = [
    path('info/', views.get_stock_info, name='stock_info'),
    path('analyze/', views.analyze_sentiment, name='analyze_sentiment'),

] 
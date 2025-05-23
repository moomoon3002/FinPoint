from django.urls import path
from .views import DepositProductListView,DepositProductDetailView

urlpatterns = [
    path('api/', DepositProductListView.as_view(), name='deposit-list'),
    path('api/<str:deposit_ID>/', DepositProductDetailView.as_view(), name='deposit-detail'),
]
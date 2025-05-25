from django.urls import path
from .views import MetalPriceListView, MetalPriceUploadView

urlpatterns = [
    path('prices/', MetalPriceListView.as_view(), name='metal-price-list'),
    path('upload/', MetalPriceUploadView.as_view(), name='metal-price-upload'),
] 
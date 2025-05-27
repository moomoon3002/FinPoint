from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.DepositProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('favorites/', views.get_favorites, name='get-favorites'),
    path('favorites/add/<str:product_id>/', views.add_favorite, name='add-favorite'),
    path('favorites/remove/<str:product_id>/', views.remove_favorite, name='remove-favorite'),
    path('favorites/check/<str:product_id>/', views.check_favorite, name='check-favorite'),
]
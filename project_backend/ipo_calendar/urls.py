from django.urls import path
from . import views

app_name = 'ipo_calendar'

urlpatterns = [
    path('', views.get_ipo_calendar, name='get_ipo_calendar'),
    path('interests/', views.get_user_ipo_interests, name='get_user_ipo_interests'),
    path('interests/<int:event_id>/', views.toggle_ipo_interest, name='toggle_ipo_interest'),
] 
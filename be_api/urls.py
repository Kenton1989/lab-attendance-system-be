from django.urls import path
from . import views

urlpatterns = [
    path('ping', views.ping, name='ping'),
    path('login', views.login_api_view, name='login'),
    path('logout', views.logout_api_view, name='logout'),
    path('user_info', views.user_info_view, name='user_info'),
]

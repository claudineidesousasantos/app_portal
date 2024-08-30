from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import home

app_name = 'home'

urlpatterns = [
    path('', home, name='home'),
]

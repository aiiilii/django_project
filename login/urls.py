from django.urls import path

from . import views

import app1

urlpatterns = [
    path('login_register', views.login_register),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
]
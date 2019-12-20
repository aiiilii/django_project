from django.urls import path

from . import views

import login

urlpatterns = [
    path('', views.index),
    path('add', views.add_post),
    path('edit/<int:postid>', views.edit_post),
    path('view/<int:postid>', views.view_post),
    path('<int:postid>/add_comment', views.add_comment),
    path('<int:postid>/like', views.like_post),
    path('<int:postid>/unlike', views.unlike_post),
    path('<int:postid>/<int:commentid>/like', views.like_comment),
    path('<int:postid>/<int:commentid>/unlike', views.unlike_comment),
    path('profile/<int:userid>', views.profile),
    path('<int:postid>/<int:commentid>/delete', views.delete_comment),
    path('<int:postid>/delete', views.delete_post),

    path('follow/<int:userid>', views.add_relationship),
]
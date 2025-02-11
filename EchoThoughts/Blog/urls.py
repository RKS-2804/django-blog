from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("create/", views.createPost, name="createPost"),
    path("edit/<int:post_sno>/", views.editPost, name="editPost"),
    path("delete/<int:post_sno>/", views.deletePost, name="deletePost"),
    path('postComment', views.postComment, name="postComment"),    
    path('', views.blogHome, name='blogHome'),
    path('<str:slug>', views.blogPost, name='blogPost'),
    path("deleteComment/<int:comment_sno>/", views.deleteComment, name="deleteComment"),
    path("like/<int:post_sno>/", views.likePost, name="likePost"),
    
]

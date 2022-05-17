from django.urls import path
from s_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('main/', views.main, name='main'),
    path('att_records/', views.records, name='att_records'),
    path('unidentified_faces_records/', views.unidentified_faces_records, name='unidentified_faces_records'),
    path('user_records/', views.records, name='user_records'),
    path('train/', views.train, name='train'),
]
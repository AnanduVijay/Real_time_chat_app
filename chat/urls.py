from django.urls import path
from . import views


urlpatterns =  [
    path("loby", views.home, name="home"),
    path("", views.chat_room, name="room"),
    path("chat/<int:user_pk>", views.get_user_id, name="user_id"),
    path("upload_file", views.upload_file, name="upload_file"),
    # path('download_file/<int:message_pk>/', views.download_file, name='download_file'),
]
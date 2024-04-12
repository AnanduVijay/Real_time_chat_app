from django.urls import path

from .consumers import ChatRoomConsumers

websocket_urlpatterns = [
    path("", ChatRoomConsumers.as_asgi()),
]
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),  # Chat général
    path('ws/private_chat/<str:username>/', consumers.PrivateChatConsumer.as_asgi()),  # Chat privé
]
"""# your_api_app/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .consumers import ChatConsumer

application = ProtocolTypeRouter({
    "websocket": URLRouter(
        [
            path("ws/chat/<int:forum_id>/", ChatConsumer.as_asgi()),
            # Add more WebSocket paths if needed
        ]
    ),
})
"""
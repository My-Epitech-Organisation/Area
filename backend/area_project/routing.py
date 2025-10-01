"""
WebSocket URL routing for the AREA project.
"""

from django.urls import path

# Import your WebSocket consumers here when you create them
# from . import consumers

websocket_urlpatterns = [
    # Add WebSocket routes here
    # path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),
    # path("ws/logs/", consumers.LogConsumer.as_asgi()),
]
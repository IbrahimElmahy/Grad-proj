from django.urls import path

from .consumers import HazardAlertConsumer


websocket_urlpatterns = [
    path("ws/alerts/", HazardAlertConsumer.as_asgi()),
]

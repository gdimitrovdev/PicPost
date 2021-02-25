# Django imports
from django.urls import re_path
from . import consumers

# routing to the consumer
websocket_urlpatterns=[
    re_path(r'wss/chat/(?P<room_name>\w+)/$',consumers.ChatConsumer),
    re_path(r'ws/chat/(?P<room_name>\w+)/$',consumers.ChatConsumer),
]
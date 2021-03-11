import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # get both users
        user = self.scope["user"]
        get_ids = self.scope["url_route"]["kwargs"]["room_name"]
        ids = get_ids.split('_')
        my_user = User.objects.get(username=user.username)
        my_id = my_user.id
        other_id = 0
        if str(ids[0]) == str(my_id):
            other_id = ids[1]
        else:
            other_id = ids[0]
        other_user = User.objects.get(pk=other_id)

        # save the sent message to a database
        new_message = Message(sender=my_user, rec=other_user, text=message, room=get_ids)
        new_message.save()

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.username,
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # get the user that sent the message
        user = event['user']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user': user
        }))

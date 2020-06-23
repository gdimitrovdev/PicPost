import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message
User=get_user_model()

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
        getIDS=self.scope["url_route"]["kwargs"]["room_name"]
        ids = getIDS.split('_')
        myUser = User.objects.get(username=user.username)
        myID = myUser.id
        otherID = 0
        if str(ids[0]) == str(myID):
            otherID = ids[1]
        else:
            otherID = ids[0]
        otherUser = User.objects.get(pk=otherID)

        # save the sent message to a database
        new_message = Message(sender=myUser, rec=otherUser, text=message, room=getIDS)
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
        user=event['user']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'user':user
        }))
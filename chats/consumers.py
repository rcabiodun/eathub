# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q
from .models import MessageGroup,Message
from core.models import User


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        try:
            self.message_group = MessageGroup.objects.get(
                Q(member_one=self.scope['user'], member_two=User.objects.get(id=self.room_name)) | Q(
                    member_one=User.objects.get(id=self.room_name), member_two=self.scope['user']))
        except MessageGroup.DoesNotExist:
            self.message_group = MessageGroup.objects.create(member_one=self.scope['user'],
                                              member_two=User.objects.get(id=self.room_name))
            self.message_group.save()
        self.room_group_name = 'chat_%s' % self.message_group.id
        # Join room group

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        print("ACCEPTED" + self.room_group_name)
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
        obj = Message.objects.create(sender_id=self.scope['user'].id, receiver_id=self.room_name, message=message)
        obj.save()
        print(obj.message)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

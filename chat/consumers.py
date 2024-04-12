import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Message, RoomName, Document
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile


User = get_user_model()

class ChatRoomConsumers(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user1_id = self.scope['user'].id
        user2_id = self.scope['session'].get('selected_userid')

        sorted_user_ids = sorted([user1_id, user2_id])

        self.room_group_name = self.get_group_name(sorted_user_ids)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
   
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("room_group_name", self.room_group_name)
        print("text_data_json", text_data_json)
        message = text_data_json.get('message', '')
        username = text_data_json.get('username', None)
        file_url = text_data_json.get('file_url', None)
        if 'file_data' in text_data_json:
             self.receive_file(text_data_json)
        else:
            await self.save_message_to_db(self.scope['user'], text_data_json)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chatroom_message',
                    'message': message,
                    'username': username,
                    'file_url': file_url
                }
            )

    async def chatroom_message(self, event):
        message = event.get('message', None)
        username = event.get('username', None)
        file_url = event.get('file_url', None)

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'file_url': file_url
        }))

    pass

    async def file_uploaded(self, event):
        file_name = event['file_name']
        file_url = event['file_url']
        
        # Send file upload message to the client
        await self.send_json({
            'type': 'file.uploaded',
            'file_name': file_name,
            'file_url': file_url,
        })

    def get_group_name(self, user_ids):
        return f"chat_{user_ids[0]}_{user_ids[1]}"
    
    @database_sync_to_async
    def save_message_to_db(self, user, text_data_json):
        sender = user
        message = text_data_json.get('message', '')
        file_db = text_data_json.get('file_db',None)
        print("file_id", file_db)
        print("text_data_json", text_data_json)
        recipient_id = self.scope['session'].get('selected_userid')
        recipient = User.objects.get(pk=recipient_id)
        group_name =  self.room_group_name
        room_name, _ = RoomName.objects.get_or_create(name= group_name)
        Message.objects.create(room_name=room_name, sender=sender, recipient=recipient, content=message, document_id=file_db)
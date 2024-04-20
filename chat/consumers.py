import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import Message, RoomName
from django.contrib.auth import get_user_model


User = get_user_model()

class ChatRoomConsumers(AsyncJsonWebsocketConsumer):
    """
    Consumer class for building the connection with websocket
    """
    async def connect(self):
        """
        Async fuction to create the handshake connection
        """
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
        """
        Async fuction to disconnect the websocket connection
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
   
    async def receive(self, text_data):
        """
        Async fuction to handle the message from websocket and
        and display it in the group channel
        """
        text_data_json = json.loads(text_data)
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
        """
         Async Function to send a message 
        """
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
        """
        Async Function to send a message 
        """
        file_name = event['file_name']
        file_url = event['file_url']
        
        # Send file upload message to the client
        await self.send_json({
            'type': 'file.uploaded',
            'file_name': file_name,
            'file_url': file_url,
        })

    def get_group_name(self, user_ids):
        """
        Helper function to create the group name using users Id
        """
        return f"chat_{user_ids[0]}_{user_ids[1]}"
    
    @database_sync_to_async
    def save_message_to_db(self, user, text_data_json):
        """
        Fuction to save message to db
        """
        sender = user
        message = text_data_json.get('message', '')
        file_db = text_data_json.get('file_db',None)
        recipient_id = self.scope['session'].get('selected_userid')
        recipient = User.objects.get(pk=recipient_id)
        group_name =  self.room_group_name
        room_name, _ = RoomName.objects.get_or_create(name= group_name)
        Message.objects.create(
            room_name=room_name, sender=sender, recipient=recipient, 
            content=message, document_id=file_db
            )
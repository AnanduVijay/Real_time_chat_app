from django.test import TestCase
from chat.models import RoomName, Document, Message
from django.contrib.auth.models import User


class ChatRoomTest(TestCase):
    """
    Test case class for testing the models RoomName, Message and Document
    """
    @classmethod
    def setUpTestData(cls):
        #Creating test User
        cls.user1 = User.objects.create(username="user1", password="password1")
        cls.user2 = User.objects.create(username="user2", password="password2")

        #Creating Test room
        cls.room = RoomName.objects.create(name="test room")

        #Creating Test Document
        cls.document = Document.objects.create(
            file="text_document.txt", 
            room_name = cls.room
            )
        
        #Creating test Message
        cls.message= Message.objects.create(
            room_name = cls.room,
            sender = cls.user1,
            recipient = cls.user2,
            content = "Hello user2",
            document = cls.document
        )


    def test_room_name_creation(self):
        """
        Testing RoomName model my creating name
        """
        room = RoomName.objects.get(name="test name")
        self.assertEqual(room.name,"test name")

    def test_document_creation(self):
        """
        Testing the Dcument Model by creating a test document
        """
        document = Document.objects.get(file="text_document.txt")
        self.assertEqual(document.file.name, "media/documents/test_document.txt")
        self.assertEqual(document.room_name, self.room)

    def test_message_creation(self):
        """
        Testing message model by creating a test message
        """
        message = Message.objects.get(content="Hello user2")
        self.assertEqual(message.room_name, self.room)
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.recipient, self.user2)
        self.assertEqual(message.document, self.document)

   

   

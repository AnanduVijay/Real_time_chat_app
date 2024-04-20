from django.db import models
from django.contrib.auth.models import User


class RoomName(models.Model):
    name = models.CharField(max_length=100)
    
    
class Document(models.Model):
    file = models.FileField(upload_to="media/documents/")
    room_name = models.ForeignKey(RoomName, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    room_name = models.ForeignKey(RoomName, on_delete= models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_messages',  on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    document = models.ForeignKey(Document, null=True, on_delete=models.CASCADE)
    
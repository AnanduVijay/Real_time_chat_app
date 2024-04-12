from django.contrib import admin

from chat.models import Message, RoomName, Document

admin.site.register(Message)
admin.site.register(RoomName)
admin.site.register(Document)

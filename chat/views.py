from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from chat.models import  Message, RoomName, Document
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
User = get_user_model()

def home(request):
    user = User.objects.all()
    if not request.user.is_authenticated:
        return redirect("login-user")
    return render(request, "home.html", {"user": user})

def get_user_id(request, user_pk ):
    if request.user.is_authenticated:
        request.session["selected_userid"] = user_pk
        return redirect( "room")
    else:
        return redirect("login-user")
    

def chat_room(request):

    if not request.user.is_authenticated:
        return redirect("login-user")
    
    def get_group_name( user_ids):
        return f"chat_{user_ids[0]}_{user_ids[1]}"
    
    recipient_id= request.session.get('selected_userid')
    sender_id=request.user.id
    sorted_user_ids = sorted([recipient_id, sender_id])
    room_name= get_group_name(sorted_user_ids)
    group_id = RoomName.objects.filter(name=room_name).first()

    if room_name:
        chat_room_message = Message.objects.filter(room_name=group_id).order_by('timestamp')
        chat_room_files = Document.objects.filter(room_name=group_id).order_by('timestamp')
    else:
        chat_room_message = None
    return render( request, "chatroom.html", {'message': chat_room_message, 'files': chat_room_files})


def upload_file(request):

    def get_group_name( user_ids):
        return f"chat_{user_ids[0]}_{user_ids[1]}"
    
    recipient_id= request.session.get('selected_userid')
    sender_id=request.user.id
    sorted_user_ids = sorted([recipient_id, sender_id])
    room_name= get_group_name(sorted_user_ids)
    group_id = RoomName.objects.get(name=room_name)

    if request.method == "POST":
        file_uploaded = request.FILES.get('file')
        if file_uploaded:
            file_obj = Document.objects.create(file=file_uploaded, room_name= group_id)
            file_url = request.build_absolute_uri(file_obj.file.url)
            return JsonResponse({"success": True, "message": "File uploaded successfully", "file_url": file_url, "file_id":file_obj.id})
        
    return JsonResponse({"success": False, "message": "Failed to upload file"})





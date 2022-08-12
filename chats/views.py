from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
#from users.authentication import AllUsersAuthentication
from .models import Message
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED,
                                   HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_503_SERVICE_UNAVAILABLE)
#from .serializers import MessageSerializer
'''
class MessageListView(APIView):
    authentication_classes = [AllUsersAuthentication]


    def get(self,request,id):
        message=Message.objects.filter(sender_name=request.user.id,receiver_id=id)
        serializer=MessageSerializer(message,many=False)
        return Response(serializer.data,status=HTTP_200_OK)
'''
def room(request, room_name):
    return render(request, 'chats/room.html', {
        'room_name': room_name
    })
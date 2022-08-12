from django.urls import path
from .views import *

urlpatterns = [
    #path('user_message_list/', MessageListView.as_view()),
    path('<str:room_name>/', room, name='room'),

]

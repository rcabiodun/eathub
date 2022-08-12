import django
from django.db import models
from datetime import datetime
from django.utils import timezone
import uuid
import secrets
from core.models import User
# Create your models here.

class Message(models.Model):
    sender_id = models.CharField(max_length=50, default='')
    sender_type = models.CharField(max_length=50, default='')
    receiver_id = models.CharField(max_length=50, default='')
    viewed = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)
    subject_line = models.CharField(max_length=50, default='')
    message = models.TextField(max_length=1000, default='')
    sender_delete = models.BooleanField(default=False)
    receiver_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    def getSender_type(self, message):
        return message.sender_type

class MessageGroup(models.Model):
    name=models.CharField(max_length=200)
    member_one = models.ForeignKey(User, related_name='messagegroupm1' ,on_delete=models.CASCADE)
    member_two = models.ForeignKey(User, related_name='messagegroupm2',on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        while not self.name:
            ref = secrets.token_urlsafe(50)
            obj_similar = MessageGroup.objects.filter(name=ref)
            if not obj_similar:
                self.name = ref
        super().save(*args, **kwargs)
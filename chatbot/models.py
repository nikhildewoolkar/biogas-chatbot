from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import *

class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    usernames=models.CharField(max_length=500)
    department=models.CharField(max_length=500)
    phoneno=models.CharField(max_length=500)
    password=models.CharField(max_length=500)
    def __str__(self):  # __str__
        return (self.user.username)
    
class ChatbotLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_logs")
    sentence=models.CharField(max_length=500)
    query=models.CharField(max_length=500)
    ans=models.CharField(max_length=500)
    timestamp=models.DateTimeField(auto_now_add=True)
    def __str__(self):  # __str__
        return (self.user.username)

class Reading(models.Model):
    sensor=models.CharField(max_length=100)
    ts = models.DateTimeField()
    value = models.FloatField()
    def __str__(self):
        return f"Reading {self.value} at {self.ts} for {self.sensor}"
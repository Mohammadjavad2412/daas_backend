from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Users(AbstractUser):
    email = models.CharField(max_length=100,unique=True,null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    

class Daas(models.Model):
    
    TIME_CHOICES = (("PERMANENTLY","PERMANENTLY"),("DAILY","DAILY"),("WEEKLY","WEEKLY"),("MONTHLY","MONTHLY"),("TOTALY","TOTALY"))
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True)
    email = models.CharField(null=False,max_length=100,unique=True)
    http_port = models.PositiveIntegerField(unique=True,null=True)
    https_port = models.PositiveIntegerField(unique=True,null=True)
    time_limit_duration = models.CharField(max_length=20,choices=TIME_CHOICES,default="PERMANENTLY")
    time_limit_value_in_hour = models.PositiveIntegerField(null=True,blank=True)
    last_uptime = models.DateTimeField(null=True,blank=True)
    is_running = models.BooleanField(default=False)
    exceeded_usage = models.BooleanField(default=False)
    container_id = models.CharField(null=False,max_length=50,blank=False)
    usage_in_minute = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
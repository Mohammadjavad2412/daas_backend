from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from config.models import DaasMetaConfig
import uuid
import subprocess


class Users(AbstractUser):
    email = models.CharField(max_length=100,unique=True,null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

def get_or_create_last_config():
    try:
        last_meta_config = DaasMetaConfig.objects.last()
        if not last_meta_config:
            last_meta_config = DaasMetaConfig.objects.create()
    except:
        subprocess.call(['python3','manage.py','makemigrations','config'])
        last_meta_config = DaasMetaConfig.objects.create()
    return last_meta_config


class Daas(models.Model):
    
    TIME_CHOICES = (("PERMANENTLY","PERMANENTLY"),("DAILY","DAILY"),("WEEKLY","WEEKLY"),("MONTHLY","MONTHLY"),("TOTALY","TOTALY"))
    last_meta_config = get_or_create_last_config()
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True)
    email = models.CharField(null=False,max_length=100,unique=True)
    http_port = models.PositiveIntegerField(unique=True,null=True)
    https_port = models.PositiveIntegerField(unique=True,null=True)
    last_uptime = models.DateTimeField(null=True,blank=True)
    is_running = models.BooleanField(default=False)
    exceeded_usage = models.BooleanField(default=False)
    container_id = models.CharField(null=False,max_length=50,blank=False)
    usage_in_minute = models.FloatField(default=0)
    can_upload_file = models.BooleanField(default=last_meta_config.can_upload_file)
    can_download_file = models.BooleanField(default=last_meta_config.can_download_file)
    clipboard_up = models.BooleanField(default=last_meta_config.clipboard_up)
    clipboard_down = models.BooleanField(default=last_meta_config.clipboard_down)
    webcam_privilege = models.BooleanField(default=last_meta_config.webcam_privilege)
    microphone_privilege = models.BooleanField(default=last_meta_config.microphone_privilege)
    time_limit_duration = models.CharField(default=last_meta_config.time_limit_duration)
    time_limit_value_in_hour = models.PositiveIntegerField(null=True,blank=True,default=last_meta_config.time_limit_value_in_hour)
    is_permanently = models.BooleanField(default=last_meta_config.is_permanently)
    max_transmission_upload_size = models.PositiveBigIntegerField(default=last_meta_config.max_transmission_upload_size)
    max_transmission_download_size = models.PositiveBigIntegerField(default=last_meta_config.max_transmission_download_size)
    forbidden_upload_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    forbidden_download_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    extra_allowed_upload_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    extra_allowed_download_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    created_at = models.DateTimeField(null=True,auto_now_add=True)
    
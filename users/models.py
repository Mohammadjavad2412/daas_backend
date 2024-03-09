from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from config.models import DaasMetaConfig
import uuid


class Users(AbstractUser):
    email = models.CharField(max_length=100,unique=True,null=False)
    is_meta_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Daas(models.Model):
    
    TIME_CHOICES = (("PERMANENTLY","PERMANENTLY"),("DAILY","DAILY"),("WEEKLY","WEEKLY"),("MONTHLY","MONTHLY"),("TEMPORARY","TEMPORARY"))
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,unique=True)
    email = models.CharField(null=False,max_length=100,unique=True)
    daas_token = models.CharField(null=True,blank=True,max_length=100,unique=True)
    http_port = models.PositiveIntegerField(unique=True,null=True)
    https_port = models.PositiveIntegerField(unique=True,null=True)
    last_uptime = models.DateTimeField(null=True,blank=True)
    is_running = models.BooleanField(default=False)
    exceeded_usage = models.BooleanField(default=False)
    container_id = models.CharField(null=True,max_length=50,blank=True)
    daas_version = models.CharField(null=True,blank=True)
    usage_in_minute = models.FloatField(default=0)
    daas_configs = models.ForeignKey(DaasMetaConfig,on_delete=models.DO_NOTHING,null=True,blank=True)
    forbidden_upload_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    forbidden_download_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    extra_allowed_upload_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    extra_allowed_download_files = ArrayField(models.CharField(max_length=15,null=True,blank=True),null=True,blank=True)
    last_login_ip = models.CharField(max_length=20,null=True,blank=True)
    is_lock = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True,auto_now_add=True)
    
    
    def save(self,*args,**kwargs) -> None:
        if not self.daas_configs:
            try:
                latest_configs = DaasMetaConfig.objects.get(is_globally_config=True)
            except:
                latest_configs = DaasMetaConfig.objects.create(is_globally_config=True)
            self.daas_configs = latest_configs
        super().save(*args,**kwargs)
        
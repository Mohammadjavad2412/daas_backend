from collections.abc import Iterable
from django.db import models
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Config(models.Model):
    keycloak_base_url = models.URLField(null=False,blank=False)
    keycloak_port = models.PositiveSmallIntegerField(null=False,blank=False)
    keycloak_ssl = models.BooleanField(default=True)
    keycloak_client_id = models.CharField(null=False,blank=False,max_length=200)
    keycloak_secret = models.CharField(null=False,blank=False,max_length=200)
    keycloak_realm = models.CharField(null=False,blank=False,max_length=100)
    daas_provider_baseurl = models.CharField(max_length=200,null=True,default="localhost")
    
    def save(self, *args, **kwargs):
        if not self.pk and Config.objects.exists():
            raise ValidationError(_('There is can be only one config instance'))
        return super(Config, self).save(*args, **kwargs)
    
    
class DaasMetaConfig(models.Model):
    
    TIME_CHOICES = (("PERMANENTLY","PERMANENTLY"),("DAILY","DAILY"),("WEEKLY","WEEKLY"),("MONTHLY","MONTHLY"),("TEMPORARY","TEMPORARY"))

    can_upload_file = models.BooleanField(default=False)
    can_download_file = models.BooleanField(default=False)
    clipboard_up = models.BooleanField(default=False)
    clipboard_down = models.BooleanField(default=False)
    webcam_privilege = models.BooleanField(default=False)
    microphone_privilege = models.BooleanField(default=False)
    time_limit_duration = models.CharField(max_length=20,choices=TIME_CHOICES,default="PERMANENTLY")
    time_limit_value_in_hour = models.PositiveIntegerField(null=True,blank=True)
    max_transmission_upload_size = models.PositiveBigIntegerField(default=50)
    max_transmission_download_size = models.PositiveBigIntegerField(default=500)
    is_globally_config = models.BooleanField(default=False)
    
    def save(self, *args,**kwargs) -> None:
        if not self.pk and self.is_globally_config and Config.objects.exists():
            raise ValidationError(_('There is can be only one config instance'))
        return super().save(*args,**kwargs)
    
    
class WhiteListFiles(models.Model):
    
    file_type = models.CharField(max_length=20,unique=True,null=False,blank=False)
    allowed_for_upload = models.BooleanField(default=False)
    allowed_for_download = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self) -> str:
        return self.file_type
    
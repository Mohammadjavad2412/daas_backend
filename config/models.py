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
        # if you'll not check for self.pk 
        # then error will also be raised in the update of exists model
            raise ValidationError(_('There is can be only one config instance'))
        return super(Config, self).save(*args, **kwargs)
    
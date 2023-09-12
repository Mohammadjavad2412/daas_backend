from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    email = models.EmailField(unique=True,null=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    

class Daas(models.Model):
    email = models.EmailField(null=False)
    http_port = models.PositiveIntegerField(unique=True,null=True)
    https_port = models.PositiveIntegerField(unique=True,null=True)
    
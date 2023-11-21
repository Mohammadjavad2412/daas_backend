from config.models import DaasMetaConfig
from django.core.management.base import BaseCommand


class Command(BaseCommand):
        
    def handle(self,*args,**options):
        meta_config = DaasMetaConfig.objects.all()
        if not meta_config:
            DaasMetaConfig.objects.create()
        
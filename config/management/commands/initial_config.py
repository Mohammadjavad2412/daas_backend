from config.models import DaasMetaConfig
from django.core.management.base import BaseCommand

def initial(BaseComamand):
    
    def handle(self,*args,**options):
        meta_config = DaasMetaConfig.objects.all()
        if not meta_config:
            DaasMetaConfig.objects.create()
        
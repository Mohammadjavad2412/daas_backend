from typing import Any
from django.core.management.base import BaseCommand
from users.models import Daas
from daas.settings import CELERY_PERIODIC_TASK_TIME
from services.desktop import Desktop
import datetime

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        time_band = datetime.datetime.timestamp(datetime.datetime.now()) - 2*(CELERY_PERIODIC_TASK_TIME)
        date_time_band = datetime.datetime.fromtimestamp(time_band)
        daases = Daas.objects.filter(last_uptime__lte=date_time_band)
        for daas in daases:
            http_port = daas.http_port
            Desktop().stop_daas_from_port(http_port)
            daas.last_uptime = datetime.datetime.now()
            daas.is_running=False
            daas.save()
            
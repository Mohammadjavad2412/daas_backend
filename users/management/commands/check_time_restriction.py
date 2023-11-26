from services.desktop import Desktop
from django.core.management.base import BaseCommand
from typing import Any
from users.models import Daas

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        daases = Daas.objects.filter(is_running=True)
        for daas in daases:
            if daas.daas_configs.time_limit_duration != "PERMANENTLY":
                allowed = Desktop().check_time_restriction(daas)
                if not allowed:
                    http_port = daas.http_port
                    Desktop().stop_daas_from_port(http_port)
                    if daas.daas_configs.time_limit_duration == "TEMPORARY":
                        daas.delete()
                    else:
                        daas.is_running=False
                        daas.exceeded_usage = True
                        daas.save()
                        
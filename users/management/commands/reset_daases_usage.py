from services.desktop import Desktop
from django.core.management.base import BaseCommand
from typing import Any
from users.models import Daas
from persiantools.jdatetime import JalaliDate
import datetime


class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        daases = Daas.objects.all()
        for daas in daases:
            if daas.time_limit_duration == 'DAILY':
                daas.usage_in_minute = 0
                daas.exceeded_usage = False
                daas.save()
            elif daas.time_limit_duration == 'WEEKLY':
                today = datetime.date.today().weekday()
                if today == 5:
                    daas.usage_in_minute = 0
                    daas.exceeded_usage = False
                    daas.save()
            elif daas.time_limit_duration == 'MONTHLY':
                today = JalaliDate.today()
                day = today.day
                if day == 1:
                    daas.usage_in_minute = 0
                    daas.exceeded_usage = False
                    daas.save()
                    
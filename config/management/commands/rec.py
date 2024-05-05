from typing import Any
from django.core.management.base import BaseCommand
from services.desktop import Desktop
from users.tasks import concat_records

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        Desktop().kill_recording("298a2f389037")


from typing import Any
from django.core.management.base import BaseCommand
from services.desktop import Desktop

class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        
        Desktop().session_recording("ce762e086cda", "eyvazi.mj@npdco.local")
        
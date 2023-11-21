from typing import Any
from django.core.management.base import BaseCommand
from config.models import DaasMetaConfig
import threading
import subprocess

def run_app():
    subprocess.call(['make','run_app'])

def run_celery():
    subprocess.call(['celery','-A','daas','worker','-B','-l','INFO'])
    
def initial_configs():
    subprocess.call(['python3', 'manage.py', 'initial_config'])

# def run_celery_beat():
#     subprocess.call(['celery','-A','daas','beat','-l','INFO','--scheduler','django_celery_beat.schedulers:DatabaseScheduler'])
    
class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        t1 = threading.Thread(target=run_app)
        t2 = threading.Thread(target=run_celery)
        initial_configs()
        # t3 = threading.Thread(target=run_celery_beat)
        t1.start()
        t2.start()
        # t3.start()
        t1.join()
        t2.join()
        # t3.join()
        
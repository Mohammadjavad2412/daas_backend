from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daas.settings')

app = Celery( 'daas',
               broker=os.getenv("CELERY_BROKER_URL"),
               backend=os.getenv("CELERY_BROKER_URL")
            )

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

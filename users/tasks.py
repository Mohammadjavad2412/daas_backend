from users.models import Daas
from daas.celery import app
from services.desktop import Desktop
from services.syslog import SysLog
from persiantools.jdatetime import JalaliDate
from daas.settings import CELERY_PERIODIC_TASK_TIME
import datetime



logger = SysLog().logger

@app.task
def stop_unused_container():
    logger.info("stop unused containers...")
    time_band = datetime.datetime.timestamp(datetime.datetime.now()) - 2*(CELERY_PERIODIC_TASK_TIME)
    date_time_band = datetime.datetime.fromtimestamp(time_band)
    daases = Daas.objects.filter(last_uptime__lte=date_time_band,is_running=True)
    for daas in daases:
        http_port = daas.http_port
        Desktop().stop_daas_from_port(http_port)
        daas.last_uptime = datetime.datetime.now()
        daas.is_running=False
        daas.save()
        
@app.task
def time_restriction_checker():
    logger.info("time restriction checking...")
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
            
@app.task
def reset_daases_usage():
    logger.info("reset_daases_usage...")
    daases = Daas.objects.all()
    for daas in daases:
        if daas.daas_configs.time_limit_duration == 'DAILY':
            daas.usage_in_minute = 0
            daas.exceeded_usage=False
            daas.save()
        elif daas.daas_configs.time_limit_duration == 'WEEKLY':
            today = datetime.date.today().weekday()
            if today == 5:
                daas.usage_in_minute = 0
                daas.exceeded_usage=False
                daas.save()
        elif daas.daas_configs.time_limit_duration == 'MONTHLY':
            today = JalaliDate.today()
            day = today.day
            if day == 1:
                daas.exceeded_usage=False
                daas.usage_in_minute = 0
                daas.save()
                
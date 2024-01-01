from config.models import Config
import logging
import traceback
import logging.handlers
import os


class SysLog():
    def __init__(self) -> None:        
        try:
            self.logger = logging.getLogger()
            has_log_server = os.getenv("HAS_LOG_SERVER")
            if has_log_server.lower()=="true":
                log_server_ip = Config.objects.all().last().log_server_ip
                log_server_port = Config.objects.all().last().log_server_port
                self.handler = logging.handlers.SysLogHandler(address=(log_server_ip,log_server_port))
                self.logger.addHandler(self.handler)
            self.logger.setLevel(logging.INFO)
        except:
            logging.error(traceback.format_exc())    
        
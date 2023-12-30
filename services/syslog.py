import logging
import logging.handlers
import os


class SysLog():
    def __init__(self) -> None:        
        self.logger = logging.getLogger()
        has_log_server = os.getenv("HAS_LOG_SERVER")
        if has_log_server.lower()=="true":
            log_server_ip = os.getenv("LOG_SERVER_IP")
            log_server_port = int(os.getenv("LOG_SERVER_PORT"))
            self.handler = logging.handlers.SysLogHandler(address=(log_server_ip,log_server_port))
            self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)
        
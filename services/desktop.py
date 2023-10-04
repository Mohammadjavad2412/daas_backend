from daas.settings import BASE_DIR
from users.models import Daas
import os
import random
import socketserver
import subprocess
import socket


class Desktop:
    
    def is_empty_port(self,port):
        pass
    
    def get_user_port(email,port):
        pass
    
    def find_free_port(self,):
        with socketserver.TCPServer(("localhost", 0), None) as s:
            return s.server_address[1]
    
    def get_initial_docker_image(self):
        docker_image_path = os.path.join(BASE_DIR,'docker_image.txt')
        with open(docker_image_path,'r') as docker_image:
            return docker_image.read()
        
    def is_port_free(self,port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
            return True
        except socket.error:
            return False

    def find_free_ports(self,start_port, end_port):
        free_ports = []
        for port in range(start_port, end_port + 1):
            if self.is_port_free(port):
                free_ports.append(port)
        return free_ports

    def random_free_port(self):
        start_port = 30000  # Replace with your start port
        end_port = 31000   # Replace with your end port

        free_ports = self.find_free_ports(start_port, end_port)

        if free_ports:
            random_port = random.choice(free_ports)
        return random_port
        
    def create_daas(self,email,password,http_port=None,https_port=None):
        if not http_port and not https_port:
            http_port = self.random_free_port()
            https_port = self.random_free_port()
            subprocess.call(['docker','run','-d','-e','TITLE=net-sep','-e',f'CUSTOM_USER={email}','-e',f'PASSWORD={password}','-p',f"{http_port}:3000",'-p',f"{https_port}:3001",,"--read-only",'lscr.io/linuxserver/webtop:ubuntu-kde'])
        return http_port,https_port
        
    def stop_daas_from_port(self,port):
        result = subprocess.check_output(['docker','ps','--filter',f"publish={port}",'--format','{{.ID}}'])
        container_id = str(result.strip().decode('utf-8'))
        subprocess.call(['docker','stop',f'{container_id}'])
        
    def check_time_restriction(self,daas:Daas):
        usage_in_minute = daas.usage_in_minute
        allowed_usage_in_hour = daas.time_limit_value_in_hour
        allowed_usage_in_minute = allowed_usage_in_hour * 60
        if usage_in_minute > allowed_usage_in_minute:
            return False
        return True
    
    def get_container_id_from_port(self,port):
        result = subprocess.check_output(['docker','ps','--filter',f"publish={port}",'--format','{{.ID}}'])
        container_id = str(result.strip().decode('utf-8'))
        return container_id
    
    def run_container_by_container_id(self,container_id):
        subprocess.call(['docker','start',f'{container_id}'])
    
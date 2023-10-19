from daas.settings import BASE_DIR
from users.models import Daas
from rest_framework import exceptions
import os
import random
import logging
import socketserver
import subprocess
import socket


logging.basicConfig(level=logging.INFO)

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
        
    def create_daas_with_credential(self,email,password,http_port=None,https_port=None,image_name="netpardaz/netsep:noPrivilage"):
        if not http_port or not https_port:
            http_port = self.random_free_port()
            https_port = self.random_free_port()
        subprocess.call(['docker','run','-d','-e','TITLE=net-sep','-e',f'CUSTOM_USER={email}','-e',f'PASSWORD={password}','-p',f"{http_port}:3000",'-p',f"{https_port}:3001",image_name])
        return http_port,https_port
    
    def create_daas_without_crediential(self,http_port=None,https_port=None,image_name="netpardaz/netsep:noPrivilage"):
        if not http_port and https_port:
            http_port = self.random_free_port()
            https_port = self.random_free_port()
        subprocess.call(['docker','run','-d','-e','TITLE=net-sep','-p',f"{http_port}:3000",'-p',f"{https_port}:3001",image_name])
        return http_port,https_port
    
    def get_image_by_access(self,access_type):
        if access_type == "NO_ACCESS":
            return "netpardaz/netsep:noPrivilage"
        elif access_type == "HAS_ACCESS":
            return "netpardaz/netsep:hasPrivilage"
        
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
        
    def delete_container(self,container_id):
        logging.info(f"delete container id:{container_id}")
        subprocess.call(['docker','stop',f'{container_id}'])
        subprocess.call(['docker','rm',f'{container_id}'])
        
    def get_email_pass_daas(self,container_id):
        result = subprocess.check_output(['docker','exec',f'{container_id}','printenv','CUSTOM_USER'])
        email = str(result.strip().decode('utf-8'))
        result = subprocess.check_output(['docker','exec',f'{container_id}','printenv','PASSWORD'])
        password = str(result.strip().decode('utf-8'))
        return email,password
    
    def restart_daas(self,container_id):
        logging.info(f"restart container id:{container_id}")
        subprocess.call(['docker','restart',f'{container_id}'])
        
    def create_container_with_new_access(self,container_id,new_access):
        try:
            daas = Daas.objects.get(container_id=container_id)
            http_port = daas.http_port
            https_port = daas.https_port
            self.restart_daas(container_id)
            email,password = self.get_email_pass_daas(container_id)
            image = self.get_image_by_access(new_access)
            if image:
                if email and password:
                    self.delete_container(container_id)
                    self.create_daas_with_credential(email,password,http_port,https_port,image)
                else:
                    self.delete_container(container_id)
                    self.create_daas_without_crediential(http_port,https_port,image)
            else:
                raise exceptions.ValidationError('image does not implemented yet')
        except:
            raise exceptions.ValidationError('invalid daas')
        
from daas.settings import BASE_DIR
from users.models import Daas
from django.utils.translation import gettext as _
from django.db.models import Q
from rest_framework import exceptions
from daas import settings
from services.syslog import SysLog
import os
import traceback
import random
import socketserver
import subprocess
import socket
import yaml
import docker


logger = SysLog().logger

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
        start_port = int(os.getenv("DAAS_START_PORT"))
        end_port = int(os.getenv("DAAS_END_PORT"))
        free_ports = self.find_free_ports(start_port, end_port)
        if free_ports:
            random_port = random.choice(free_ports)
            has_used = Daas.objects.filter(Q(http_port=random_port)| Q(https_port=random_port))
            if has_used:
                return self.random_free_port()
        return random_port
        
    def create_daas_with_credential(self,email,password,http_port=None,https_port=None):
        image = os.getenv("DAAS_DOCKER_IMAGE")
        version = os.getenv("DAAS_IMAGE_VERSION")
        image_name = image+":"+version
        if not http_port or not https_port:
            http_port = self.random_free_port()
            https_port = self.random_free_port()
        subprocess.call(['docker','run','-d','-e','TITLE=net-sep','-e',f'TZ={os.getenv("TIME_ZONE")}','-e',f'CUSTOM_USER={email}',
                         '-e',f'PASSWORD={password}','-e',f'FILE_SERVER_HOST={settings.FILE_SERVER_HOST}',
                         '-e',f'MANAGER_HOST={settings.MANEGER_HOST}','-p',f"{http_port}:3000",'-p',f"{https_port}:3001",
                         '--device','/dev/dri:/dev/dri', # mount gpu driver
                         '--shm-size=3gb', # shared memory
                         '--security-opt','seccomp=unconfined', # set security option
                         image_name])
        return http_port,https_port
    
    def create_daas_without_crediential(self,http_port=None,https_port=None):
        image = os.getenv("DAAS_DOCKER_IMAGE")
        version = os.getenv("DAAS_IMAGE_VERSION")
        image_name = image+version
        if not http_port or not https_port:
            http_port = self.random_free_port()
            https_port = self.random_free_port()
        subprocess.call(['docker','run','-d','-e','TITLE=net-sep','-e',f'TZ={os.getenv("TIME_ZONE")}',
                            '-e',f'FILE_SERVER_HOST={settings.FILE_SERVER_HOST}',
                            '-e',f'MANAGER_HOST={settings.MANEGER_HOST}','-p',f"{http_port}:3000",'-p',f"{https_port}:3001",
                            '--device','/dev/dri:/dev/dri', # mount gpu driver
                            '--shm-size=3gb', # shared memory
                            '--security-opt','seccomp=unconfined', # set security option
                            image_name])                         
        return http_port,https_port
            
    def stop_daas_from_port(self,port):
        result = subprocess.check_output(['docker','ps','--filter',f"publish={port}",'--format','{{.ID}}'])
        container_id = str(result.strip().decode('utf-8'))
        subprocess.call(['docker','stop',f'{container_id}'])
        
    def check_time_restriction(self,daas:Daas):
        usage_in_minute = daas.usage_in_minute
        allowed_usage_in_hour = daas.daas_configs.time_limit_value_in_hour
        if allowed_usage_in_hour:
            allowed_usage_in_minute = allowed_usage_in_hour * 60
            if usage_in_minute > allowed_usage_in_minute:
                return False
            return True
        else:
            return False
    
    def get_container_id_from_port(self,port):
        result = subprocess.check_output(['docker','ps','--filter',f"publish={port}",'--format','{{.ID}}'])
        container_id = str(result.strip().decode('utf-8'))
        return container_id
    
    def run_container_by_container_id(self,container_id):
        logger.info(f"run container: {container_id}")
        subprocess.call(['docker','start',f'{container_id}'])
        
    def delete_container(self,container_id):
        logger.info(f"delete container id:{container_id}")
        subprocess.call(['docker','stop',f'{container_id}'])
        subprocess.call(['docker','rm',f'{container_id}'])
        
    def get_email_pass_daas(self,container_id):
        result = subprocess.check_output(['docker','exec',f'{container_id}','printenv','CUSTOM_USER'])
        email = str(result.strip().decode('utf-8'))
        result = subprocess.check_output(['docker','exec',f'{container_id}','printenv','PASSWORD'])
        password = str(result.strip().decode('utf-8'))
        return email,password
    
    def restart_daas(self,container_id):
        logger.info(f"restart container id:{container_id}")
        subprocess.call(['docker','restart',f'{container_id}'])
        
    def get_all_containers(self,):
        cmd = subprocess.check_output(['docker','ps','-a','-q','--filter','ancestor=netpardaz/netsep:latest']) 
        all_containers = str(cmd.strip().decode('utf-8'))
        return all_containers
    
    def get_tag_of_container(self,container_id):
        cmd = subprocess.check_output(["docker","inspect","--format","'{{.Config.Image}}'", container_id])
        image = cmd.strip().decode("utf-8")
        tag = image.split(":")[-1].split("'")[0]
        return tag
        
    def get_latest_version(self):
        client = docker.from_env()
        image = client.images.get(os.getenv("DAAS_DOCKER_IMAGE"))
        return [tag.split(':')[1] for tag in image.tags]
            
    def handle_file_transmition_access(self,container_id,upload_access_mode,download_access_mode):
        pass
    
    def handle_clipboard_access(self,container_id,upload_access_mode=None,download_access_mode=None):
        try:
            task = subprocess.Popen(['docker','exec',f'{container_id}','cat','usr/local/share/kasmvnc/kasmvnc_defaults.yaml'],stdout=subprocess.PIPE)
            file = yaml.safe_load(task.stdout)    
            if upload_access_mode != None:    
                file['data_loss_prevention']['clipboard']['client_to_server']['enabled'] = upload_access_mode
            if download_access_mode != None:
                file['data_loss_prevention']['clipboard']['server_to_client']['enabled'] = upload_access_mode
            with open(f'temp_configs/{container_id}.yml', 'w') as outfile:
                yaml.dump(file, outfile)
            subprocess.call(['docker','cp',f'temp_configs/{container_id}.yml',f'{container_id}:/usr/local/share/kasmvnc/',])
            subprocess.call(['docker','exec',f'{container_id}','cp',f'/usr/local/share/kasmvnc/{container_id}.yml','/usr/local/share/kasmvnc/kasmvnc_defaults.yaml'])
            subprocess.call(['docker','exec',f'{container_id}','rm',f'/usr/local/share/kasmvnc/{container_id}.yml'])
            os.remove(f"{BASE_DIR}/temp_configs/{container_id}.yml")
        except:
            logger.error(traceback.format_exc())
                
    def update_container_with_new_access(self,container_id,validated_data):
        try:
            self.restart_daas(container_id)
            if 'can_upload_file' or 'can_download_file' in validated_data:
                upload_access_mode = validated_data['can_upload_file']
                download_access_mode = validated_data['can_download_file']
                self.handle_file_transmition_access(self,container_id,upload_access_mode,download_access_mode)
            if 'clipboard_up' or 'clipboard_down' in validated_data:
                upload_access_mode = None
                download_access_mode = None
                if 'clipboard_down' in validated_data:
                    upload_access_mode = validated_data['clipboard_up']
                    if upload_access_mode.lower() == 'false':
                        upload_access_mode = False
                    else:
                        upload_access_mode = True
                if 'clipboard_down' in validated_data:
                    download_access_mode = validated_data['clipboard_down']
                    if download_access_mode.lower() == 'false':
                        download_access_mode = False
                    else:
                        download_access_mode = True
                self.handle_clipboard_access(self,container_id,upload_access_mode,download_access_mode)
            self.restart_daas(container_id)
            
        except:
            logger.error(traceback.format_exc())
            raise exceptions.ValidationError(_('invalid daas'))
        
    def update_daas_version(self,container_id,email,password):
        try:
            logger.info(f"update daas for user {email}")
            daas = Daas.objects.get(container_id=container_id)
            self.delete_container(container_id)
            http_port = daas.http_port
            https_port = daas.https_port
            daas.delete()
            credential_env = os.getenv("DAAS_FORCE_CREDENTIAL")
            if credential_env.lower()=="false":
                force_credential = False
            else:
                force_credential = True
            if force_credential:
                Desktop().create_daas_with_credential(email,password,http_port,https_port)
            else:
                Desktop().create_daas_without_crediential(http_port,https_port)
        except:
            raise exceptions.ValidationError(_('invalid daas'))
        
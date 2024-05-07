from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import authenticate , logout
from users.serializers import LogInSerializer,DaasSerializer,UpdateDaasSerializer,UserSerializer,ValidUserSerializer,LogoutSerializer
from users.handler import DaasTokenAuthentication
from daas.permissions import OnlyAdmin,OnlyOwner,OnlyMetaAdmin
from rest_framework.viewsets import ModelViewSet
from services.keycloak import Keycloak
from services.syslog import SysLog
from django.utils.translation import gettext as _
from users.token import CustomToken
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework import filters
from rest_framework.permissions import OR
from services.desktop import Desktop
from daas.pagination import CustomPagination
from users.models import Daas,Users
from config.models import Config
from utils.fuctions import get_client_ip_address
from django.contrib.auth import login
from daas import settings
from django.http import FileResponse
import copy
import time
import os
import subprocess
import secrets
import string
import datetime
import traceback


logger = SysLog().logger

class LogInView(APIView):
    
    throttle_scope = "login"
    
    def post(self,request):
        data = request.data
        serializer_data = LogInSerializer(data=data)
        ip_address = str(get_client_ip_address(request))
        if serializer_data.is_valid():
            valid_datas = serializer_data.validated_data
            email = str(valid_datas['email']).lower()
            user_password = valid_datas['password']
            try:
                authenticator = Keycloak()
                is_valid_user = authenticator.is_valid_user(email,user_password)
                if is_valid_user:
                    logger.info(f"user with email: {email} logged in from ip: {ip_address}")
                    config = Config.objects.all().last()
                    daas = Daas.objects.filter(email__iexact=email).last()
                    if daas:
                        daas_configs = daas.daas_configs
                        usage_in_minute = daas.usage_in_minute
                        forbidden_upload_files = daas.forbidden_upload_files
                        forbidden_download_files = daas.forbidden_download_files
                        extra_allowed_upload_files = daas.extra_allowed_upload_files
                        last_login_ip = daas.last_login_ip
                        extra_allowed_download_files = daas.extra_allowed_download_files
                        token = daas.daas_token
                        is_lock = daas.is_lock
                    latest_tag = os.getenv("DAAS_IMAGE_VERSION")
                    if daas and daas.exceeded_usage == False:
                        if daas.is_running:
                            last_uptime = daas.last_uptime
                            now = datetime.datetime.now()
                            delta_time = now - datetime.timedelta(2*int(os.getenv("CELERY_PERIODIC_TASK_TIME")))
                            if last_uptime > delta_time:
                                file_server_docker_ip = os.getenv("FILE_SERVER_DOCKER_IP")
                                container_ip_address = Desktop().get_container_ip(daas.container_id)
                                if ip_address != daas.last_login_ip and ip_address != os.getenv("FILE_SERVER_HOST") and ip_address != container_ip_address and ip_address!=file_server_docker_ip:
                                    pass
                                    # return Response({'error':_(f"This desktop is using by other user!!")},status=status.HTTP_400_BAD_REQUEST)
                        if daas.is_lock:
                            return Response({"error": _("your account is locked!")},status=status.HTTP_400_BAD_REQUEST)
                        refresh_token = str(CustomToken.for_user(daas))
                        access_token = str(CustomToken.for_user(daas).access_token)
                        http_port = daas.http_port
                        container_id = daas.container_id
                        tag = Desktop().get_tag_of_container(container_id)
                        if tag == latest_tag:
                            Desktop().run_container_by_container_id(container_id,ip_address)
                        else:
                            Desktop().update_daas_version(container_id,email,user_password,token,ip_address)
                            container_id = Desktop().get_container_id_from_port(http_port)
                            Desktop().session_recording(container_id=container_id, email=email)
                            daas.container_id = container_id
                            daas.daas_configs = daas_configs
                            daas.usage_in_minute = usage_in_minute
                            daas.forbidden_upload_files = forbidden_upload_files
                            daas.forbidden_download_files = forbidden_download_files
                            daas.extra_allowed_upload_files = extra_allowed_upload_files
                            daas.extra_allowed_download_files = extra_allowed_download_files
                        if ip_address != os.getenv("FILE_SERVER_HOST"):
                            daas.last_login_ip = last_login_ip
                        daas.is_lock = is_lock
                        daas.is_running=True
                        daas.last_uptime=datetime.datetime.now()
                        daas.daas_version = latest_tag
                        if ip_address != Desktop().get_container_ip(daas.container_id):
                            daas.last_login_ip = ip_address
                        daas.save()
                        Desktop().session_recording(container_id=container_id,email=email)
                        return Response({"http":f"http://{config.daas_provider_baseurl}:{daas.http_port}","https":f"https://{config.daas_provider_baseurl}:{daas.https_port}","refresh_token":refresh_token,"access_token":access_token},status.HTTP_200_OK)
                    elif daas and daas.exceeded_usage:
                        return Response({"error":_("you reach your time limit!")},status=status.HTTP_403_FORBIDDEN)
                    else:
                        token = None
                        credential_env = os.getenv("DAAS_FORCE_CREDENTIAL")
                        if credential_env.lower()=='token':
                            alphabet = string.ascii_letters + string.digits
                            token = ''.join(secrets.choice(alphabet) for i in range(40))
                            http_port,https_port = Desktop().create_daas_with_token(email,token,ip_address)
                            # Desktop().set_ip_restriction_by_port(ip_address,http_port)
                        elif credential_env.lower()=="false":
                            http_port,https_port = Desktop().create_daas_without_crediential()
                        else:
                            http_port,https_port = Desktop().create_daas_with_credential(email,user_password)    
                        container_id = Desktop().get_container_id_from_port(http_port)
                        daas = Daas.objects.create(email=email,daas_token=token,http_port=http_port,https_port=https_port,is_running=True,last_uptime=datetime.datetime.now(),container_id=container_id,daas_version=latest_tag,last_login_ip=ip_address)
                        refresh_token = str(CustomToken.for_user(daas))
                        access_token = str(CustomToken.for_user(daas).access_token)
                        return Response({"http":f"http://{config.daas_provider_baseurl}:{http_port}","https":f"https://{config.daas_provider_baseurl}:{https_port}","refresh_token":refresh_token,"access_token":access_token},status.HTTP_200_OK)
                else:
                    try:
                        user = authenticate(request,email=email,password=user_password)
                        if user and user.is_superuser:
                            logger.info(f"an admin with email: {email} logged in from ip: {ip_address}")
                            user = Users.objects.get(email=email)
                            refresh_token = str(RefreshToken.for_user(user))
                            access_token = str(RefreshToken.for_user(user).access_token)
                            login(request,user)
                            return Response({"info":_("successfull"),"access_token":access_token,"refresh_token":refresh_token},status=status.HTTP_200_OK)
                        else:
                            return Response({"error":_("invalid username or password")},status=status.HTTP_400_BAD_REQUEST)
                    except:
                        logger.error(traceback.format_exc())
                        return Response({"error":_("internal server error")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except:
                logger.error(traceback.format_exc())
                # used when no authentication set or handle
                try:
                    user = authenticate(request,email=email,password=user_password)
                    if user and user.is_superuser:
                        logger.info(f"an admin with email: {email} logged in from ip: {ip_address}")
                        user = Users.objects.get(email=email)
                        refresh_token = str(RefreshToken.for_user(user))
                        access_token = str(RefreshToken.for_user(user).access_token)
                        login(request,user)
                        return Response({"info":_("successfull"),"access_token":access_token,"refresh_token":refresh_token},status=status.HTTP_200_OK)
                    else:
                        return Response({"error":_("invalid username or password")},status=status.HTTP_400_BAD_REQUEST)
                except:
                    logger.error(traceback.format_exc())
                    return Response({"error":_("internal server error")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer_data.errors,status=status.HTTP_400_BAD_REQUEST)
    

class DaasView(ModelViewSet):
    
    queryset=Daas.objects.all()
    serializer_class=DaasSerializer
    filter_backends = [filters.SearchFilter]
    authentication_classes=(DaasTokenAuthentication,)
    search_fields = ['email',]
    pagination_class = CustomPagination
    http_method_name=['get','patch','delete','option','head']
    
    
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['online_users'] = Daas.objects.filter(is_running=True).count()
        response.data['online_recording_sessions'] = Daas.objects.filter(daas_configs__is_recording=True).count()
        return response
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return UpdateDaasSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'retrieve':
            return[OR(OnlyOwner(),OnlyAdmin())]
        else:
            return[OnlyAdmin()]
    
    def update(self, request, *args, **kwargs):
        try:
            daas = self.get_object()
            data = request.data
            user = request.user
            ser_data = UpdateDaasSerializer(instance=daas,data=data)
            if ser_data.is_valid():
                ser_data.save()
                logger.info(f"user : {user.email} update daas for user: {daas.email} with data {data}")
                return Response({"info":_("successfull")},status=status.HTTP_202_ACCEPTED)
            else:
                return Response(ser_data.errors,status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.error(traceback.format_exc())
            return Response({"error":_("invalid data passed")},status=status.HTTP_400_BAD_REQUEST)
        
    def destroy(self, request,pk,*args, **kwargs):
        daas = self.get_object()
        user = request.user
        if daas:
            container_id = daas.container_id
            logger.info(f"user : {user.email} destroy daas for user: {daas.email}")
            subprocess.call(['docker','stop',f'{container_id}'])
            subprocess.call(['docker','rm',f'{container_id}'])
        return super().destroy(request, *args, **kwargs)
        
class Profile(ModelViewSet):
    
    authentication_classes = (DaasTokenAuthentication,)
    permission_classes = [OnlyOwner|OnlyAdmin]
    
    def get(self,request):
        requester = request.user
        if isinstance(requester,Daas):
            if requester.is_lock:
                return Response({"error":_("you are blocked!")},status=status.HTTP_401_UNAUTHORIZED)
            ser_data = DaasSerializer(requester)
        elif isinstance(requester,Users):
            ser_data = UserSerializer(requester)
        else:
            return Response({"error":_("invalid data passed")},status=status.HTTP_400_BAD_REQUEST)
        return Response(ser_data.data,status=status.HTTP_200_OK)
        

class UpdateUsage(ModelViewSet):
    authentication_classes = (DaasTokenAuthentication,)
    permission_classes = [OnlyOwner,]
    
    def get(self,request):
        try:
            daas = request.user
            if daas and daas and daas.is_running:
                if daas.is_lock:
                    return Response({"error":_("you are blocked!")},status=status.HTTP_401_UNAUTHORIZED)
                last_uptime = datetime.datetime.timestamp(daas.last_uptime)
                now = datetime.datetime.now().timestamp()
                usage = (now - last_uptime)/60
                last_usage = daas.usage_in_minute
                daas.usage_in_minute = last_usage+usage 
                daas.last_uptime = datetime.datetime.now()
                daas.save()
                return Response({"info":_("successfully update")},status=status.HTTP_200_OK)
            else:
                return Response({"error":_("you can't update usage of down desktop!")},status=status.HTTP_401_UNAUTHORIZED)
        except:
            logger.error(traceback.format_exc())
            return Response({"error":_("internal server error")},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class ResetUsage(ModelViewSet):
    queryset = Daas.objects.all()
    authentication_classes = (DaasTokenAuthentication,)
    permission_classes = (OnlyAdmin,)
    http_method_names = ['get',]
    serializer_class = DaasSerializer
    
    
    def list(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"user: {user.email} restart all usage of daases")
        daases = self.get_queryset()
        for daas in daases:
            daas.usage_in_minute = 0
            daas.exceeded_usage = False
            daas.save()
            return Response({"info":_("reset successfully")})
    
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        daas = self.get_object()
        daas.usage_in_minute = 0
        daas.exceeded_usage = False
        daas.save()
        logger.info(f"user: {user.email} restart usage of user's daas with email {daas.email}")
        return Response({"info":_("reset successfully")})
    
        
class IsValidUser(APIView):
    def post(self,request):
        try:
            data = request.data
            ser_data = ValidUserSerializer(data=data)
            if ser_data.is_valid():
                valid_datas = ser_data.validated_data
                email = valid_datas['email']
                user_password = valid_datas['password']
                if os.getenv("DAAS_FORCE_CREDENTIAL") != "token":
                    authenticator = Keycloak()
                    is_valid_user = authenticator.is_valid_user(email,user_password)
                    return Response({"info":is_valid_user},status=status.HTTP_200_OK)
                else:
                    try:
                        daas = Daas.objects.get(email=email,token=user_password)
                        if daas:
                            return Response({"info":True},status=status.HTTP_200_OK)
                        else:
                            return Response({"info":True},status=status.HTTP_200_OK)
                    except:
                        return Response({"info":True},status=status.HTTP_200_OK)
            else:
                return Response(ser_data.errors,status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.info(traceback.format_exc())
            return Response({"error":_("internal server error")})
        
        
class UsersView(ModelViewSet):
    
    queryset=Users.objects.filter(is_superuser=True)
    serializer_class = UserSerializer
    permission_classes = [OnlyMetaAdmin]
    authentication_classes = (DaasTokenAuthentication,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['email','username']
    pagination_class = CustomPagination
    
    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        data.pop("password")
        user = request.user
        logger.info(f"{user.email} create superuser with data {data}")
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        obj = self.get_object()
        logger.info(f"user: {request.user.email} update admin with email {obj.email} and data: {data}")
        return super().update(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(is_superuser=True)
        
    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        if request.user.email == obj.email:
            return Response({"error":_("you can't delete yourself!")},status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"user: {request.user.email} delete admin with email {obj.email}")
        return super().destroy(request, *args, **kwargs)
    
class LockRequestView(ModelViewSet):
    queryset = Daas.objects.all()
    authentication_classes = (DaasTokenAuthentication,)
    http_method_names = ['get']
    
    def list(self,request):
        daas = request.user
        daas.is_lock = True
        Desktop().stop_daas_from_port(daas.http_port)
        daas.save()
        logger.info(f"daas with email : {daas.email} locked!")
        return Response({"info":_("locked account successfully")})
    
    def retrieve(self, request, *args, **kwargs):
        return Response({"error":_("can't lock account with given id")})
    

class LogOutView(ModelViewSet):
    queryset = Daas.objects.all()
    serializer_class = LogoutSerializer
    authentication_classes = (DaasTokenAuthentication,)
    http_method_names = ['post']
    
    def create(self, request, *args, **kwargs):
        data = request.data
        ser_data = LogoutSerializer(data=data)
        if ser_data.is_valid():
            refresh_token = request.data['refresh_token']
            if isinstance(request.user,Daas):
                daas = request.user
                http_port = daas.http_port
                daas.is_running = False
                daas.last_uptime = datetime.datetime.now()
                daas.save()
                Desktop().stop_daas_from_port(http_port)
            elif isinstance(request.user,Users):
                logout(request)     
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"info":_("log out successfully")},status=status.HTTP_200_OK)
        else:
            return Response(ser_data.errors,status=status.HTTP_400_BAD_REQUEST)
    

class RecordsListView(APIView):


    def get(self, request):
        try:
            id = request.query_params.get('id')
            daas_user = Daas.objects.get(id=id)
            daas_user_email = daas_user.email
            dir = os.path.join(settings.BASE_DIR, "streams")
            all_contents = os.listdir(dir)
            response = {}
            for content in all_contents:
                if os.path.isdir(os.path.join(dir, content)) and content == daas_user_email:
                    user_path = os.path.join(dir, content)                    
                    for root, dirs, files in os.walk(user_path):
                        if files:
                            day_time = root.split('/')[-1]
                            response[day_time] = files
            response_copy = response.copy()
            result = {"today": {}, "history": {}}
            for date, file_names in response_copy.items():
                val_list = []
                for file_name in file_names:
                    record_time_estimate = Desktop().get_recording_length(f"{daas_user_email}/{date}/{file_name}")
                    val = {"record_length": record_time_estimate, "record_name": file_name}
                    val_list.append(val)
                today = str(datetime.datetime.today().strftime('%Y%m%d'))
                # today = "20240423"
                if date == today:
                    result["today"][date] = val_list
                else:
                    result["history"][date] = val_list
            return Response(result, status.HTTP_200_OK)
        except:
            logger.error(traceback.format_exc())

            
class RecordsFileView(APIView):

    def get(self, request):
        try:
            record_name = request.query_params.get("record_name")
            user_record_name = record_name.split('_')[0]
            day_time = record_name.split('_')[2]
            dir = os.path.join(settings.BASE_DIR, "streams")
            for root, dirs, files in os.walk(dir):
                if user_record_name in dirs:
                    user_dir_path = os.path.join(dir, user_record_name)
                    record_file_path = os.path.join(user_dir_path,day_time,record_name)
                    if os.path.exists(record_file_path):
                        response = FileResponse(open(record_file_path, 'rb'))
                        return response
                    else:
                        return Response({'error': 'file not found'}, status.HTTP_400_BAD_REQUEST)
        except:
            logger.error(traceback.format_exc())


                    



























# class DeleteAllDesktops(ModelViewSet):
#     queryset = Daas.objects.all()
#     authentication_classes = (DaasTokenAuthentication,)
#     permission_classes = [OnlyMetaAdmin,]
#     http_method_names = ['get']
    
#     def list(self, request, *args, **kwargs):
#         Desktop().delete_all_containers()
#         daases = Daas.objects.all().delete()
#         return Response({"info":_("deleted succesfully")})
    
#     def retrieve(self, request, *args, **kwargs):
#         return Response({"error":_("retrieve method not allowed")})
    
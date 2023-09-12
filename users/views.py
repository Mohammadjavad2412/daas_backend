from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import authenticate
from users.serializers import LogInSerializer,DaasSerializer
from daas.permissions import OnlyAdmin
from services.keycloak import Keycloak
from django.utils.translation import gettext as _
from django.db.models import Q
from rest_framework import filters
from services.desktop import Desktop
from daas.pagination import CustomPagination
from users.models import Daas
from config.models import Config
from utils.fuctions import get_client_ip_address
import subprocess
import logging 
import traceback
import logging

logging.basicConfig(level=logging.INFO)

class LogInView(APIView):
    
    def post(self,request):
        data = request.data
        serializer_data = LogInSerializer(data=data)
        if serializer_data.is_valid():
            valid_datas = serializer_data.validated_data
            is_admin = valid_datas['is_admin']
            email = valid_datas['email']
            password = valid_datas['password']
            if not is_admin:
                authenticator = Keycloak()
                is_valid_user = authenticator.is_valid_user(email,password)
                if is_valid_user:
                    ip_address = get_client_ip_address(request)
                    logging.info(f"user with email: {email} logged in from ip: {ip_address}")
                    config = Config.objects.all().last()
                    daas = Daas.objects.filter(email=email).last()
                    if daas:
                        return Response({"http":f"http://{config.daas_provider_baseurl}:{daas.http_port}","https":f"https://{config.daas_provider_baseurl}:{daas.https_port}"},status.HTTP_200_OK)
                    else:
                        http_port,https_port = Desktop().create_daas(email,password)
                        Daas.objects.create(email=email,http_port=http_port,https_port=https_port)
                        return Response({"http":f"http://{config.daas_provider_baseurl}:{http_port}","https":f"https://{config.daas_provider_baseurl}:{https_port}"},status.HTTP_200_OK)
                else:
                    return Response({"error":_("invalid user")},status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    user = authenticate(request,email=email,password=password)
                    if user.is_superuser:
                        return Response({"info":_("successfull")},status=status.HTTP_200_OK)
                    else:
                        return Response({"error":_("you are not admin")},status=status.HTTP_400_BAD_REQUEST)
                except:
                    logging.error(traceback.format_exc())
                    return Response({"error":_("invalid username or password")},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer_data.errors,status=status.HTTP_400_BAD_REQUEST)
    
        
class DaasView(ModelViewSet):
    
    queryset=Daas.objects.all()
    model=Daas
    serializer_class=DaasSerializer
    permission_classes=(OnlyAdmin,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['email',]
    pagination_class = CustomPagination
    http_method_name=['get','delete','option','head']
    
    def destroy(self, request,pk,*args, **kwargs):
        daas = self.get_object()
        if daas:
            http = daas.http_port
            result = subprocess.check_output(['docker','ps','--filter',f"publish={http}",'--format','{{.ID}}'])
            container_id = str(result.strip().decode('utf-8'))
            subprocess.call(['docker','stop',f'{container_id}'])
            subprocess.call(['docker','rm',f'{container_id}'])
        return super().destroy(request, *args, **kwargs)
        
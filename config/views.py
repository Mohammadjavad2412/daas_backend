from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from daas.permissions import OnlyAdmin
from config.models import Config,WhiteListFiles,DaasMetaConfig
from config.serializers import ConfigSerializer,WhiteListFilesSerializer,DaasMetaConfigSerializer
from services.syslog import SysLog
from daas.pagination import CustomPagination

logger = SysLog().logger

class ConfigView(ModelViewSet,):
    queryset = Config.objects.all()
    permission_classes = (OnlyAdmin,)
    serializer_class = ConfigSerializer
    http_method_names = ['put','patch','get']
    
    def create(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"user: {user.email} create config")
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        data = request.data
        logger.info(f"user: {user.email} update config with config {obj} with data {data}")
        return super().update(request, *args, **kwargs)
    

class DaasMetaConfigView(ModelViewSet):
    queryset = DaasMetaConfig.objects.all()
    serializer_class = DaasMetaConfigSerializer
    permission_classes = [OnlyAdmin,]
    pagination_class = CustomPagination
    http_method_names = ['post','put','patch','get']
    
    def update(self, request, *args, **kwargs):
        user = request.user
        logger.info(f"user : {user.email} update daas meta configs with data {request.data}")
        return super().update(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        try:
            config = DaasMetaConfig.objects.get(is_globally_config=True)
            ser_config = DaasMetaConfigSerializer(config)
            return Response(ser_config.data,status=status.HTTP_200_OK)
        except:
            return Response({},status=status.HTTP_200_OK)
        
    
class WhiteListFilesView(ModelViewSet):
    queryset = WhiteListFiles.objects.all().order_by('-updated_at')
    serializer_class = WhiteListFilesSerializer
    permission_classes = [OnlyAdmin,]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['file_type']
    
    
    def update(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        obj = self.get_object()
        logger.info(f"user : {user.email} update object : {obj} with data: {data}")
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        obj = self.get_object()
        logger.info(f"user : {user.email} delete object : {obj}")
        return super().destroy(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        logger.info(f"user : {user.email} create white list with data: {data}")
        return super().create(request, *args, **kwargs)
    
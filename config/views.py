from rest_framework.viewsets import ModelViewSet
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from daas.permissions import OnlyAdmin
from config.models import Config,WhiteListFiles,DaasMetaConfig
from config.serializers import ConfigSerializer,WhiteListFilesSerializer,DaasMetaConfigSerializer
from daas.pagination import CustomPagination
import logging



class ConfigView(ModelViewSet,):
    queryset = Config.objects.all()
    permission_classes = (OnlyAdmin,)
    serializer_class = ConfigSerializer
    

class DaasMetaConfigView(ModelViewSet):
    queryset = DaasMetaConfig.objects.all()
    serializer_class = DaasMetaConfigSerializer
    permission_classes = [OnlyAdmin,]
    pagination_class = CustomPagination
    http_method_names = ['get','put','patch']
    
    def update(self, request, *args, **kwargs):
        user = request.user
        logging.info(f"user : {user.email} update daas config")
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
    
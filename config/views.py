from rest_framework.viewsets import ModelViewSet
from daas.permissions import OnlyAdmin
from config.models import Config,WhiteListFiles,DaasMetaConfig
from config.serializers import ConfigSerializer,WhiteListFilesSerializer,DaasMetaConfig
from daas.pagination import CustomPagination
import logging



class ConfigView(ModelViewSet,):
    queryset = Config.objects.all()
    permission_classes = (OnlyAdmin,)
    serializer_class = ConfigSerializer
    

class DaasMetaConfigView(ModelViewSet):
    queryset = DaasMetaConfig.objects.all()
    serializer_class = DaasMetaConfig
    permission_classes = [OnlyAdmin,]
    # pagination_class = CustomPagination
    http_method_names = ['get','put','patch']
    
    def update(self, request, *args, **kwargs):
        user = request.user
        logging.info(f"user : {user.email} update daas config")
        return super().update(request, *args, **kwargs)
    
class WhiteListFilesView(ModelViewSet):
    queryset = WhiteListFiles.objects.all()
    serializer_class = WhiteListFilesSerializer
    permission_classes = [OnlyAdmin,]
    pagination_class = CustomPagination
    search_fields = ['file_type']
    
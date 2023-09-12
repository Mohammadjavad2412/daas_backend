from rest_framework.viewsets import ModelViewSet
from daas.permissions import OnlyAdmin
from config.models import Config
from config.serializers import ConfigSerializer


class ConfigView(ModelViewSet,):
    queryset = Config.objects.all()
    permission_classes = (OnlyAdmin,)
    serializer_class = ConfigSerializer
    
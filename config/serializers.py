from rest_framework.serializers import ModelSerializer
from config.models import Config


class ConfigSerializer(ModelSerializer):
    class Meta:
        model = Config
        fields="__all__"
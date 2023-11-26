from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from config.models import Config,WhiteListFiles,DaasMetaConfig
from users.models import Daas
from django.db.transaction import atomic

class ConfigSerializer(ModelSerializer):
    class Meta:
        model = Config
        fields="__all__"
        

class DaasMetaConfigSerializer(ModelSerializer):
    class Meta:
        model = DaasMetaConfig
        fields="__all__"
    
    # @atomic
    # def create(self, validated_data):
    #     if validated_data['is_globally_config']:
    #         daases = Daas.objects.all()
    #         last_config = DaasMetaConfig.objects.last()
    #         for daas in daases:
    #             for key,value in validated_data:
    #                 if daas.__getattribute__(key) == last_config.__getattribute__(key):
    #                     daas.__setattr__(key,value)
    #             daas.save()
    #     return super().create(validated_data)    
    
    @atomic
    def update(self, instance, validated_data):
        daases = Daas.objects.all()
        for daas in daases:
            if daas.daas_configs.is_globally_config:
                for key,value in validated_data.items():
                    daas.daas_configs.__setattr__(key,value)
                daas.save()
        return super().update(instance, validated_data)
    
    
class WhiteListFilesSerializer(ModelSerializer):
    class Meta:
        model = WhiteListFiles
        fields = '__all__'
        
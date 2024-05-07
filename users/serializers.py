from rest_framework import serializers
from drf_writable_nested import WritableNestedModelSerializer
from users.models import Daas,Users
from config.models import Config,WhiteListFiles,DaasMetaConfig
from config.serializers import DaasMetaConfigSerializer
from users.token import CustomToken
from services.desktop import Desktop
import base64


class LogInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    
    
class ValidUserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    
    
class DaasSerializer(serializers.ModelSerializer):
    allowed_files_type_for_upload = serializers.SerializerMethodField("get_allowed_upload_files_type")
    allowed_files_type_for_download = serializers.SerializerMethodField("get_allowed_download_files_type")
    base_url = serializers.SerializerMethodField('get_base_url')
    daas_configs = DaasMetaConfigSerializer()
    
    class Meta:
        model = Daas
        fields = ('id','email','http_port','https_port','last_uptime','exceeded_usage','is_running','base_url',
                  'usage_in_minute','forbidden_upload_files','forbidden_download_files','extra_allowed_upload_files','daas_version','extra_allowed_download_files',
                  'allowed_files_type_for_upload','allowed_files_type_for_download','daas_configs','container_id','last_login_ip','is_lock','created_at')
        
    def get_base_url(self,obj):
        return Config.objects.all().first().daas_provider_baseurl
    
    def get_allowed_upload_files_type(self,obj):
        defaults =  [obj.file_type for obj in WhiteListFiles.objects.filter(allowed_for_upload=True,is_active=True)]
        forbiddens = obj.forbidden_upload_files
        extra_allowed = obj.extra_allowed_upload_files
        if not extra_allowed:
            extra_allowed = []
        only_allowed = defaults + extra_allowed
        if forbiddens and only_allowed:
            all_allowed_upload_file = set(only_allowed) - set(forbiddens)
        elif not forbiddens and only_allowed:
            all_allowed_upload_file = only_allowed
        else:
            return None
        return list(all_allowed_upload_file)
    
    def get_allowed_download_files_type(self,obj):
        defaults =  [obj.file_type for obj in WhiteListFiles.objects.filter(allowed_for_download=True,is_active=True)]
        forbiddens = obj.forbidden_download_files
        extra_allowed = obj.extra_allowed_download_files
        if not extra_allowed:
            extra_allowed = []
        only_allowed = defaults+extra_allowed
        if forbiddens and only_allowed:
            all_allowed_download_file = set(only_allowed) - set(forbiddens)
        elif not forbiddens and only_allowed:
            all_allowed_download_file = only_allowed
        else:
            return None
        return list(all_allowed_download_file)
    
    
class UpdateDaasSerializer(WritableNestedModelSerializer,serializers.ModelSerializer):
    daas_configs = DaasMetaConfigSerializer()
    
    class Meta:
        model = Daas
        fields = ['forbidden_upload_files','forbidden_download_files','extra_allowed_upload_files','extra_allowed_download_files','daas_configs','is_lock']
        
    def update(self, instance, validated_data):
        if 'daas_configs' in validated_data:
            instance.daas_configs.is_globally_config = False
        record = validated_data['daas_configs']['is_recording']
        prev_record = instance['daas_configs']['is_recording']
        if not record and prev_record:
            container_id = instance.container_id
            Desktop().kill_recording(container_id)
        elif record and not prev_record:
            container_id = instance.container_id
            email = instance.email
            Desktop().session_recording(container_id, email)
        return super().update(instance, validated_data)
                
                
class DaasTokenObtainSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        try:
            obj = Daas.objects.get(email=email)
        except Daas.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')
        attrs['obj'] = obj
        return attrs
    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
    def create(self, validated_data):
        if "password" in validated_data:
            user = super().create(validated_data)
            user.set_password(validated_data['password'])
            user.save()
            validated_data.pop("password")
            return user
        else:
            return super().create(validated_data)
          
    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            same_password_sent = instance.check_password(password)
            if same_password_sent:
                raise serializers.ValidationError("try another password")
            instance.set_password(password)
        return super().update(instance, validated_data)
            

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    
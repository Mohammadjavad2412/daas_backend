from rest_framework import serializers
from users.models import Daas,Users
from config.models import WhiteListFiles
from config.serializers import WhiteListFilesSerializer
from config.models import Config,DaasMetaConfig


class LogInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    is_admin = serializers.BooleanField(required=True)
    
    
class ValidUserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    
    
class DaasSerializer(serializers.ModelSerializer):
    allowed_files_type_for_upload = serializers.SerializerMethodField("get_allowed_upload_files_type")
    allowed_files_type_for_download = serializers.SerializerMethodField("get_allowed_download_files_type")
    base_url = serializers.SerializerMethodField('get_base_url')
    
    class Meta:
        model = Daas
        fields = ('id','email','http_port','https_port','can_upload_file','can_download_file','clipboard_up','clipboard_down','webcam_privilege',
                  'microphone_privilege','time_limit_duration','time_limit_value_in_hour','last_uptime','exceeded_usage','is_running','base_url',
                  'usage_in_minute','forbidden_upload_files','forbidden_download_files','extra_allowed_upload_files','extra_allowed_download_files',
                  'allowed_files_type_for_upload','allowed_files_type_for_download','max_transmission_upload_size','max_transmission_download_size')
        
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
    
    
class UpdateDaasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daas
        fields = ['time_limit_duration','time_limit_value_in_hour','can_upload_file','can_download_file','clipboard_up','clipboard_down','webcam_privilege',
                  'microphone_privilege','forbidden_upload_files','forbidden_download_files','extra_allowed_upload_files','extra_allowed_download_files','max_transmission_upload_size','max_transmission_download_size']
                
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
      
      
class ChangePasswordSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Users
        fields = ['email','password']  
        
    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            same_password_sent = instance.check_password(password)
            if same_password_sent:
                raise serializers.ValidationError("try another password")
            instance.set_password(password)      
            return super().update(instance, validated_data)
        else:
            raise serializers.ValidationError("password not sent")
        
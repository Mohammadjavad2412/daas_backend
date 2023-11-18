from rest_framework import serializers
from users.models import Daas,Users
from config.models import Config


class LogInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    is_admin = serializers.BooleanField(required=True)
    
    
class ValidUserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    
    
class DaasSerializer(serializers.ModelSerializer):
    
    base_url = serializers.SerializerMethodField('get_base_url')
    
    class Meta:
        model = Daas
        fields = ('id','email','http_port','https_port','can_upload_file','can_download_file','clipboard_up','clipboard_down','webcam_privilege',
                  'microphone_privilege','time_limit_duration','time_limit_value_in_hour','last_uptime','exceeded_usage','is_running','base_url','usage_in_minute','forbidden_upload_files','forbidden_download_files','created_at')
        
    def get_base_url(self,obj):
        return Config.objects.all().first().daas_provider_baseurl
    
        
class UpdateDaasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daas
        fields = ['time_limit_duration','time_limit_value_in_hour','can_upload_file','can_download_file','clipboard_up','clipboard_down','webcam_privilege',
                  'microphone_privilege','forbidden_upload_files','forbidden_download_files']
    
        
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
        
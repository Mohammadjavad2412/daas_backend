from rest_framework import serializers
from users.models import Daas,Users
from config.models import Config


class LogInSerializer(serializers.Serializer):
    email = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    is_admin = serializers.BooleanField(required=True)
    

class DaasSerializer(serializers.ModelSerializer):
    
    base_url = serializers.SerializerMethodField('get_base_url')
    
    class Meta:
        model = Daas
        fields = ('id','email','http_port','https_port','time_limit_duration','time_limit_value_in_hour','last_uptime','exceeded_usage','is_running','base_url','usage_in_minute','created_at')
        
    def get_base_url(self,obj):
        return Config.objects.all().first().daas_provider_baseurl
        
class UpdateDaasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daas
        fields = ['time_limit_duration','time_limit_value_in_hour',]
       
        
class DaasTokenObtainSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        
        try:
            obj = Daas.objects.get(email=email)  # Adjust this to match your model's fields
        except Daas.DoesNotExist:
            raise serializers.ValidationError('Invalid credentials')

        attrs['obj'] = obj
        return attrs
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        
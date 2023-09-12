from rest_framework import serializers
from users.models import Daas


class LogInSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True,write_only=True)
    password = serializers.CharField(required=True,write_only=True)
    is_admin = serializers.BooleanField(required=True)
    

class DaasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Daas
        fields = "__all__"
        
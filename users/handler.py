from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from users.models import Daas,Users

class DaasTokenAuthentication(JWTAuthentication):

    def authenticate(self, request):
        try:
            validated_token = self.get_validated_token(self.get_raw_token(self.get_header(request)))
            # Now, validated_token is an instance of your CustomToken class
            obj = self.get_obj(validated_token)
            return obj, validated_token
        except:pass

    def get_obj(self, validated_token):
        try:
            obj_id = validated_token.payload['obj_id']  # get the custom model instance's id from the payload
            obj = Daas.objects.get(id=obj_id)
        except:
            obj_id = validated_token.payload['user_id']  # get the default model instance's id from the payload
            obj = Users.objects.get(id=obj_id)
        return obj
    
from rest_framework_simplejwt.tokens import RefreshToken


class CustomToken(RefreshToken):
    @classmethod
    def for_user(cls, obj):
        token = cls()
        # Assuming obj is an instance of your custom model
        token.payload['obj_id'] = str(obj.id)  # add the custom model instance's id to the payload
        token.payload['obj'] = str(obj)
        return token
    
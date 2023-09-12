from config.models import Config
import requests


class Keycloak:
    def __init__(self) -> None:
        config = Config.objects.first()
        self.host = config.keycloak_base_url
        self.port = config.keycloak_port
        self.client_id = config.keycloak_client_id
        self.client_secret = config.keycloak_secret
        self.realm_name = config.keycloak_realm
        
    def is_valid_user(self,username,password):
        
        # Authenticate with Keycloak to obtain an access token
        token_url = f"{self.host}:{self.port}/realms/{self.realm_name}/protocol/openid-connect/token"
        token_data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username":username,
            "password":password
        }
        token_response = requests.post(token_url, data=token_data)
        if token_response.status_code == 200:
            return True
        return False
    
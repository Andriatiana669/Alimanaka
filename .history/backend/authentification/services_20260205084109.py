import requests
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class KeycloakService:
    """Service pour interagir avec Keycloak"""
    
    @staticmethod
    def get_oidc_config():
        """Récupère la configuration OIDC depuis Keycloak"""
        config_url = f"{settings.KEYCLOAK_CONFIG['BASE_URL']}/realms/{settings.KEYCLOAK_CONFIG['REALM']}/.well-known/openid-configuration"
        
        try:
            response = requests.get(config_url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erreur récupération config OIDC: {e}")
        
        return None
    
    @staticmethod
    def get_auth_url(redirect_uri, state):
        """Génère l'URL d'authentification Keycloak"""
        config = KeycloakService.get_oidc_config()
        if not config:
            return None
        
        params = {
            'client_id': settings.KEYCLOAK_CONFIG['CLIENT_ID'],
            'response_type': 'code',
            'scope': 'openid profile email',
            'redirect_uri': redirect_uri,
            'state': state,
        }
        
        auth_url = config.get('authorization_endpoint', '')
        if auth_url:
            from urllib.parse import urlencode
            return f"{auth_url}?{urlencode(params)}"
        
        return None
    
    @staticmethod
    def exchange_code_for_token(code, redirect_uri):
        """Échange un code d'autorisation contre un token"""
        config = KeycloakService.get_oidc_config()
        if not config:
            return None
        
        token_url = config.get('token_endpoint', '')
        if not token_url:
            return None
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.KEYCLOAK_CONFIG['CLIENT_ID'],
            'client_secret': settings.KEYCLOAK_CONFIG.get('CLIENT_SECRET', ''),
            'code': code,
            'redirect_uri': redirect_uri,
        }
        
        try:
            response = requests.post(token_url, data=data, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erreur échange token: {e}")
        
        return None
    
    @staticmethod
    def get_user_info(access_token):
        """Récupère les informations utilisateur depuis Keycloak"""
        config = KeycloakService.get_oidc_config()
        if not config:
            return None
        
        userinfo_url = config.get('userinfo_endpoint', '')
        if not userinfo_url:
            return None
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(userinfo_url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erreur récupération userinfo: {e}")
        
        return None
    
    @staticmethod
    def create_or_update_user(keycloak_user):
        """Crée ou met à jour un utilisateur Django"""
        username = keycloak_user.get('preferred_username') or keycloak_user.get('sub')
        email = keycloak_user.get('email')
        
        if not username or not email:
            return None
        
        # Chercher l'utilisateur par email
        try:
            user = User.objects.get(email=email)
            # Mettre à jour si nécessaire
            user.username = username
            user.first_name = keycloak_user.get('given_name', '')
            user.last_name = keycloak_user.get('family_name', '')
            user.save()
            return user, False  # False = pas créé
        except User.DoesNotExist:
            # Créer un nouvel utilisateur
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=keycloak_user.get('given_name', ''),
                last_name=keycloak_user.get('family_name', ''),
                password=None  # Pas de mot de passe local
            )
            return user, True  # True = créé
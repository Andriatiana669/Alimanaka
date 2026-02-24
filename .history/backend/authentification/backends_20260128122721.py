from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .services import KeycloakService

User = get_user_model()

class KeycloakBackend(BaseBackend):
    """Backend d'authentification Keycloak"""
    
    def authenticate(self, request, access_token=None, **kwargs):
        """Authentifie un utilisateur via Keycloak"""
        if not access_token:
            return None
        
        # Récupérer les infos utilisateur depuis Keycloak
        user_info = KeycloakService.get_user_info(access_token)
        if not user_info:
            return None
        
        # Créer ou mettre à jour l'utilisateur
        result = KeycloakService.create_or_update_user(user_info)
        if result:
            user, created = result
            return user
        
        return None
    
    def get_user(self, user_id):
        """Récupère un utilisateur par son ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
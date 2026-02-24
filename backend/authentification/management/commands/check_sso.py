from django.core.management.base import BaseCommand
from authentification.keycloak_service import KeycloakService

class Command(BaseCommand):
    help = 'Vérifie la connexion au serveur Keycloak'
    
    def handle(self, *args, **options):
        try:
            jwks = KeycloakService.get_jwks()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Connexion Keycloak réussie!')
            )
            self.stdout.write(f'Clés disponibles: {len(jwks.get("keys", []))}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur connexion Keycloak: {e}')
            )
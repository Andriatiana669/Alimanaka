# backend/users/management/commands/ajouter_solde_mensuel.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User

class Command(BaseCommand):
    help = 'Ajoute le solde mensuel de congés à tous les utilisateurs actifs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(
            f'Début de l\'ajout du solde mensuel - {timezone.now()}'
        ))
        
        users = User.objects.filter(is_active=True)
        total = 0
        
        for user in users:
            ancien_solde = user.solde_conge_actuelle
            user.ajouter_solde_mensuel()
            total += 1
            
            self.stdout.write(
                f'  {user.username}: {ancien_solde} → {user.solde_conge_actuelle} '
                f'(+{user.solde_conge_recue_par_mois})'
            )
        
        self.stdout.write(self.style.SUCCESS(
            f'\n{total} utilisateurs mis à jour avec succès !'
        ))
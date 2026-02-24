# backend/users/middleware.py
from django.utils import timezone
from datetime import timedelta
from .models import CronJobLog
from django.core.management import call_command

class MonthlySoldeMiddleware:
    """Vérifie et exécute l'ajout mensuel du solde si nécessaire"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        self.check_and_run_monthly_job()
        response = self.get_response(request)
        return response
    
    def check_and_run_monthly_job(self):
        """Vérifie si le job mensuel doit être exécuté"""
        job_name = 'ajouter_solde_mensuel'
        today = timezone.now()
        
        # Cherche le dernier log
        try:
            log = CronJobLog.objects.get(job_name=job_name)
            last_run = log.last_run
            
            # Vérifie si on est le 1er du mois et si pas déjà exécuté ce mois-ci
            if today.day == 1:
                if last_run.month != today.month or last_run.year != today.year:
                    self.run_job(log)
        except CronJobLog.DoesNotExist:
            # Premier run - exécute si on est le 1er du mois
            if today.day == 1:
                log = CronJobLog(job_name=job_name, last_run=today)
                self.run_job(log)
    
    def run_job(self, log):
        """Exécute la commande et loggue"""
        from io import StringIO
        import sys
        
        try:
            out = StringIO()
            sys.stdout = out
            call_command('ajouter_solde_mensuel')
            sys.stdout = sys.__stdout__
            
            log.last_run = timezone.now()
            log.success = True
            log.message = out.getvalue()
            log.save()
            
            print(f"[CRON] Solde mensuel ajouté avec succès - {log.last_run}")
        except Exception as e:
            log.last_run = timezone.now()
            log.success = False
            log.message = str(e)
            log.save()
            print(f"[CRON] Erreur ajout solde mensuel: {e}")


# Alternative plus simple : Vue API qui déclenche le job
# backend/users/views.py - Ajoute cette vue

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from django.core.management import call_command

@api_view(['POST'])
@permission_classes([IsAdminUser])
def trigger_monthly_solde(request):
    """Déclenche manuellement l'ajout du solde mensuel (admin uniquement)"""
    try:
        call_command('ajouter_solde_mensuel')
        return Response({'success': True, 'message': 'Solde mensuel ajouté'})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
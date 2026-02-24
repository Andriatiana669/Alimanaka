# backend/users/middleware.py

from django.utils import timezone
from django.apps import apps
from django.core.management import call_command
from io import StringIO
import sys


class MonthlySoldeMiddleware:
    """Vérifie et exécute l'ajout mensuel du solde si nécessaire (1 → 10)"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.check_and_run_monthly_job()
        return self.get_response(request)

    def check_and_run_monthly_job(self):
        job_name = "ajouter_solde_mensuel"
        today = timezone.now()

        # 👉 fenêtre autorisée : du 1 au 10 inclus
        if not (1 <= today.day <= 10):
            return

        # Récupération lazy du modèle (IMPORTANT)
        CronJobLog = apps.get_model("users", "CronJobLog")

        log, created = CronJobLog.objects.get_or_create(
            job_name=job_name,
            defaults={
                "last_run": today,
                "success": False,
                "message": "Initialisation"
            }
        )

        # 👉 Déjà exécuté ce mois-ci → on stop
        if (
            not created
            and log.last_run.month == today.month
            and log.last_run.year == today.year
        ):
            return

        self.run_job(log)

    def run_job(self, log):
        try:
            out = StringIO()
            sys.stdout = out

            call_command("ajouter_solde_mensuel")

            sys.stdout = sys.__stdout__

            log.last_run = timezone.now()
            log.success = True
            log.message = out.getvalue()
            log.save()

            print(f"[CRON] Solde mensuel ajouté avec succès - {log.last_run}")

        except Exception as e:
            sys.stdout = sys.__stdout__

            log.last_run = timezone.now()
            log.success = False
            log.message = str(e)
            log.save()

            print(f"[CRON] Erreur ajout solde mensuel : {e}")

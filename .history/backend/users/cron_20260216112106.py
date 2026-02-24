from django.utils import timezone
from django.apps import apps
from django.core.management import call_command


def monthly_solde_job():
    """
    Job CRON :
    - exécutable du 1 au 10
    - une seule fois par mois
    """

    today = timezone.now()

    # Fenêtre autorisée
    if not (1 <= today.day <= 10):
        return

    CronJobLog = apps.get_model("users", "CronJobLog")
    job_name = "ajouter_solde_mensuel"

    log, created = CronJobLog.objects.get_or_create(
        job_name=job_name,
        defaults={
            "last_run": today,
            "success": False,
            "message": "Initialisation CRON"
        }
    )

    # Déjà exécuté ce mois-ci
    if (
        not created
        and log.last_run.month == today.month
        and log.last_run.year == today.year
    ):
        return

    try:
        call_command("ajouter_solde_mensuel")

        log.last_run = timezone.now()
        log.success = True
        log.message = "Solde mensuel ajouté avec succès"
        log.save()

        print(f"[CRON] Solde mensuel ajouté ({log.last_run})")

    except Exception as e:
        log.last_run = timezone.now()
        log.success = False
        log.message = str(e)
        log.save()

        print(f"[CRON] ERREUR solde mensuel : {e}")

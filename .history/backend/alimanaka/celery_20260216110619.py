# backend/alimanaka/celery.py

from celery import Celery
from celery.schedules import crontab

app = Celery('alimanaka')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'ajouter-solde-mensuel': {
        'task': 'users.tasks.ajouter_solde_mensuel_task',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),
    },
}

app.autodiscover_tasks()
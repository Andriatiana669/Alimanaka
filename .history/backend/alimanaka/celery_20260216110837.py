# backend/alimanaka/celery.py

import os
from celery import Celery
from celery.schedules import crontab

# Définit le settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alimanaka.settings')

app = Celery('alimanaka')

# Charge la config depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Planification des tâches
app.conf.beat_schedule = {
    'ajouter-solde-mensuel': {
        'task': 'users.tasks.ajouter_solde_mensuel_task',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),
    },
}

# Auto-découverte des tâches dans les apps Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
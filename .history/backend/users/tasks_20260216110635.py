# backend/users/tasks.py

from celery import shared_task
from django.core.management import call_command

@shared_task
def ajouter_solde_mensuel_task():
    """Tâche Celery pour ajouter le solde mensuel"""
    call_command('ajouter_solde_mensuel')
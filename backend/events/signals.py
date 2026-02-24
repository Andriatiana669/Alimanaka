from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from conges.models import Conge, JourFerie, JourExceptionnel
from retards.models import Retard
from permissions.models import Permission
from reposmedicale.models import ReposMedical
from ostie.models import Ostie

from .services import EventSyncService
from .models import Event


# Congés
@receiver(post_save, sender=Conge)
def sync_conge_on_save(sender, instance, **kwargs):
    EventSyncService.sync_conge(instance)


@receiver(post_delete, sender=Conge)
def delete_conge_event(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    Event.objects.filter(content_type=content_type, object_id=instance.id).delete()


# Retards
@receiver(post_save, sender=Retard)
def sync_retard_on_save(sender, instance, **kwargs):
    EventSyncService.sync_retard(instance)


@receiver(post_delete, sender=Retard)
def delete_retard_event(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    Event.objects.filter(content_type=content_type, object_id=instance.id).delete()


# Permissions
@receiver(post_save, sender=Permission)
def sync_permission_on_save(sender, instance, **kwargs):
    EventSyncService.sync_permission(instance)


@receiver(post_delete, sender=Permission)
def delete_permission_event(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    Event.objects.filter(content_type=content_type, object_id=instance.id).delete()


# Repos médicaux
@receiver(post_save, sender=ReposMedical)
def sync_repos_on_save(sender, instance, **kwargs):
    EventSyncService.sync_repos_medical(instance)


@receiver(post_delete, sender=ReposMedical)
def delete_repos_event(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    Event.objects.filter(content_type=content_type, object_id=instance.id).delete()


# OSTIES
@receiver(post_save, sender=Ostie)
def sync_ostie_on_save(sender, instance, **kwargs):
    EventSyncService.sync_ostie(instance)


@receiver(post_delete, sender=Ostie)
def delete_ostie_event(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)
    Event.objects.filter(content_type=content_type, object_id=instance.id).delete()


# Jours fériés et exceptionnels
@receiver(post_save, sender=JourFerie)
def sync_jour_ferie(sender, instance, **kwargs):
    # Logique pour créer l'événement
    pass


@receiver(post_save, sender=JourExceptionnel)
def sync_jour_exceptionnel(sender, instance, **kwargs):
    # Logique pour créer l'événement
    pass
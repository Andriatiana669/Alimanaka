from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
from .models import Event


class EventSyncService:
    """Service pour synchroniser les événements depuis les autres applications"""
    
    @classmethod
    def sync_conge(cls, conge):
        """Synchronise un congé"""
        content_type = ContentType.objects.get(app_label='conges', model='conge')
        event, created = Event.objects.update_or_create(
            content_type=content_type,
            object_id=conge.id,
            defaults={
                'title': f"Congé - {conge.utilisateur.get_display_name()}",
                'event_type': 'conge',
                'start_date': conge.date_debut,
                'end_date': conge.date_fin,
                'all_day': True,
                'color': cls._get_conge_color(conge),
                'user': conge.utilisateur,
                'statut': conge.statut,
                'is_system': False,
                'is_blocked': False,
            }
        )
        return event
    
    @classmethod
    def sync_retard(cls, retard):
        """Synchronise un retard"""
        content_type = ContentType.objects.get(app_label='retards', model='retard')
        event, created = Event.objects.update_or_create(
            content_type=content_type,
            object_id=retard.id,
            defaults={
                'title': f"Retard - {retard.utilisateur.get_display_name()}",
                'description': retard.motif_retard,
                'event_type': 'retard',
                'start_date': retard.date,
                'all_day': True,
                'color': '#f39c12',
                'user': retard.utilisateur,
                'statut': retard.statut,
                'is_system': False,
                'is_blocked': False,
            }
        )
        return event
    
    @classmethod
    def sync_permission(cls, permission):
        """Synchronise une permission"""
        content_type = ContentType.objects.get(app_label='permissions', model='permission')
        event, created = Event.objects.update_or_create(
            content_type=content_type,
            object_id=permission.id,
            defaults={
                'title': f"Permission - {permission.utilisateur.get_display_name()}",
                'event_type': 'permission',
                'start_date': permission.date,
                'all_day': True,
                'color': '#27ae60',
                'user': permission.utilisateur,
                'statut': permission.statut,
                'is_system': False,
                'is_blocked': False,
            }
        )
        return event
    
    @classmethod
    def sync_repos_medical(cls, repos):
        """Synchronise un repos médical"""
        content_type = ContentType.objects.get(app_label='reposmedicale', model='reposmedical')
        event, created = Event.objects.update_or_create(
            content_type=content_type,
            object_id=repos.id,
            defaults={
                'title': f"Repos médical - {repos.utilisateur.get_display_name()}",
                'event_type': 'repos_medical',
                'start_date': repos.date,
                'all_day': True,
                'color': '#e74c3c',
                'user': repos.utilisateur,
                'statut': repos.statut,
                'is_system': False,
                'is_blocked': False,
            }
        )
        return event
    
    @classmethod
    def sync_ostie(cls, ostie):
        """Synchronise un OSTIE"""
        content_type = ContentType.objects.get(app_label='ostie', model='ostie')
        event, created = Event.objects.update_or_create(
            content_type=content_type,
            object_id=ostie.id,
            defaults={
                'title': f"OSTIE - {ostie.utilisateur.get_display_name()}",
                'event_type': 'ostie',
                'start_date': ostie.date,
                'all_day': True,
                'color': '#9b59b6',
                'user': ostie.utilisateur,
                'statut': ostie.statut,
                'is_system': False,
                'is_blocked': False,
            }
        )
        return event
    
    @classmethod
    def create_jour_ferie(cls, nom, mois, jour, annee):
        """Crée un jour férié"""
        from conges.models import JourFerie
        
        try:
            date_jf = datetime(annee, mois, jour).date()
        except ValueError:
            return None
            
        content_type = ContentType.objects.get(app_label='conges', model='jourferie')
        event, created = Event.objects.update_or_create(
            content_type=content_type,
            object_id=f"{annee}_{mois}_{jour}",  # ID unique
            defaults={
                'title': f"🎉 {nom}",
                'event_type': 'ferie',
                'start_date': date_jf,
                'all_day': True,
                'color': '#ffeb3b',
                'is_system': True,
                'is_blocked': True,
            }
        )
        return event
    
    @classmethod
    def create_jour_exceptionnel(cls, date, description, type_jour):
        """Crée un jour exceptionnel"""
        from conges.models import JourExceptionnel
        
        content_type = ContentType.objects.get(app_label='conges', model='jourexceptionnel')
        event, created = Event.objects.update_or_create(
            content_type=content_type,
            object_id=f"exc_{date.isoformat()}",
            defaults={
                'title': f"⛔ {description or 'Exceptionnel'}",
                'description': description,
                'event_type': 'exceptionnel',
                'start_date': date,
                'all_day': True,
                'color': '#ff5722' if type_jour == 'exceptionnel' else '#4caf50',
                'is_system': True,
                'is_blocked': type_jour == 'exceptionnel',
            }
        )
        return event
    
    @classmethod
    def generate_weekends(cls, annee):
        """Génère tous les weekends d'une année"""
        from datetime import date, timedelta
        
        current = date(annee, 1, 1)
        while current.year == annee:
            if current.weekday() >= 5:  # Samedi ou Dimanche
                content_type = ContentType.objects.get(app_label='events', model='event')
                Event.objects.update_or_create(
                    content_type=content_type,
                    object_id=f"weekend_{current.isoformat()}",
                    defaults={
                        'title': "📅 Weekend",
                        'event_type': 'weekend',
                        'start_date': current,
                        'all_day': True,
                        'color': '#e0e0e0',
                        'is_system': True,
                        'is_blocked': True,
                    }
                )
            current += timedelta(days=1)
    
    @classmethod
    def _get_conge_color(cls, conge):
        """Détermine la couleur d'un congé selon son type"""
        colors = {
            'matin': '#ff9800',
            'midi': '#4caf50',
            'journee': '#2196f3'
        }
        return colors.get(conge.type_conge, '#9e9e9e')
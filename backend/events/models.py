from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from users.models import User


class Event(models.Model):
    """Modèle unifié pour tous les événements du calendrier"""
    
    EVENT_TYPES = [
        ('conge', 'Congé'),
        ('retard', 'Retard'),
        ('permission', 'Permission'),
        ('repos_medical', 'Repos médical'),
        ('ostie', 'OSTIE'),
        ('ferie', 'Jour férié'),
        ('exceptionnel', 'Jour exceptionnel'),
        ('weekend', 'Weekend'),
        ('system', 'Système'),
    ]
    
    # Relations génériques pour lier à n'importe quel modèle
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Métadonnées de l'événement
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, db_index=True)
    
    # Dates
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    all_day = models.BooleanField(default=True)
    
    # Apparence
    color = models.CharField(max_length=20, blank=True, help_text="Code couleur hexadécimal")
    icon = models.CharField(max_length=50, blank=True)
    
    # Comportement
    is_blocked = models.BooleanField(default=False, help_text="Jour bloqué (pas de congés)")
    is_system = models.BooleanField(default=False, help_text="Événement système")
    
    # Utilisateur concerné (pour les événements utilisateur)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='calendar_events'
    )
    
    # Statut (pour les événements utilisateur)
    statut = models.CharField(max_length=20, blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['-start_date', 'start_time']
        indexes = [
            models.Index(fields=['event_type', 'start_date']),
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['is_system']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_date}"
    
    def to_calendar_dict(self):
        """Convertit l'événement au format pour le calendrier frontend"""
        return {
            'id': f"event_{self.id}",
            'title': self.title,
            'start': self.start_date.isoformat(),
            'end': self.end_date.isoformat() if self.end_date else None,
            'allDay': self.all_day,
            'color': self.color,
            'type': self.event_type,
            'user_id': self.user.id if self.user else None,
            'user_display_name': self.user.get_display_name() if self.user else None,
            'statut': self.statut if self.statut else None,
            'isBlocked': self.is_blocked,
            'isSystem': self.is_system,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
        }
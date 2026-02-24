from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from users.models import User
from reposmedicale.models import ReposMedical


class Ostie(models.Model):
    """OSTIE (type d'absence spécifique)"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('transforme', 'Transformé en Repos Médical'),
        ('annule', 'Annulé'),
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='osties',
        verbose_name="Utilisateur"
    )
    
    date = models.DateField(verbose_name="Date de l'OSTIE")
    
    # Heure de début
    heure_debut = models.TimeField(verbose_name="Heure de début")
    
    # Heure de fin (saisie lors de la validation/transformation)
    heure_fin = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure de fin"
    )
    
    motif = models.TextField(
        verbose_name="Motif",
        blank=True,
        default=""
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut",
        db_index=True
    )
    
    # Lien vers le repos médical si transformé
    repos_genere = models.ForeignKey(
        ReposMedical,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ostie_origine',
        verbose_name="Repos médical généré"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Validation par manager
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='osties_validees',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Annulation
    annule_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='osties_annulees',
        verbose_name="Annulé par"
    )
    date_annulation = models.DateTimeField(null=True, blank=True)
    commentaire_annulation = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "OSTIE"
        verbose_name_plural = "OSTIES"
        ordering = ['-date', '-date_creation']
        indexes = [
            models.Index(fields=['utilisateur', 'date']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.get_display_name()} - {self.date} ({self.heure_debut})"
    
    def valider(self, heure_fin, user=None):
        """Valider directement l'OSTIE"""
        self.statut = 'approuve'
        self.heure_fin = heure_fin
        self.valide_par = user
        self.date_validation = datetime.now()
        self.save()
    
    def transformer_en_repos_medical(self, heure_fin_ostie, heure_fin_repos, user=None):
        """Transformer l'OSTIE en repos médical"""
        from reposmedicale.models import ReposMedical
        
        # Mettre à jour l'OSTIE
        self.statut = 'transforme'
        self.heure_fin = heure_fin_ostie
        self.valide_par = user
        self.date_validation = datetime.now()
        
        # Créer le repos médical
        repos = ReposMedical.objects.create(
            utilisateur=self.utilisateur,
            date=self.date,
            heure_debut=heure_fin_ostie,  # L'heure de fin de l'OSTIE devient heure de début du repos
            heure_fin=heure_fin_repos,
            motif=f"[TRANSFORMÉ DEPUIS OSTIE] {self.motif}",
            avertissement="Transformé automatiquement depuis OSTIE",
            statut='en_attente'
        )
        
        # Lier le repos médical à l'OSTIE
        self.repos_genere = repos
        self.save()
        
        return repos
    
    def annuler(self, user=None, commentaire=""):
        """Annuler l'OSTIE"""
        self.statut = 'annule'
        self.annule_par = user
        self.date_annulation = datetime.now()
        self.commentaire_annulation = commentaire
        self.save()
    
    def to_calendar_event(self):
        """Pour l'affichage dans le calendrier"""
        couleur = '#ff9800'  # Orange par défaut (en_attente)
        if self.statut == 'approuve':
            couleur = '#4caf50'  # Vert
        elif self.statut == 'transforme':
            couleur = '#9c27b0'  # Violet
        elif self.statut == 'annule':
            couleur = '#9e9e9e'  # Gris
        
        title = f"⚡ {self.utilisateur.username.upper()} - Début {self.heure_debut}"
        if self.heure_fin:
            title += f" → Fin {self.heure_fin}"
        if self.statut == 'transforme' and self.repos_genere:
            title += f" → Repos #{self.repos_genere.id}"
        
        return {
            'id': f"ostie_{self.id}",
            'title': title,
            'start': self.date.isoformat(),
            'allDay': True,
            'color': couleur,
            'type': 'ostie',
            'user_id': self.utilisateur.id,
            'statut': self.statut,
            'heure_debut': str(self.heure_debut),
            'heure_fin': str(self.heure_fin) if self.heure_fin else None,
            'repos_genere_id': self.repos_genere.id if self.repos_genere else None
        }


class OstieConfig(models.Model):
    """Configuration des OSTIES"""
    
    # Peut-être des règles spécifiques plus tard
    class Meta:
        verbose_name = "Configuration des OSTIES"
        verbose_name_plural = "Configurations des OSTIES"
    
    def __str__(self):
        return "Configuration des OSTIES"
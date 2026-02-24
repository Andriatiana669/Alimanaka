from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from users.models import User
from conges.models import TypeCongeConfig, Conge


class ReposMedical(models.Model):
    """Repos médical (maladie, consultation, etc.)"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),      # Créé, en attente de validation
        ('approuve', 'Approuvé'),           # Validé directement
        ('transforme', 'Transformé en congé'), # Transformé en congé
        ('annule', 'Annulé'),
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='repos_medicaux',
        verbose_name="Utilisateur"
    )
    
    date = models.DateField(verbose_name="Date du repos")
    
    # Heures
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    
    # Calculs
    duree_heures = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        verbose_name="Durée en heures"
    )
    
    motif = models.TextField(
        verbose_name="Motif",
        default="Malade",
        blank=True
    )
    
    avertissement = models.TextField(
        verbose_name="Avertissement",
        default="N'oublie pas d'apporter ton justificatif médical (PJ)",
        help_text="Message affiché à l'utilisateur"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut",
        db_index=True
    )
    
    # Lien vers le congé si transformé
    conge_genere = models.ForeignKey(
        Conge,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repos_medical_origine',
        verbose_name="Congé généré"
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
        related_name='repos_medicaux_valides',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Annulation
    annule_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='repos_medicaux_annules',
        verbose_name="Annulé par"
    )
    date_annulation = models.DateTimeField(null=True, blank=True)
    commentaire_annulation = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Repos médical"
        verbose_name_plural = "Repos médicaux"
        ordering = ['-date', '-date_creation']
        indexes = [
            models.Index(fields=['utilisateur', 'date']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.get_display_name()} - {self.date} ({self.heure_debut}-{self.heure_fin})"
    
    def save(self, *args, **kwargs):
        # Calcul automatique de la durée
        from datetime import datetime, timedelta
        debut_dt = datetime.combine(self.date, self.heure_debut)
        fin_dt = datetime.combine(self.date, self.heure_fin)
        diff = fin_dt - debut_dt
        heures = Decimal(str(diff.total_seconds())) / Decimal('3600')
        self.duree_heures = heures.quantize(Decimal('0.01'))
        
        super().save(*args, **kwargs)
    
    def valider(self, user=None):
        """Valider directement le repos médical"""
        self.statut = 'approuve'
        self.valide_par = user
        self.date_validation = datetime.now()
        self.save()
    
    def transformer_en_conge(self, type_conge, user=None):
        """Transformer le repos médical en congé"""
        from conges.models import Conge
        
        # Créer le congé
        conge = Conge.objects.create(
            utilisateur=self.utilisateur,
            type_conge=type_conge,
            date_debut=self.date,
            date_fin=self.date,
            motif=f"[REPOS MEDICAL] {self.motif}",
            statut='en_attente'  # Sera validé par le manager dans Conges.vue
        )
        
        # Calculer la déduction (selon les règles des congés)
        conge.calculer_deduction()
        conge.save()
        
        # Lier le repos médical au congé
        self.conge_genere = conge
        self.statut = 'transforme'
        self.valide_par = user
        self.date_validation = datetime.now()
        self.save()
        
        return conge
    
    def annuler(self, user=None, commentaire=""):
        """Annuler le repos médical"""
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
        
        title = f"🏥 {self.utilisateur.username.upper()} - {self.heure_debut}→{self.heure_fin} ({self.duree_heures}h)"
        if self.statut == 'transforme' and self.conge_genere:
            title += f" → Congé #{self.conge_genere.id}"
        
        return {
            'id': f"repos_{self.id}",
            'title': title,
            'start': self.date.isoformat(),
            'allDay': True,
            'color': couleur,
            'type': 'repos_medical',
            'user_id': self.utilisateur.id,
            'statut': self.statut,
            'duree_heures': float(self.duree_heures),
            'conge_genere_id': self.conge_genere.id if self.conge_genere else None
        }


class ReposMedicalConfig(models.Model):
    """Configuration des repos médicaux"""
    
    jours_max_par_an = models.PositiveIntegerField(
        default=30,
        verbose_name="Jours max par an",
        help_text="Nombre maximum de jours de repos médical par an"
    )
    
    class Meta:
        verbose_name = "Configuration des repos médicaux"
        verbose_name_plural = "Configurations des repos médicaux"
    
    def __str__(self):
        return "Configuration des repos médicaux"
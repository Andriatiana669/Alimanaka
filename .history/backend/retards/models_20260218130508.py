from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date, timedelta
from users.models import User


class TypeRetardConfig(models.Model):
    """Configuration des types de retards avec seuils et multiplicateurs"""
    
    nom_personnalise = models.CharField(
        max_length=50,
        verbose_name="Nom personnalisé",
        help_text="Nom affiché dans l'interface"
    )
    
    type_retard = models.CharField(
        max_length=20,
        choices=[
            ('Matin', 'Matin'),
            ('Midi', 'Midi'), 
            ('Autres', 'Autres')
        ],
        default='Matin',
        verbose_name="Type (pour le calcul)"
    )
    
    # Heure de début prévue par défaut (configurable)
    heure_debut_prevue = models.TimeField(
        default='08:00',
        verbose_name="Heure de début prévue",
        help_text="Heure à laquelle l'utilisateur est censé commencer"
    )
    
    # Seuils en minutes
    minutes_min = models.PositiveIntegerField(
        verbose_name="Minutes minimum",
        help_text="Seuil minimum inclus"
    )
    minutes_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Minutes maximum",
        help_text="Seuil maximum inclus (null = illimité)"
    )
    
    # Multiplicateur pour calcul du temps à rattraper
    multiplicateur = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name="Multiplicateur de rattrapage"
    )
    
    # Couleur pour le calendrier
    couleur = models.CharField(
        max_length=7,
        default='#ff9800',
        verbose_name="Couleur dans le calendrier"
    )
    
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    class Meta:
        verbose_name = "Configuration type de retard"
        verbose_name_plural = "Configurations types de retard"
        ordering = ['minutes_min', 'ordre']
    
    def __str__(self):
        return self.nom_personnalise
    def clean(self):
        if self.minutes_max and self.minutes_min >= self.minutes_max:
            raise ValidationError({
                'minutes_max': 'Le maximum doit être supérieur au minimum'
            })
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        
        
        
class Retard(models.Model):
    """Déclaration de retard d'un utilisateur"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente de rattrapage'),
        ('en_cours', 'Rattrapage en cours'),
        ('approuve', 'Rattrapé / Approuvé'),
        ('annule', 'Annulé'),
        ('remplace', 'Remplacé'),
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='retards',
        verbose_name="Utilisateur"
    )
    
    date = models.DateField(verbose_name="Date du retard")
    
    # Heures réelles (maintenant on stocke la config utilisée)
    type_retard_config = models.ForeignKey(
        TypeRetardConfig,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Configuration utilisée"
    )
    heure_debut_prevue = models.TimeField(
        verbose_name="Heure de début prévue"
    )
    heure_arrivee_reelle = models.TimeField(
        verbose_name="Heure d'arrivée réelle"
    )
    
    # Calculs automatiques
    minutes_retard = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutes de retard",
        editable=False
    )
    heures_a_rattraper = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Heures à rattraper",
        editable=False
    )
    heures_restantes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Heures restantes à rattraper"
    )
    
    # Type calculé
    type_retard = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Type de retard calculé",
        editable=False
    )
    
    motif_retard = models.TextField(
        blank=True,
        null=True,
        verbose_name="Justificatif / Motif du retard"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut",
        db_index=True
    )
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    approuve_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='retards_approuves',
        verbose_name="Approuvé par"
    )
    date_approbation = models.DateTimeField(null=True, blank=True, verbose_name="Date d'approbation")
    
    annule_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='retards_annules',
        verbose_name="Annulé par"
    )
    date_annulation = models.DateTimeField(null=True, blank=True, verbose_name="Date d'annulation")
    commentaire_annulation = models.TextField(blank=True, null=True, verbose_name="Commentaire d'annulation")
    
    retard_original = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='retards_fractionnes',
        verbose_name="Retard original"
    )
    
    class Meta:
        verbose_name = "Retard"
        verbose_name_plural = "Retards"
        ordering = ['-date', '-date_creation']
        indexes = [
            models.Index(fields=['utilisateur', 'date']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.get_display_name()} - {self.date} ({self.minutes_retard}min)"
    
    def clean(self):
        if self.heure_arrivee_reelle <= self.heure_debut_prevue:
            raise ValidationError({
                'heure_arrivee_reelle': "L'heure d'arrivée doit être après l'heure de début prévue"
            })
        
        if self.date > date.today():
            raise ValidationError({
                'date': "La date du retard ne peut pas être dans le futur"
            })
    
    def save(self, *args, **kwargs):
        if not self.pk or self._state.adding:
            self.calculer_retard()
        super().save(*args, **kwargs)
    
    def calculer_retard(self):
        from datetime import datetime
        
        debut = datetime.combine(self.date, self.heure_debut_prevue)
        arrivee = datetime.combine(self.date, self.heure_arrivee_reelle)
        
        diff = arrivee - debut
        self.minutes_retard = max(0, int(diff.total_seconds() / 60))
        
        if self.type_retard_config:
            self.type_retard = self.type_retard_config.type_retard
            heures_brutes = Decimal(self.minutes_retard) / Decimal('60')
            self.heures_a_rattraper = (heures_brutes * self.type_retard_config.multiplicateur).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            self.type_retard = 'Matin'
            self.heures_a_rattraper = (Decimal(self.minutes_retard) / Decimal('60')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        if self._state.adding:
            self.heures_restantes = self.heures_a_rattraper
        
        return self.minutes_retard, self.heures_a_rattraper
    
    def rattraper_heures(self, heures_rattrapees, user=None):
        self.heures_restantes = max(Decimal('0'), self.heures_restantes - Decimal(str(heures_rattrapees)))
        self.heures_restantes = self.heures_restantes.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if self.heures_restantes <= 0:
            self.statut = 'approuve'
            self.approuve_par = user
            from django.utils import timezone
            self.date_approbation = timezone.now()
        else:
            self.statut = 'en_cours'
        
        self.save()
        return self.heures_restantes
    
    def to_calendar_event(self):
        return {
            'id': f"retard_{self.id}",
            'title': f"⏰ {self.utilisateur.username.upper()} - {self.minutes_retard}min ({self.heures_restantes}h restantes)",
            'start': self.date.isoformat(),
            'allDay': True,
            'color': self.type_retard_config.couleur if self.type_retard_config else '#ff9800',
            'type': 'retard',
            'user_id': self.utilisateur.id,
            'statut': self.statut,
            'minutes_retard': self.minutes_retard,
            'heures_restantes': float(self.heures_restantes)
        }
        
        
class Rattrapage(models.Model):
    """Session de rattrapage d'heures pour un retard"""
    
    retard = models.ForeignKey(
        Retard,
        on_delete=models.CASCADE,
        related_name='rattrapages',
        verbose_name="Retard concerné"
    )
    
    date_rattrapage = models.DateField(verbose_name="Date du rattrapage")
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    
    heures_rattrapees = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Heures rattrapées",
        editable=False
    )
    
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rattrapages_valides',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(auto_now_add=True, verbose_name="Date de validation")
    
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire")
    
    class Meta:
        verbose_name = "Rattrapage"
        verbose_name_plural = "Rattrapages"
        ordering = ['-date_rattrapage']
    
    def __str__(self):
        return f"Rattrapage {self.retard.utilisateur} - {self.date_rattrapage} ({self.heures_rattrapees}h)"
    
    def clean(self):
        if self.heure_fin <= self.heure_debut:
            raise ValidationError("L'heure de fin doit être après l'heure de début")
        
        if self.date_rattrapage > date.today():
            raise ValidationError("La date de rattrapage ne peut pas être dans le futur")
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.calculer_heures()
        super().save(*args, **kwargs)
        
        self.retard.rattraper_heures(self.heures_rattrapees, self.valide_par)
    
    def calculer_heures(self):
        from datetime import datetime
        
        debut = datetime.combine(self.date_rattrapage, self.heure_debut)
        fin = datetime.combine(self.date_rattrapage, self.heure_fin)
        
        diff = fin - debut
        heures = Decimal(str(diff.total_seconds())) / Decimal('3600')
        self.heures_rattrapees = heures.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.heures_rattrapees
    """Session de rattrapage d'heures pour un retard"""
    
    retard = models.ForeignKey(
        Retard,
        on_delete=models.CASCADE,
        related_name='rattrapages',
        verbose_name="Retard concerné"
    )
    
    date_rattrapage = models.DateField(verbose_name="Date du rattrapage")
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    
    heures_rattrapees = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Heures rattrapées",
        editable=False
    )
    
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rattrapages_valides',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(auto_now_add=True, verbose_name="Date de validation")
    
    commentaire = models.TextField(blank=True, null=True, verbose_name="Commentaire")
    
    class Meta:
        verbose_name = "Rattrapage"
        verbose_name_plural = "Rattrapages"
        ordering = ['-date_rattrapage']
    
    def __str__(self):
        return f"Rattrapage {self.retard.utilisateur} - {self.date_rattrapage} ({self.heures_rattrapees}h)"
    
    def clean(self):
        """Validation des heures"""
        if self.heure_fin <= self.heure_debut:
            raise ValidationError("L'heure de fin doit être après l'heure de début")
        
        # Vérifier que la date n'est pas dans le futur
        if self.date_rattrapage > date.today():
            raise ValidationError("La date de rattrapage ne peut pas être dans le futur")
    
    def save(self, *args, **kwargs):
        """Calcul automatique des heures et mise à jour du retard"""
        if not self.pk:
            self.calculer_heures()
        super().save(*args, **kwargs)
        
        # Mettre à jour les heures restantes du retard
        self.retard.rattraper_heures(self.heures_rattrapees, self.valide_par)
    
    def calculer_heures(self):
        """Calcule les heures entre début et fin"""
        from datetime import datetime
        
        debut = datetime.combine(self.date_rattrapage, self.heure_debut)
        fin = datetime.combine(self.date_rattrapage, self.heure_fin)
        
        diff = fin - debut
        heures = Decimal(str(diff.total_seconds())) / Decimal('3600')
        self.heures_rattrapees = heures.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.heures_rattrapees
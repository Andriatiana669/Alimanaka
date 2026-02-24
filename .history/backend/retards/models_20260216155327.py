from django.db import models

# Create your models here.
from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from users.models import User


class TypeRetardConfig(models.Model):
    """Configuration des types de retards"""
    
    TYPE_CHOICES = [
        ('leger', 'Retard léger (< 30min)'),
        ('moyen', 'Retard moyen (30min - 1h)'),
        ('important', 'Retard important (> 1h)'),
    ]
    
    type_retard = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        unique=True,
        verbose_name="Type de retard"
    )
    
    # Seuils en minutes
    minutes_min = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutes minimum"
    )
    minutes_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Minutes maximum (null = illimité)"
    )
    
    # Multiplicateur pour calcul du temps à rattraper
    # Ex: 1.0 = rattraper exactement le temps perdu, 1.5 = pénalité de 50%
    multiplicateur = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('1.00'),
        verbose_name="Multiplicateur de rattrapage"
    )
    
    class Meta:
        verbose_name = "Configuration type de retard"
        verbose_name_plural = "Configurations types de retard"
    
    def __str__(self):
        return f"{self.get_type_retard_display()}"


class Retard(models.Model):
    """Demande de déclaration de retard"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('annule', 'Annulé'),
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='retards',
        verbose_name="Utilisateur"
    )
    
    date = models.DateField(verbose_name="Date du retard")
    
    # Heures réelles
    heure_debut_prevue = models.TimeField(
        verbose_name="Heure de début prévue",
        help_text="Récupéré de la config admin"
    )
    heure_arrivee_reelle = models.TimeField(
        verbose_name="Heure d'arrivée réelle"
    )
    
    # Calcul automatique
    minutes_retard = models.PositiveIntegerField(
        default=0,
        verbose_name="Minutes de retard"
    )
    heures_a_rattraper = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Heures à rattraper"
    )
    heures_restantes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Heures restantes à rattraper"
    )
    
    # Justificatif
    motif_retard = models.TextField(
        blank=True,
        null=True,
        verbose_name="Justificatif / Motif du retard"
    )
    
    # Type calculé automatiquement selon les minutes
    type_retard = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Type de retard calculé"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    
    # Timestamps
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    # Validation
    approuve_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='retards_approuves',
        verbose_name="Approuvé par"
    )
    date_approbation = models.DateTimeField(null=True, blank=True, verbose_name="Date d'approbation")
    
    # Annulation
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
    
    # Lien vers retard original (si fractionné)
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
    
    def __str__(self):
        return f"{self.utilisateur.get_display_name()} - {self.date} ({self.minutes_retard}min)"
    
    def calculer_retard(self):
        """Calcule les minutes de retard et les heures à rattraper"""
        from datetime import datetime
        
        # Calcul des minutes de retard
        debut = datetime.combine(self.date, self.heure_debut_prevue)
        arrivee = datetime.combine(self.date, self.heure_arrivee_reelle)
        
        diff = arrivee - debut
        self.minutes_retard = max(0, int(diff.total_seconds() / 60))
        
        # Déterminer le type de retard
        config = self._get_config_retard()
        if config:
            self.type_retard = config.type_retard
            # Calculer heures à rattraper avec multiplicateur
            heures_brutes = Decimal(self.minutes_retard) / Decimal('60')
            self.heures_a_rattraper = (heures_brutes * config.multiplicateur).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        else:
            # Fallback si pas de config
            self.type_retard = 'leger'
            self.heures_a_rattraper = (Decimal(self.minutes_retard) / Decimal('60')).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        
        # Initialiser les heures restantes
        if self.heures_restantes == 0 or self._state.adding:
            self.heures_restantes = self.heures_a_rattraper
        
        return self.minutes_retard, self.heures_a_rattraper
    
    def _get_config_retard(self):
        """Récupère la config selon les minutes de retard"""
        for config in TypeRetardConfig.objects.all().order_by('minutes_min'):
            if self.minutes_retard >= config.minutes_min:
                if config.minutes_max is None or self.minutes_retard <= config.minutes_max:
                    return config
        return None
    
    def rattraper_heures(self, heures_rattrapees):
        """Met à jour les heures restantes après un rattrapage"""
        self.heures_restantes = max(Decimal('0'), self.heures_restantes - Decimal(str(heures_rattrapees)))
        self.heures_restantes = self.heures_restantes.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Si tout est rattrapé, passer en approuvé
        if self.heures_restantes <= 0:
            self.statut = 'approuve'
        
        self.save()
        return self.heures_restantes


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
        verbose_name="Heures rattrapées"
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
    
    def calculer_heures(self):
        """Calcule les heures entre début et fin"""
        from datetime import datetime
        
        debut = datetime.combine(self.date_rattrapage, self.heure_debut)
        fin = datetime.combine(self.date_rattrapage, self.heure_fin)
        
        diff = fin - debut
        heures = Decimal(str(diff.total_seconds())) / Decimal('3600')
        self.heures_rattrapees = heures.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.heures_rattrapees
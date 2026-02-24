from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User


class TypeCongeConfig(models.Model):
    """Configuration des types de congés et leurs horaires"""
    
    TYPE_CHOICES = [
        ('matin', 'Matin'),
        ('midi', 'Midi'),
        ('journee', 'Une journée'),
    ]
    
    type_conge = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        unique=True,
        verbose_name="Type de congé"
    )
    
    # Horaires par défaut
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    
    # Valeurs de déduction/consommation
    deduction_jours = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.5'),
        verbose_name="Déduction (jours)",
        help_text="Nombre de jours déduits du solde"
    )
    
    # Règles spéciales
    vendredi_deduction = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Déduction Vendredi",
        help_text="Si différent du standard (ex: Vendredi Midi = 2.5)"
    )
    
    jeudi_deduction = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Déduction Jeudi",
        help_text="Si Vendredi est rayé, Jeudi = -3 jours"
    )
    
    class Meta:
        verbose_name = "Configuration type de congé"
        verbose_name_plural = "Configurations types de congé"
    
    def __str__(self):
        return f"{self.get_type_conge_display()} ({self.heure_debut}-{self.heure_fin})"


class JourFerie(models.Model):
    """Jours fériés récurrents chaque année"""
    
    nom = models.CharField(max_length=100, verbose_name="Nom")
    mois = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Mois"
    )
    jour = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name="Jour"
    )
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Jour férié"
        verbose_name_plural = "Jours fériés"
        unique_together = ['mois', 'jour']
        ordering = ['mois', 'jour']
    
    def __str__(self):
        return f"{self.nom} ({self.jour}/{self.mois})"


class JourExceptionnel(models.Model):
    """Jours exceptionnels (rayés) ou non-exceptionnels (dé-rayés)"""
    
    TYPE_CHOICES = [
        ('exceptionnel', 'Jour exceptionnel (rayé)'),
        ('non_exceptionnel', 'Jour non-exceptionnel (dé-rayé)'),
    ]
    
    type_jour = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type"
    )
    
    date = models.DateField(verbose_name="Date")
    annee = models.PositiveSmallIntegerField(verbose_name="Année")
    description = models.CharField(max_length=200, blank=True, verbose_name="Description")
    
    class Meta:
        verbose_name = "Jour exceptionnel"
        verbose_name_plural = "Jours exceptionnels"
        ordering = ['-annee', 'date']
    
    def __str__(self):
        return f"{self.get_type_jour_display()} - {self.date}"


class CongeAnnuel(models.Model):
    """Périodes de congés annuels (rayées sur le calendrier)"""
    
    nom = models.CharField(max_length=100, verbose_name="Nom")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    annee = models.PositiveSmallIntegerField(verbose_name="Année")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Congé annuel"
        verbose_name_plural = "Congés annuels"
        ordering = ['-annee', 'date_debut']
    
    def __str__(self):
        return f"{self.nom} ({self.date_debut} - {self.date_fin})"


class Conge(models.Model):
    """Demande de congé d'un utilisateur"""
    
    TYPE_CHOICES = [
        ('matin', 'Matin'),
        ('midi', 'Midi'),
        ('journee', 'Une journée'),
    ]
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conges',
        verbose_name="Utilisateur"
    )
    
    type_conge = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="Type de congé"
    )
    
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    
    motif = models.TextField(blank=True, null=True, verbose_name="Motif")
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    
    # Calculs automatiques
    jours_deduits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name="Jours déduits",
        help_text="Calculé automatiquement selon les règles"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.utilisateur.get_display_name()} - {self.get_type_conge_display()} ({self.date_debut})"
    
    def calculer_deduction(self):
        """Calcule la déduction selon les règles métier"""
        from datetime import timedelta
        
        config = TypeCongeConfig.objects.get(type_conge=self.type_conge)
        total_jours = 0
        
        current_date = self.date_debut
        while current_date <= self.date_fin:
            weekday = current_date.weekday()  # 0=Lundi, 6=Dimanche
            
            # Vérifier si c'est un weekend (Samedi=5, Dimanche=6)
            if weekday >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Vérifier si c'est un jour férié
            if JourFerie.objects.filter(mois=current_date.month, jour=current_date.day, est_actif=True).exists():
                current_date += timedelta(days=1)
                continue
            
            # Vérifier si c'est un jour exceptionnel
            jour_exc = JourExceptionnel.objects.filter(date=current_date, annee=current_date.year).first()
            if jour_exc and jour_exc.type_jour == 'exceptionnel':
                current_date += timedelta(days=1)
                continue
            
            # Calculer la déduction selon le jour
            deduction = config.deduction_jours
            
            # Règles spéciales Vendredi (4)
            if weekday == 4:  # Vendredi
                if config.vendredi_deduction:
                    deduction = config.vendredi_deduction
            
            # Règles spéciales Jeudi (3) si Vendredi suivant est rayé
            if weekday == 3:  # Jeudi
                vendredi_suivant = current_date + timedelta(days=1)
                # Vérifier si Vendredi est exceptionnel ou férié
                if (JourExceptionnel.objects.filter(date=vendredi_suivant, type_jour='exceptionnel').exists() or
                    JourFerie.objects.filter(mois=vendredi_suivant.month, jour=vendredi_suivant.day).exists()):
                    if config.jeudi_deduction:
                        deduction = config.jeudi_deduction
            
            total_jours += float(deduction)
            current_date += timedelta(days=1)
        
        self.jours_deduits = total_jours
        return total_jours
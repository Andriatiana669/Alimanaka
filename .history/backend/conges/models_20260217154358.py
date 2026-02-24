from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal, ROUND_HALF_UP  # ← AJOUTÉ
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
        default=Decimal('0.5'),  # ← CORRIGÉ: Decimal au lieu de 0.5
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


class Droit(models.Model):
    """Types de droits (congés exceptionnels) qui ne déduisent pas du solde"""
    
    nom = models.CharField(max_length=100, verbose_name="Nom du droit")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.PositiveSmallIntegerField(default=0, verbose_name="Ordre d'affichage")
    
    class Meta:
        verbose_name = "Droit (congé exceptionnel)"
        verbose_name_plural = "Droits (congés exceptionnels)"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom
    
    
    
    
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
        default=Decimal('0.00'),  # ← CORRIGÉ: Decimal au lieu de 0.0
        verbose_name="Jours déduits",
        help_text="Calculé automatiquement selon les règles"
    )
    
    jours_valides = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Jours validés",
        help_text="Liste des dates validées (pour validation partielle)"
    )
    
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    valide_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conges_valides',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")
    
    refuse_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conges_refuses',
        verbose_name="Refusé par"
    )
    date_refus = models.DateTimeField(null=True, blank=True, verbose_name="Date de refus")
    commentaire_refus = models.TextField(blank=True, null=True, verbose_name="Commentaire de refus")
    
    conge_original = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conges_fractionnes',
        verbose_name="Congé original"
    )
    
    est_droit = models.BooleanField(default=False, verbose_name="Est un droit (congé exceptionnel)")
    droit = models.ForeignKey(
        Droit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conges',
        verbose_name="Droit sélectionné"
    )
    
    class Meta:
        verbose_name = "Congé"
        verbose_name_plural = "Congés"
        ordering = ['-date_debut']
        
        
    def est_valide(self, date):
        """Vérifie si une date spécifique est validée"""
        date_str = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else date
        return date_str in self.jours_valides
    
    def __str__(self):
        return f"{self.utilisateur.get_display_name()} - {self.get_type_conge_display()} ({self.date_debut})"
    
    def calculer_deduction(self):
        """Calcule la déduction selon les règles métier"""
        from datetime import timedelta
        
        config = TypeCongeConfig.objects.get(type_conge=self.type_conge)
        total_jours = Decimal('0')  # ← CORRIGÉ: Initialiser en Decimal
        
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
            deduction = config.deduction_jours  # ← Déjà un Decimal
            
            # Règles spéciales Vendredi (4)
            if weekday == 4:  # Vendredi
                if config.vendredi_deduction:
                    deduction = config.vendredi_deduction  # ← Déjà un Decimal
            
            # Règles spéciales Jeudi (3) si Vendredi suivant est rayé
            if weekday == 3:  # Jeudi
                vendredi_suivant = current_date + timedelta(days=1)
                # Vérifier si Vendredi est exceptionnel ou férié
                if (JourExceptionnel.objects.filter(date=vendredi_suivant, type_jour='exceptionnel').exists() or
                    JourFerie.objects.filter(mois=vendredi_suivant.month, jour=vendredi_suivant.day).exists()):
                    if config.jeudi_deduction:
                        deduction = config.jeudi_deduction  # ← Déjà un Decimal
                        
            # Si c'est un droit, pas de déduction
            if self.est_droit:
                self.jours_deduits = Decimal('0.00')
                return self.jours_deduits
            
            
            total_jours += deduction  # ← CORRIGÉ: Decimal + Decimal ✓
            current_date += timedelta(days=1)
        
        # Arrondir à 2 décimales
        self.jours_deduits = total_jours.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return self.jours_deduits
    
    

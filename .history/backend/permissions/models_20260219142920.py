# backend/permissions/models.py

from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from users.models import User
from conges.models import TypeCongeConfig, Conge  # Pour la transformation


class Permission(models.Model):
    """Permission de sortie (max 2h)"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),        # Créé, en attente du jour J
        ('retourne', 'Retourné'),             # Après avoir cliqué sur "De retour"
        ('rattrapage', 'Rattrapage en cours'), # Rattrapage commencé
        ('approuve', 'Approuvé'),              # Rattrapage terminé
        ('transforme', 'Transformé en congé'), # Transformé en congé (va dans Conges.vue)
        ('annule', 'Annulé'),
    ]
    
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='permissions',
        verbose_name="Utilisateur"
    )
    
    date = models.DateField(verbose_name="Date de la permission")
    
    # Heures planifiées
    heure_depart = models.TimeField(verbose_name="Heure de départ")
    heure_arrivee_max = models.TimeField(
        verbose_name="Heure d'arrivée max",
        help_text="Calculé automatiquement: heure_depart + 2h"
    )
    
    # Heure réelle de retour (saisie le jour J)
    heure_arrivee_reelle = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Heure d'arrivée réelle"
    )
    
    motif = models.TextField(verbose_name="Motif de la permission")
    
    # Calculs automatiques
    minutes_depassement = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Minutes de dépassement"
    )
    
    heures_a_rattraper = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        editable=False,
        verbose_name="Heures à rattraper"
    )
    
    heures_restantes = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Heures restantes à rattraper"
    )
    
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut",
        db_index=True
    )
    
    # Rattrapages (comme pour les retards)
    rattrapages = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Sessions de rattrapage"
    )
    
    # Lien vers le congé si transformé
    conge_genere = models.ForeignKey(
        Conge,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_origine',
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
        related_name='permissions_validees',
        verbose_name="Validé par"
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Annulation
    annule_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permissions_annulees',
        verbose_name="Annulé par"
    )
    date_annulation = models.DateTimeField(null=True, blank=True)
    commentaire_annulation = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['-date', '-date_creation']
        indexes = [
            models.Index(fields=['utilisateur', 'date']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"{self.utilisateur.get_display_name()} - {self.date} ({self.heure_depart})"
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # Calculer l'heure d'arrivée max (départ + 2h)
            from datetime import datetime, timedelta
            depart_dt = datetime.combine(self.date, self.heure_depart)
            arrivee_max_dt = depart_dt + timedelta(hours=2)
            self.heure_arrivee_max = arrivee_max_dt.time()
        
        super().save(*args, **kwargs)
    
    def enregistrer_retour(self, heure_arrivee):
        """Méthode appelée quand l'utilisateur clique sur 'De retour'"""
        self.heure_arrivee_reelle = heure_arrivee
        self.statut = 'retourne'
        
        # Calculer le dépassement
        from datetime import datetime, timedelta
        arrivee_dt = datetime.combine(self.date, heure_arrivee)
        max_dt = datetime.combine(self.date, self.heure_arrivee_max)
        
        if arrivee_dt > max_dt:
            diff = arrivee_dt - max_dt
            self.minutes_depassement = int(diff.total_seconds() / 60)
            # Convertir en heures (1 minute = 1/60 heure)
            self.heures_a_rattraper = Decimal(self.minutes_depassement) / Decimal('60')
            self.heures_restantes = self.heures_a_rattraper
        else:
            self.minutes_depassement = 0
            self.heures_a_rattraper = Decimal('0')
            self.heures_restantes = Decimal('0')
            self.statut = 'approuve'  # Pas de dépassement, approuvé directement
        
        self.save()
        return self.heures_a_rattraper
    
    def ajouter_rattrapage(self, date_rattrapage, heure_debut, heure_fin, commentaire="", user=None):
        """Ajoute une session de rattrapage (comme dans retards)"""
        from datetime import datetime
        
        # Calculer les heures rattrapées
        debut = datetime.combine(date_rattrapage, heure_debut)
        fin = datetime.combine(date_rattrapage, heure_fin)
        diff = fin - debut
        heures = Decimal(str(diff.total_seconds())) / Decimal('3600')
        
        # Ajouter au JSON des rattrapages
        rattrapage = {
            'id': len(self.rattrapages) + 1,
            'date': date_rattrapage.isoformat(),
            'heure_debut': heure_debut.isoformat(),
            'heure_fin': heure_fin.isoformat(),
            'heures': float(heures),
            'commentaire': commentaire,
            'valide_par': user.id if user else None,
            'date_validation': datetime.now().isoformat()
        }
        
        self.rattrapages.append(rattrapage)
        
        # Mettre à jour les heures restantes
        self.heures_restantes = max(Decimal('0'), self.heures_restantes - heures)
        self.heures_restantes = self.heures_restantes.quantize(Decimal('0.01'))
        
        if self.heures_restantes <= 0:
            self.statut = 'approuve'  # Rattrapage terminé → approuvé
        else:
            self.statut = 'rattrapage'  # Encore des heures à rattraper
        
        self.save()
        return heures
    
    def transformer_en_conge(self, type_conge, user=None):
        """Transforme la permission en congé"""
        from conges.models import Conge
        
        # Créer le congé
        conge = Conge.objects.create(
            utilisateur=self.utilisateur,
            type_conge=type_conge,
            date_debut=self.date,
            date_fin=self.date,
            motif=f"[PERMISSION] {self.motif}",
            statut='en_attente'  # Sera validé par le manager dans Conges.vue
        )
        
        # Calculer la déduction (selon les règles des congés)
        conge.calculer_deduction()
        conge.save()
        
        # Lier la permission au congé
        self.conge_genere = conge
        self.statut = 'transforme'  # La permission est transformée
        self.save()
        
        return conge
    
    def to_calendar_event(self):
        """Pour l'affichage dans le calendrier"""
        couleur = '#ff9800'  # Orange par défaut (en_attente)
        if self.statut == 'approuve':
            couleur = '#4caf50'  # Vert
        elif self.statut == 'rattrapage':
            couleur = '#2196f3'  # Bleu
        elif self.statut == 'transforme':
            couleur = '#9c27b0'  # Violet (pour indiquer que c'est devenu un congé)
        elif self.statut == 'annule':
            couleur = '#9e9e9e'  # Gris
        elif self.statut == 'retourne':
            couleur = '#ff9800'  # Orange (en attente de décision)
        
        title = f"🚪 {self.utilisateur.username.upper()} - {self.heure_depart}→{self.heure_arrivee_max}"
        if self.heures_restantes > 0:
            title += f" ({self.heures_restantes}h restantes)"
        
        # Ajouter un indicateur si transformé en congé
        if self.statut == 'transforme' and self.conge_genere:
            title += f" → Congé #{self.conge_genere.id}"
        
        return {
            'id': f"perm_{self.id}",
            'title': title,
            'start': self.date.isoformat(),
            'allDay': True,
            'color': couleur,
            'type': 'permission',
            'user_id': self.utilisateur.id,
            'statut': self.statut,
            'heures_restantes': float(self.heures_restantes) if self.heures_restantes else 0,
            'peut_retourner': self.statut == 'en_attente' and self.date <= date.today(),
            'conge_genere_id': self.conge_genere.id if self.conge_genere else None
        }
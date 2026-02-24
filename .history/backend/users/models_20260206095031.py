from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Modèle utilisateur étendu avec pseudo"""
    
    # Les champs existants dans AbstractUser :
    # username = models.CharField(max_length=150, unique=True)  # Matricule
    # first_name = models.CharField(max_length=150)  # Nom
    # last_name = models.CharField(max_length=150)  # Prénom
    # email = models.EmailField(unique=True)
    
    # Nouveau champ
    pseudo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Pseudo",
        help_text="Pseudonyme personnalisé"
    )
    
    # NOUVEAU : Champ pour le format du pseudo
    pseudo_format_choices = [
        ('first_word', 'Premier mot du nom'),
        ('second_word', 'Deuxième mot du nom'),
        ('third_word', 'Troisième mot du nom'),
        ('first_two', 'Premier + Deuxième mots'),
        ('last_two', 'Deuxième + Troisième mots'),
        ('all_words', 'Tous les mots'),
        ('custom', 'Personnalisé (saisie libre)'),
    ]
    
    
    # Métadonnées supplémentaires
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    
    # Champs Keycloak
    keycloak_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name="ID Keycloak"
    )
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        if self.pseudo:
            return f"{self.pseudo} ({self.username})"
        return f"{self.get_full_name()} ({self.username})"
    
    def get_full_name(self):
        """Retourne le nom complet : Prénom Nom"""
        if self.last_name and self.first_name:
            return f"{self.last_name} {self.first_name}"
        return self.username
    
    def get_display_name(self):
        """Retourne le nom d'affichage (pseudo si disponible)"""
        if self.pseudo:
            return self.pseudo
        return self.get_full_name()


@receiver(post_save, sender='users.User')
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil pour l'utilisateur"""
    if created:
        # Ici tu pourras ajouter d'autres modèles liés plus tard
        pass
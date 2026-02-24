from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver



class Pole(models.Model) :
    
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    nom = models.CharField(max_length=100, verbose_name="Nom du pôle")
    description = models.TextField(blank=True, verbose_name="Description")
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pôle"
        verbose_name_plural = "Pôles"
        ordering = ['nom']
    
    def __str__(self):
        return super().__str__()
    
    
class Equipe(models.Model):
    
    nom = models.CharField(max_length=100, verbose_name="Nom de l'équipe")
    description = models.TextField(blank=True, verbose_name="Description")
    pole = models.ForeignKey(
        Pole, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='equipes',
        verbose_name="Pôle"
    )
    
    # Hiérarchie : une équipe a un manager (chef d'équipe)
    manager = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipes_gerees',
        verbose_name="Manager/Chef d'équipe"
    )
    
    # Équipe parente (pour sous-équipes)
    equipe_parente = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sous_equipes',
        verbose_name="Équipe parente"
    )
    
    est_actif = models.BooleanField(default=True, verbose_name="Est actif")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        verbose_name = "Equipe"
        verbose_name_plural = "Equipes"
        ordering = ['nom']
        
    def __str__(self):
        if self.pole:
            return f"{self.nom} ({self.pole.code})"
        return self.nom
    
    @property
    def membres_count(self):
        return self.membres.count()
    
    @property
    def niveau_hierarchique(self):
        """Calcule le niveau dans l'arbre (0 = racine)"""
        niveau = 0
        parent = self.equipe_parente
        while parent:
            niveau += 1
            parent = parent.equipe_parente
        return niveau
    
    

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
    
    
    pseudo_format = models.CharField(
        max_length=20,
        choices=pseudo_format_choices,
        default='first_word',
        verbose_name="Format du pseudo",
        help_text="Comment générer le pseudo à partir du nom"
    )
    
    
    pole = models.ForeignKey(
        Pole,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name="Pôle"
    )
    
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='membres',  # Les membres de l'équipe
        verbose_name="Équipe"
    )
    
    
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
        """Retourne le nom d'affichage selon le format choisi"""
        if self.pseudo_format == 'custom' and self.pseudo:
            return self.pseudo
        
        # Extraire les mots du nom complet
        full_name = self.get_full_name()
        words = [word for word in full_name.split() if word]
        
        if not words:
            return self.username
        
        # Générer selon le format
        if self.pseudo_format == 'first_word' and len(words) >= 1:
            return words[0]
        elif self.pseudo_format == 'second_word' and len(words) >= 2:
            return words[1]
        elif self.pseudo_format == 'third_word' and len(words) >= 3:
            return words[2]
        elif self.pseudo_format == 'first_two' and len(words) >= 2:
            return f"{words[0]} {words[1]}"
        elif self.pseudo_format == 'last_two' and len(words) >= 3:
            return f"{words[1]} {words[2]}"
        elif self.pseudo_format == 'all_words':
            return full_name
        else:
            # Fallback au premier mot
            return words[0]
        
    
    def update_pseudo_from_format(self):
        """Met à jour le pseudo automatiquement selon le format"""
        if self.pseudo_format != 'custom':
            self.pseudo = self.get_display_name()
            self.save()
            
    @property
    def est_chef_equipe(self):
        """Vérifie si l'utilisateur est manager d'une équipe"""
        return self.equipes_gerees.exists()
    
    @property
    def equipes_managerisees(self):
        """Liste des équipes gérées par l'utilisateur"""
        return self.equipes_gerees.filter(est_actif=True)
    
    @property
    def sous_equipes_accessibles(self):
        """Toutes les sous-équipes des équipes gérées (récursif)"""
        equipes = []
        for equipe in self.equipes_gerees.filter(est_actif=True):
            equipes.append(equipe)
            # Récupérer récursivement les sous-équipes
            def get_sous_equipes(eq):
                sous = eq.sous_equipes.filter(est_actif=True)
                result = list(sous)
                for s in sous:
                    result.extend(get_sous_equipes(s))
                return result
            equipes.extend(get_sous_equipes(equipe))
        return equipes


@receiver(post_save, sender='users.User')
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil pour l'utilisateur"""
    if created:
        # Ici tu pourras ajouter d'autres modèles liés plus tard
        pass
    
    
    
    

    
    
    

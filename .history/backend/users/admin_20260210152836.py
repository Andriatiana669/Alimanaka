from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Pole, Equipe


@admin.register(Pole)
class PoleAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'est_actif', 'equipes_count', 'utilisateurs_count']
    list_filter = ['est_actif']
    search_fields = ['code', 'nom', 'description']
    ordering = ['nom']
    
    @admin.display(description="Nombre d'équipes")
    def equipes_count(self, obj):
        return obj.equipes.count()
    
    @admin.display(description="Nombre d'utilisateurs")
    def utilisateurs_count(self, obj):
        return obj.utilisateurs.count()


class EquipeInline(admin.TabularInline):
    """Affiche les sous-équipes dans l'admin"""
    model = Equipe
    fk_name = 'equipe_parente'
    extra = 0
    fields = ['nom', 'manager', 'est_actif']
    show_change_link = True


class CoManagerInline(admin.TabularInline):
    """Affiche les co-managers dans l'admin de l'équipe"""
    model = Equipe.co_managers.through
    extra = 1
    verbose_name = "Co-manager"
    verbose_name_plural = "Co-managers"
    autocomplete_fields = ['user']


@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'pole', 'manager', 'co_managers_list',
        'niveau_hierarchique', 'membres_count', 
        'sous_equipes_count', 'est_actif'
    ]
    list_filter = ['pole', 'est_actif', 'date_creation']
    search_fields = [
        'nom', 'description', 
        'manager__username', 'manager__last_name',
        'co_managers__username', 'co_managers__last_name'
    ]
    raw_id_fields = ['manager', 'equipe_parente']
    filter_horizontal = ['co_managers']  # Interface pratique pour ManyToMany
    inlines = [EquipeInline]
    
    fieldsets = (
        (None, {
            'fields': ('nom', 'description', 'pole', 'est_actif')
        }),
        ('Hiérarchie', {
            'fields': ('manager', 'co_managers', 'equipe_parente'),
            'description': "Configuration de la hiérarchie de l'équipe. Le manager principal est unique, les co-managers sont des assistants."
        }),
    )
    
    @admin.display(description="Niveau hiérarchique")
    def niveau_hierarchique(self, obj):
        return obj.niveau_hierarchique
    
    @admin.display(description="Nombre de membres")
    def membres_count(self, obj):
        return obj.membres.count()
    
    @admin.display(description="Sous-équipes")
    def sous_equipes_count(self, obj):
        return obj.sous_equipes.count()
    
    @admin.display(description="Co-managers")
    def co_managers_list(self, obj):
        """Affiche la liste des co-managers dans la liste"""
        co_managers = obj.co_managers.all()
        if not co_managers:
            return "-"
        return ", ".join([u.get_display_name() for u in co_managers[:3]])
    co_managers_list.short_description = "Co-managers"


class UserEquipeInline(admin.TabularInline):
    """Affiche les équipes gérées par l'utilisateur (en tant que manager principal)"""
    model = Equipe
    fk_name = 'manager'
    extra = 0
    fields = ['nom', 'pole', 'est_actif']
    verbose_name = "Équipe gérée (manager principal)"
    verbose_name_plural = "Équipes gérées (manager principal)"


class UserCoEquipeInline(admin.TabularInline):
    """Affiche les équipes co-gérées par l'utilisateur"""
    model = Equipe.co_managers.through
    extra = 0
    verbose_name = "Équipe co-gérée"
    verbose_name_plural = "Équipes co-gérées"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        'username', 'display_name', 'pole', 'equipe',
        'est_chef_equipe', 'is_staff', 'is_active', 'last_login'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active',
        'pole', 'equipe', 'pseudo_format',
        'equipes_gerees', 'equipes_co_gerees'  # Filtre par équipes gérées
    ]
    search_fields = [
        'username', 'first_name', 'last_name',
        'email', 'pseudo', 'keycloak_id'
    ]

    # Exclure les champs non modifiables
    exclude = ('date_joined',)

    # Définir les champs en lecture seule
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Informations importantes', {
            'fields': ('last_login', 'date_joined')
        }),
        ('Informations Alimanaka', {
            'fields': ('pseudo', 'pseudo_format', 'keycloak_id')
        }),
        ('Organisation', {
            'fields': ('pole', 'equipe'),
            'description': "Pôle et équipe de l'utilisateur"
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Organisation', {
            'fields': ('pole', 'equipe')
        }),
    )

    inlines = [UserEquipeInline, UserCoEquipeInline]

    @admin.display(description="Nom affiché")
    def display_name(self, obj):
        return obj.get_display_name()
    
    @admin.display(description="Chef d'équipe", boolean=True)
    def est_chef_equipe(self, obj):
        """Indique si l'utilisateur est manager d'au moins une équipe"""
        return obj.equipes_gerees.exists() or obj.equipes_co_gerees.exists()
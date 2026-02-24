# backend/users/admin_site.py
from django.contrib.admin import AdminSite
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import User, Pole, Equipe


# ============================================================================
# CUSTOM ADMIN SITE
# ============================================================================

class AlimanakaAdminSite(AdminSite):
    site_header = "Administration Alimanaka"
    site_title = "Alimanaka Admin"
    index_title = "Tableau de bord"
    site_url = "/"


# ============================================================================
# CUSTOM FILTERS
# ============================================================================

class EstActifFilter(admin.SimpleListFilter):
    title = 'Statut'
    parameter_name = 'est_actif'
    
    def lookups(self, request, model_admin):
        return (
            ('actif', 'Actif'),
            ('inactif', 'Inactif'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'actif':
            return queryset.filter(est_actif=True)
        if self.value() == 'inactif':
            return queryset.filter(est_actif=False)


class ChefEquipeFilter(admin.SimpleListFilter):
    title = 'Rôle dans équipe'
    parameter_name = 'est_chef'
    
    def lookups(self, request, model_admin):
        return (
            ('chef', 'Chef d\'équipe'),
            ('co', 'Co-manager'),
            ('membre', 'Membre simple'),
            ('sans', 'Sans équipe'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'chef':
            return queryset.filter(equipes_gerees__isnull=False)
        if self.value() == 'co':
            return queryset.filter(equipes_co_gerees__isnull=False)
        if self.value() == 'membre':
            return queryset.filter(equipe__isnull=False).exclude(
                equipes_gerees__isnull=False
            ).exclude(
                equipes_co_gerees__isnull=False
            )
        if self.value() == 'sans':
            return queryset.filter(equipe__isnull=True)


# ============================================================================
# POLE ADMIN
# ============================================================================

class PoleAdmin(admin.ModelAdmin):
    list_display = [
        'code_badge', 'nom', 'stats_badge', 
        'est_actif_badge', 'action_buttons'
    ]
    list_display_links = ['code_badge', 'nom']
    list_filter = [EstActifFilter]
    search_fields = ['code', 'nom', 'description']
    ordering = ['nom']
    list_per_page = 20
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('code', 'nom', 'description'),
            'classes': ('wide',)
        }),
        ('Statut', {
            'fields': ('est_actif',),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description="Code")
    def code_badge(self, obj):
        color = "green" if obj.est_actif else "gray"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-weight: bold;">{}</span>',
            color, obj.code
        )
    
    @admin.display(description="Statistiques")
    def stats_badge(self, obj):
        equipes_count = obj.equipes.count()
        users_count = obj.utilisateurs.count()
        return format_html(
            '<div style="display: flex; gap: 10px;">'
            '<span title="Équipes" style="background: #3498db; color: white; '
            'padding: 2px 8px; border-radius: 10px;">🏢 {} équipes</span>'
            '<span title="Utilisateurs" style="background: #2ecc71; color: white; '
            'padding: 2px 8px; border-radius: 10px;">👤 {} users</span>'
            '</div>',
            equipes_count, users_count
        )
    
    @admin.display(description="Statut")
    def est_actif_badge(self, obj):
        if obj.est_actif:
            return format_html(
                '<span style="background-color: #2ecc71; color: white; '
                'padding: 4px 12px; border-radius: 12px; font-weight: bold;">'
                '✅ Actif</span>'
            )
        return format_html(
            '<span style="background-color: #e74c3c; color: white; '
            'padding: 4px 12px; border-radius: 12px; font-weight: bold;">'
            '❌ Inactif</span>'
        )
    
    @admin.display(description="Actions")
    def action_buttons(self, obj):
        view_url = reverse('alimanaka_admin:users_pole_changelist') + f'?pole__id__exact={obj.id}'
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<a href="{}" class="button" title="Voir les équipes" '
            'style="background: #3498db; color: white; padding: 4px 8px; '
            'border-radius: 4px; text-decoration: none;">🏢 Équipes</a>'
            '<a href="{}" class="button" title="Voir les utilisateurs" '
            'style="background: #2ecc71; color: white; padding: 4px 8px; '
            'border-radius: 4px; text-decoration: none;">👤 Users</a>'
            '</div>',
            view_url, view_url
        )


# ============================================================================
# EQUIPE ADMIN
# ============================================================================

class SousEquipeInline(admin.TabularInline):
    model = Equipe
    fk_name = 'equipe_parente'
    extra = 0
    fields = ['nom_link', 'manager_link', 'membres_badge', 'est_actif_badge']
    readonly_fields = ['nom_link', 'manager_link', 'membres_badge', 'est_actif_badge']
    can_delete = False
    max_num = 10
    verbose_name = "Sous-équipe"
    verbose_name_plural = "Sous-équipes"
    
    @admin.display(description="Nom")
    def nom_link(self, obj):
        url = reverse('alimanaka_admin:users_equipe_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.nom)
    
    @admin.display(description="Manager")
    def manager_link(self, obj):
        if obj.manager:
            url = reverse('alimanaka_admin:users_user_change', args=[obj.manager.id])
            return format_html('<a href="{}">{}</a>', url, obj.manager.get_display_name())
        return "-"
    
    @admin.display(description="Membres")
    def membres_badge(self, obj):
        count = obj.membres.count()
        color = "blue" if count > 0 else "gray"
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 10px;">👥 {}</span>',
            color, count
        )
    
    @admin.display(description="Statut")
    def est_actif_badge(self, obj):
        if obj.est_actif:
            return format_html('<span style="color: green;">✅</span>')
        return format_html('<span style="color: red;">❌</span>')


class EquipeAdmin(admin.ModelAdmin):
    list_display = [
        'nom', 'pole_link', 'hierarchy_indicator',
        'manager_link', 'co_managers_badge',
        'membres_badge', 'sous_equipes_badge',
        'est_actif_badge', 'action_buttons'
    ]
    list_display_links = ['nom']
    list_filter = ['pole', EstActifFilter, 'date_creation']
    search_fields = ['nom', 'description', 'manager__username', 'manager__last_name']
    ordering = ['nom']
    list_per_page = 25
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'pole', 'est_actif'),
            'classes': ('wide',)
        }),
        ('Hiérarchie', {
            'fields': ('manager', 'co_managers', 'equipe_parente'),
            'classes': ('collapse',),
            'description': format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; '
                'margin-bottom: 10px;">'
                '<strong>💡 Astuce :</strong> Le manager principal est unique, '
                'les co-managers sont des assistants.'
                '</div>'
            )
        }),
    )
    
    filter_horizontal = ['co_managers']
    inlines = [SousEquipeInline]
    
    @admin.display(description="Pôle")
    def pole_link(self, obj):
        if obj.pole:
            url = reverse('alimanaka_admin:users_pole_change', args=[obj.pole.id])
            return format_html(
                '<a href="{}" style="background: #3498db; color: white; '
                'padding: 2px 8px; border-radius: 10px; text-decoration: none;">{}</a>',
                url, obj.pole.code
            )
        return format_html(
            '<span style="background: #95a5a6; color: white; padding: 2px 8px; '
            'border-radius: 10px;">Sans pôle</span>'
        )
    
    @admin.display(description="Niveau")
    def hierarchy_indicator(self, obj):
        level = obj.niveau_hierarchique
        dots = "•" * (level + 1)
        return format_html(
            '<span style="color: #7f8c8d;" title="Niveau {}">{}</span>',
            level, dots
        )
    
    @admin.display(description="Manager")
    def manager_link(self, obj):
        if obj.manager:
            url = reverse('alimanaka_admin:users_user_change', args=[obj.manager.id])
            return format_html(
                '<a href="{}" style="background: #e67e22; color: white; '
                'padding: 2px 8px; border-radius: 10px; text-decoration: none;">👑 {}</a>',
                url, obj.manager.get_display_name()
            )
        return format_html(
            '<span style="background: #95a5a6; color: white; padding: 2px 8px; '
            'border-radius: 10px;">Non assigné</span>'
        )
    
    @admin.display(description="Co-managers")
    def co_managers_badge(self, obj):
        co_managers = obj.co_managers.all()
        if not co_managers:
            return "-"
        return format_html(
            '<div style="display: flex; flex-wrap: wrap; gap: 3px;">{}</div>',
            "".join([
                format_html(
                    '🛡️ {} {}',
                    cm.get_display_name(),  # <-- Affiche le display_name dans le titre
                    cm.username.upper(),     # <-- Matricule dans le tooltip
                    cm.get_display_name()[:8]  # <-- Affiche le display_name (tronqué si long)
                ) for cm in co_managers[:3]
            ]) + ("..." if len(co_managers) > 3 else "")
        )
    
    @admin.display(description="Membres")
    def membres_badge(self, obj):
        count = obj.membres.count()
        color = "#3498db" if count > 0 else "#95a5a6"
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-weight: bold;">👥 {}</span>',
            color, count
        )
    
    @admin.display(description="Sous-équipes")
    def sous_equipes_badge(self, obj):
        count = obj.sous_equipes.count()
        if count > 0:
            url = reverse('alimanaka_admin:users_equipe_changelist') + f'?equipe_parente__id__exact={obj.id}'
            return format_html(
                '<a href="{}" style="background: #9b59b6; color: white; padding: 4px 10px; '
                'border-radius: 12px; font-weight: bold; text-decoration: none;">'
                '🏗️ {}</a>', url, count
            )
        return format_html(
            '<span style="background: #95a5a6; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-weight: bold;">🏗️ 0</span>'
        )
    
    @admin.display(description="Statut")
    def est_actif_badge(self, obj):
        if obj.est_actif:
            return format_html(
                '<span style="background: #2ecc71; color: white; padding: 4px 12px; '
                'border-radius: 12px; font-weight: bold;">✅ Actif</span>'
            )
        return format_html(
            '<span style="background: #e74c3c; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">❌ Inactif</span>'
        )
    
    @admin.display(description="Actions")
    def action_buttons(self, obj):
        view_url = reverse('alimanaka_admin:users_user_changelist') + f'?equipe__id__exact={obj.id}'
        return format_html(
            '<a href="{}" class="button" title="Voir les membres" '
            'style="background: #3498db; color: white; padding: 4px 8px; '
            'border-radius: 4px; text-decoration: none;">👥 Membres</a>',
            view_url
        )


# ============================================================================
# USER ADMIN
# ============================================================================

class EquipeGereeInline(admin.TabularInline):
    model = Equipe
    fk_name = 'manager'
    extra = 0
    fields = ['nom_link', 'pole_badge', 'membres_badge', 'est_actif_badge']
    readonly_fields = ['nom_link', 'pole_badge', 'membres_badge', 'est_actif_badge']
    can_delete = False
    verbose_name = "Équipe gérée (Manager)"
    verbose_name_plural = "Équipes gérées (Manager)"
    
    @admin.display(description="Équipe")
    def nom_link(self, obj):
        url = reverse('alimanaka_admin:users_equipe_change', args=[obj.id])
        return format_html('<a href="{}">{}</a>', url, obj.nom)
    
    @admin.display(description="Pôle")
    def pole_badge(self, obj):
        if obj.pole:
            return format_html(
                '<span style="background: #3498db; color: white; padding: 2px 6px; '
                'border-radius: 10px;">{}</span>',
                obj.pole.code
            )
        return "-"
    
    @admin.display(description="Membres")
    def membres_badge(self, obj):
        return format_html(
            '<span style="background: #2ecc71; color: white; padding: 2px 6px; '
            'border-radius: 10px;">👥 {}</span>',
            obj.membres.count()
        )
    
    @admin.display(description="Statut")
    def est_actif_badge(self, obj):
        if obj.est_actif:
            return format_html('<span style="color: green;">✅</span>')
        return format_html('<span style="color: red;">❌</span>')


class EquipeCoGereeInline(admin.TabularInline):
    model = Equipe.co_managers.through
    extra = 0
    verbose_name = "Équipe co-gérée"
    verbose_name_plural = "Équipes co-gérées"
    autocomplete_fields = ['equipe']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "equipe":
            kwargs["queryset"] = Equipe.objects.filter(est_actif=True).order_by('nom')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'username_badge', 'display_name', 'role_badge',
        'pole_equipe_badge', 'last_login_badge', 'is_active_badge', 'action_buttons'
    ]
    list_display_links = ['username_badge', 'display_name']
    list_filter = [
        'is_staff', 'is_superuser', ChefEquipeFilter,
        'pole', 'equipe', 'pseudo_format'
    ]
    search_fields = [
        'username', 'first_name', 'last_name',
        'email', 'pseudo', 'keycloak_id'
    ]
    ordering = ['last_name', 'first_name']
    list_per_page = 30
    
    readonly_fields = [
        'date_joined', 'last_login', 'equipes_gerees_list',
        'equipes_co_gerees_list', 'role_display'
    ]
    
    fieldsets = (
        ('Identifiants', {
            'fields': ('username', 'password'),
            'classes': ('wide',)
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email'),
            'classes': ('wide',)
        }),
        ('Pseudo Alimanaka', {
            'fields': ('pseudo', 'pseudo_format'),
            'description': format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; '
                'margin-bottom: 10px;">'
                '<strong>💡 Format du pseudo :</strong> '
                'Premier mot = {}, Deuxième mot = {}, etc.'
                '</div>',
                User.pseudo_format_choices[0][1], User.pseudo_format_choices[1][1]
            )
        }),
        ('Organisation', {
            'fields': ('pole', 'equipe'),
            'description': format_html(
                '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px; '
                'margin-bottom: 10px;">'
                '<strong>🏢 Structure :</strong> Pôle → Équipe → Utilisateur'
                '</div>'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('SSO & Métadonnées', {
            'fields': ('keycloak_id', 'date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
        ('Équipes gérées (Lecture seule)', {
            'fields': ('role_display', 'equipes_gerees_list', 'equipes_co_gerees_list'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'fields': ('username', 'password1', 'password2')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Pseudo & Organisation', {
            'fields': ('pseudo', 'pseudo_format', 'pole', 'equipe')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )
    
    inlines = [EquipeGereeInline, EquipeCoGereeInline]
    
    @admin.display(description="Matricule")
    def username_badge(self, obj):
        color = "#e74c3c" if obj.is_superuser else "#3498db" if obj.is_staff else "#2ecc71"
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-weight: bold; font-family: monospace;">{}</span>',
            color, obj.username.upper()
        )
    
    @admin.display(description="Nom affiché")
    def display_name(self, obj):
        display = obj.get_display_name()
        if obj.pseudo and obj.pseudo_format == 'custom':
            return format_html(
                '<strong>{}</strong> <span style="color: #7f8c8d; font-size: 0.9em;">'
                '(Pseudo personnalisé)</span>',
                display
            )
        return display
    
    @admin.display(description="Rôle")
    def role_badge(self, obj):
        if obj.is_superuser:
            return format_html(
                'Super Admin</span>'
            )
        elif obj.is_staff:
            return format_html(
                'Admin / Staff</span>'
            )
        elif obj.equipes_gerees.exists() or obj.equipes_co_gerees.exists():
            return format_html(
                '👨‍💼 Chef d\'équipe</span>'
            )
        else:
            return format_html(
                '👤 Utilisateur</span>'
            )
    
    @admin.display(description="Pôle & Équipe")
    def pole_equipe_badge(self, obj):
        badges = []
        if obj.pole:
            badges.append(format_html(
                '<span style="background: #3498db; color: white; padding: 2px 8px; '
                'border-radius: 10px; margin-right: 5px;">🏢 {}</span>',
                obj.pole.code
            ))
        if obj.equipe:
            color = "#e67e22" if obj.equipes_gerees.filter(id=obj.equipe.id).exists() else "#2ecc71"
            icon = "👑" if obj.equipes_gerees.filter(id=obj.equipe.id).exists() else "👤"
            badges.append(format_html(
                '<span style="background: {}; color: white; padding: 2px 8px; '
                'border-radius: 10px;">{} {}</span>',
                color, icon, obj.equipe.nom[:15] + ("..." if len(obj.equipe.nom) > 15 else "")
            ))
        if not badges:
            badges.append(format_html(
                '<span style="background: #95a5a6; color: white; padding: 2px 8px; '
                'border-radius: 10px;">🚫 Non assigné</span>'
            ))
        return format_html('<div style="display: flex; gap: 5px;">{}</div>', "".join(badges))
    
    @admin.display(description="Dernière connexion")
    def last_login_badge(self, obj):
        if obj.last_login:
            from django.utils import timezone
            from datetime import datetime, timedelta
            
            now = timezone.now()
            delta = now - obj.last_login
            
            if delta < timedelta(minutes=5):
                color = "#2ecc71"
                text = "À l'instant"
            elif delta < timedelta(hours=1):
                color = "#2ecc71"
                text = f"{delta.seconds // 60} min"
            elif delta < timedelta(days=1):
                color = "#f39c12"
                text = f"{delta.seconds // 3600} h"
            else:
                color = "#e74c3c"
                text = f"{delta.days} j"
            
            return format_html(
                '<span style="background: {}; color: white; padding: 3px 8px; '
                'border-radius: 10px; font-size: 0.85em;">{}</span>',
                color, text
            )
        return format_html(
            '<span style="background: #95a5a6; color: white; padding: 3px 8px; '
            'border-radius: 10px; font-size: 0.85em;">Jamais</span>'
        )
    
    @admin.display(description="Statut")
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #2ecc71; color: white; padding: 4px 12px; '
                'border-radius: 12px; font-weight: bold;">✅</span>'
            )
        return format_html(
            '<span style="background: #e74c3c; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">❌</span>'
        )
    
    @admin.display(description="Actions")
    def action_buttons(self, obj):
        equipe_url = reverse('alimanaka_admin:users_equipe_changelist') + f'?manager__id__exact={obj.id}'
        return format_html(
            '<div style="display: flex; gap: 3px;">'
            '<a href="{}" class="button" title="Équipes gérées" '
            'style="background: #e67e22; color: white; padding: 3px 6px; '
            'border-radius: 4px; text-decoration: none; font-size: 0.85em;">🏢</a>'
            '</div>',
            equipe_url
        )
    
    @admin.display(description="Rôle complet")
    def role_display(self, obj):
        return self.role_badge(obj)
    
    @admin.display(description="Équipes gérées (Manager)")
    def equipes_gerees_list(self, obj):
        equipes = obj.equipes_gerees.all()
        if not equipes:
            return format_html('<span style="color: #95a5a6;">Aucune</span>')
        
        items = []
        for equipe in equipes:
            url = reverse('alimanaka_admin:users_equipe_change', args=[equipe.id])
            items.append(format_html(
                '<li style="margin-bottom: 5px;">'
                '<a href="{}" style="color: #3498db;">{}</a> '
                '<span style="color: #7f8c8d; font-size: 0.9em;">'
                '({} membres)</span>'
                '</li>',
                url, equipe.nom, equipe.membres.count()
            ))
        
        return format_html('<ul style="margin: 0; padding-left: 20px;">{}</ul>', "".join(items))
    
    @admin.display(description="Équipes co-gérées")
    def equipes_co_gerees_list(self, obj):
        equipes = obj.equipes_co_gerees.all()
        if not equipes:
            return format_html('<span style="color: #95a5a6;">Aucune</span>')
        
        items = []
        for equipe in equipes:
            url = reverse('alimanaka_admin:users_equipe_change', args=[equipe.id])
            items.append(format_html(
                '<li style="margin-bottom: 5px;">'
                '<a href="{}" style="color: #f39c12;">{}</a> '
                '<span style="color: #7f8c8d; font-size: 0.9em;">'
                '(Manager: {})</span>'
                '</li>',
                url, equipe.nom, 
                equipe.manager.get_display_name() if equipe.manager else "Non assigné"
            ))
        
        return format_html('<ul style="margin: 0; padding-left: 20px;">{}</ul>', "".join(items))


# ============================================================================
# CREATE ADMIN SITE INSTANCE
# ============================================================================

alimanaka_admin = AlimanakaAdminSite(name='alimanaka_admin')

# Enregistre les modèles
alimanaka_admin.register(User, CustomUserAdmin)
alimanaka_admin.register(Pole, PoleAdmin)
alimanaka_admin.register(Equipe, EquipeAdmin)
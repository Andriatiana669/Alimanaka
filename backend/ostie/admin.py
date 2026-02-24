from django.contrib import admin
from django.utils.html import format_html
from users.admin_site import alimanaka_admin
from .models import Ostie, OstieConfig
from django.utils import timezone


class OstieAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur_link', 'date', 'heure_debut', 'heure_fin',
        'statut_badge', 'repos_genere_link'
    ]
    list_filter = ['statut', 'date']
    search_fields = [
        'utilisateur__username', 'utilisateur__first_name',
        'utilisateur__last_name', 'motif'
    ]
    readonly_fields = ['date_creation', 'date_modification']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('utilisateur', 'date', 'heure_debut', 'motif')
        }),
        ('Validation', {
            'fields': ('heure_fin',),
        }),
        ('Transformation en repos médical', {
            'fields': ('repos_genere',),
            'classes': ('collapse',),
        }),
        ('Statut', {
            'fields': ('statut',),
        }),
        ('Validation', {
            'fields': ('valide_par', 'date_validation'),
            'classes': ('collapse',),
        }),
        ('Annulation', {
            'fields': ('annule_par', 'date_annulation', 'commentaire_annulation'),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description="Utilisateur")
    def utilisateur_link(self, obj):
        url = f"/alimanaka-admin/users/user/{obj.utilisateur.id}/change/"
        return format_html(
            '<a href="{}" style="font-weight: 600;">{}</a>',
            url, obj.utilisateur.get_display_name()
        )
    
    @admin.display(description="Repos médical généré")
    def repos_genere_link(self, obj):
        if obj.repos_genere:
            url = f"/alimanaka-admin/reposmedicale/reposmedical/{obj.repos_genere.id}/change/"
            return format_html(
                '<a href="{}">Repos #{}</a>',
                url, obj.repos_genere.id
            )
        return '-'
    
    @admin.display(description="Statut")
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ff9800',
            'approuve': '#4caf50',
            'transforme': '#9c27b0',
            'annule': '#9e9e9e'
        }
        labels = {
            'en_attente': '⏳ En attente',
            'approuve': '✅ Approuvé',
            'transforme': '🔄 Transformé',
            'annule': '❌ Annulé'
        }
        color = colors.get(obj.statut, '#9e9e9e')
        label = labels.get(obj.statut, obj.statut)
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px;">{}</span>',
            color, label
        )
    
    actions = ['valider_osties', 'annuler_osties']
    
    @admin.action(description='Valider les OSTIES sélectionnés')
    def valider_osties(self, request, queryset):
        # Note: cette action ne peut pas définir heure_fin automatiquement
        # Elle est surtout utile pour les tests
        updated = queryset.filter(statut='en_attente').update(
            statut='approuve',
            valide_par=request.user,
            date_validation=timezone.now()
        )
        self.message_user(request, f'{updated} OSTIE(s) validé(s).')
    
    @admin.action(description='Annuler les OSTIES sélectionnés')
    def annuler_osties(self, request, queryset):
        updated = queryset.exclude(statut='annule').update(
            statut='annule',
            annule_par=request.user,
            date_annulation=timezone.now()
        )
        self.message_user(request, f'{updated} OSTIE(s) annulé(s).')


class OstieConfigAdmin(admin.ModelAdmin):
    list_display = ['id']


# Enregistrement sur l'admin Alimanaka
alimanaka_admin.register(Ostie, OstieAdmin)
alimanaka_admin.register(OstieConfig, OstieConfigAdmin)
from django.contrib import admin
from django.utils.html import format_html
from users.admin_site import alimanaka_admin
from .models import Permission


class PermissionAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur_link', 'date', 'heure_depart', 'heure_arrivee_max',
        'statut_badge', 'heures_restantes', 'conge_genere_link'
    ]
    list_filter = ['statut', 'date']
    search_fields = [
        'utilisateur__username', 'utilisateur__first_name',
        'utilisateur__last_name', 'motif'
    ]
    readonly_fields = [
        'minutes_depassement', 'heures_a_rattraper',
        'date_creation', 'date_modification'
    ]
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('utilisateur', 'date', 'heure_depart', 'motif')
        }),
        ('Retour et calculs', {
            'fields': ('heure_arrivee_reelle', 'heure_arrivee_max', 
                      'minutes_depassement', 'heures_a_rattraper', 'heures_restantes'),
            'classes': ('collapse',),
        }),
        ('Rattrapages', {
            'fields': ('rattrapages',),
            'classes': ('collapse',),
        }),
        ('Transformation en congé', {
            'fields': ('conge_genere',),
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
    
    @admin.display(description="Congé généré")
    def conge_genere_link(self, obj):
        if obj.conge_genere:
            url = f"/alimanaka-admin/conges/conge/{obj.conge_genere.id}/change/"
            return format_html(
                '<a href="{}">Congé #{}</a>',
                url, obj.conge_genere.id
            )
        return '-'
    
    @admin.display(description="Statut")
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ff9800',
            'retourne': '#2196f3',
            'rattrapage': '#9c27b0',
            'approuve': '#4caf50',
            'transforme': '#9c27b0',
            'annule': '#9e9e9e'
        }
        labels = {
            'en_attente': '⏳ En attente',
            'retourne': '🔄 Retourné',
            'rattrapage': '⏱️ Rattrapage',
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
    
    actions = ['marquer_approuve', 'annuler_permissions']
    
    @admin.action(description='Marquer comme approuvé')
    def marquer_approuve(self, request, queryset):
        updated = queryset.filter(statut__in=['retourne', 'rattrapage']).update(
            statut='approuve',
            valide_par=request.user,
            date_validation=timezone.now(),
            heures_restantes=0
        )
        self.message_user(request, f'{updated} permission(s) approuvée(s).')
    
    @admin.action(description='Annuler les permissions sélectionnées')
    def annuler_permissions(self, request, queryset):
        from django.utils import timezone
        updated = queryset.exclude(statut='annule').update(
            statut='annule',
            annule_par=request.user,
            date_annulation=timezone.now()
        )
        self.message_user(request, f'{updated} permission(s) annulée(s).')


# Enregistrement sur l'admin Alimanaka
alimanaka_admin.register(Permission, PermissionAdmin)
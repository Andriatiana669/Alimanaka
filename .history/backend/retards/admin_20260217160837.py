from django.contrib import admin
from django.utils.html import format_html
from users.admin_site import alimanaka_admin
from .models import TypeRetardConfig, Retard, Rattrapage


class TypeRetardConfigAdmin(admin.ModelAdmin):
    list_display = ['type_retard_badge', 'minutes_min', 'minutes_max', 'multiplicateur', 'couleur_preview', 'est_actif', 'ordre']
    list_editable = ['minutes_min', 'minutes_max', 'multiplicateur', 'est_actif', 'ordre']
    list_filter = ['est_actif']
    
    @admin.display(description="Type")
    def type_retard_badge(self, obj):
        colors = {
            'leger': '#4caf50',      # Vert
            'moyen': '#ff9800',       # Orange
            'important': '#f44336'    # Rouge
        }
        color = colors.get(obj.type_retard, '#9e9e9e')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color, obj.get_type_retard_display()
        )
    
    @admin.display(description="Couleur")
    def couleur_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 30px; border-radius: 4px; background: {};"></div>',
            obj.couleur
        )


class RattrapageInline(admin.TabularInline):
    model = Rattrapage
    extra = 0
    readonly_fields = ['date_validation', 'valide_par']
    fields = ['date_rattrapage', 'heure_debut', 'heure_fin', 'heures_rattrapees', 'valide_par', 'date_validation']


class RetardAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur_link', 'date', 'minutes_retard_badge', 'heures_restantes',
        'type_retard_badge', 'statut_badge', 'date_creation'
    ]
    list_filter = ['statut', 'type_retard', 'date']
    search_fields = [
        'utilisateur__username', 'utilisateur__first_name',
        'utilisateur__last_name', 'motif_retard'
    ]
    readonly_fields = ['minutes_retard', 'heures_a_rattraper', 'type_retard', 'date_creation', 'date_modification']
    date_hierarchy = 'date'
    inlines = [RattrapageInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('utilisateur', 'date', 'heure_debut_prevue', 'heure_arrivee_reelle', 'motif_retard')
        }),
        ('Calculs automatiques', {
            'fields': ('minutes_retard', 'heures_a_rattraper', 'heures_restantes', 'type_retard'),
            'classes': ('collapse',),
        }),
        ('Statut', {
            'fields': ('statut',),
        }),
        ('Approbation', {
            'fields': ('approuve_par', 'date_approbation'),
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
    
    @admin.display(description="Minutes")
    def minutes_retard_badge(self, obj):
        if obj.minutes_retard < 30:
            color = '#4caf50'
        elif obj.minutes_retard < 60:
            color = '#ff9800'
        else:
            color = '#f44336'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 10px; font-weight: bold;">{}min</span>',
            color, obj.minutes_retard
        )
    
    @admin.display(description="Type")
    def type_retard_badge(self, obj):
        colors = {
            'leger': '#4caf50',
            'moyen': '#ff9800',
            'important': '#f44336'
        }
        color = colors.get(obj.type_retard, '#9e9e9e')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px;">{}</span>',
            color, obj.get_type_retard_display()
        )
    
    @admin.display(description="Statut")
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ff9800',
            'en_cours': '#2196f3',
            'approuve': '#4caf50',
            'annule': '#9e9e9e',
            'remplace': '#9c27b0'
        }
        labels = {
            'en_attente': '⏳ En attente',
            'en_cours': '🔄 En cours',
            'approuve': '✅ Rattrapé',
            'annule': '❌ Annulé',
            'remplace': '🔄 Remplacé'
        }
        color = colors.get(obj.statut, '#9e9e9e')
        label = labels.get(obj.statut, obj.statut)
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px;">{}</span>',
            color, label
        )
    
    actions = ['marquer_en_cours', 'marquer_approuve']
    
    @admin.action(description='Marquer comme en cours')
    def marquer_en_cours(self, request, queryset):
        updated = queryset.filter(statut='en_attente').update(
            statut='en_cours'
        )
        self.message_user(request, f'{updated} retard(s) marqué(s) en cours.')
    
    @admin.action(description='Marquer comme approuvé')
    def marquer_approuve(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(statut__in=['en_attente', 'en_cours']).update(
            statut='approuve',
            approuve_par=request.user,
            date_approbation=timezone.now(),
            heures_restantes=0
        )
        self.message_user(request, f'{updated} retard(s) approuvé(s).')


class RattrapageAdmin(admin.ModelAdmin):
    list_display = ['retard_info', 'date_rattrapage', 'heures_rattrapees', 'valide_par', 'date_validation']
    list_filter = ['date_rattrapage', 'valide_par']
    search_fields = ['retard__utilisateur__username', 'commentaire']
    readonly_fields = ['heures_rattrapees', 'date_validation']
    
    @admin.display(description="Retard concerné")
    def retard_info(self, obj):
        return f"{obj.retard.utilisateur.get_display_name()} - {obj.retard.date}"


# Enregistrement sur l'admin Alimanaka
alimanaka_admin.register(TypeRetardConfig, TypeRetardConfigAdmin)
alimanaka_admin.register(Retard, RetardAdmin)
alimanaka_admin.register(Rattrapage, RattrapageAdmin)
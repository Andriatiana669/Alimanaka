# backend/conges/admin.py
from django.contrib import admin
from django.utils.html import format_html
from users.admin_site import alimanaka_admin  # Importe ton admin personnalisé
from .models import TypeCongeConfig, JourFerie, JourExceptionnel, CongeAnnuel, Conge


class TypeCongeConfigAdmin(admin.ModelAdmin):
    list_display = ['type_conge', 'heure_debut', 'heure_fin', 'deduction_jours', 'vendredi_deduction', 'jeudi_deduction']
    list_editable = ['heure_debut', 'heure_fin', 'deduction_jours', 'vendredi_deduction', 'jeudi_deduction']
    
    @admin.display(description="Type")
    def type_conge(self, obj):
        colors = {
            'matin': '#ff9800',
            'midi': '#4caf50', 
            'journee': '#2196f3'
        }
        color = colors.get(obj.type_conge, '#9e9e9e')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: bold;">{}</span>',
            color, obj.get_type_conge_display()
        )


class JourFerieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_display', 'est_actif_badge']
    # list_editable = ['est_actif']
    list_filter = ['est_actif', 'mois']
    search_fields = ['nom']
    
    @admin.display(description="Date")
    def date_display(self, obj):
        return f"{obj.jour:02d}/{obj.mois:02d}"
    
    @admin.display(description="Statut")
    def est_actif_badge(self, obj):
        if obj.est_actif:
            return format_html('<span style="color: #4caf50;">✅ Actif</span>')
        return format_html('<span style="color: #f44336;">❌ Inactif</span>')


class JourExceptionnelAdmin(admin.ModelAdmin):
    list_display = ['type_jour_badge', 'date', 'annee', 'description']
    list_filter = ['type_jour', 'annee']
    search_fields = ['description']
    
    @admin.display(description="Type")
    def type_jour_badge(self, obj):
        if obj.type_jour == 'exceptionnel':
            return format_html(
                '<span style="background: #ff5722; color: white; padding: 4px 12px; '
                'border-radius: 12px;">⛔ Exceptionnel</span>'
            )
        return format_html(
            '<span style="background: #4caf50; color: white; padding: 4px 12px; '
            'border-radius: 12px;">✅ Non-exceptionnel</span>'
        )


class CongeAnnuelAdmin(admin.ModelAdmin):
    list_display = ['nom', 'periode', 'annee', 'est_actif_badge']
    list_filter = ['annee', 'est_actif']
    list_editable = ['est_actif']
    
    @admin.display(description="Période")
    def periode(self, obj):
        return f"{obj.date_debut} → {obj.date_fin}"
    
    @admin.display(description="Statut")
    def est_actif_badge(self, obj):
        if obj.est_actif:
            return format_html('<span style="color: #4caf50;">✅ Actif</span>')
        return format_html('<span style="color: #f44336;">❌ Inactif</span>')


class CongeAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur_link', 'type_conge_badge', 'periode', 
        'jours_deduits_badge', 'statut_badge', 'date_creation'
    ]
    list_filter = ['statut', 'type_conge', 'date_debut']
    search_fields = [
        'utilisateur__username', 'utilisateur__first_name', 
        'utilisateur__last_name', 'motif'
    ]
    readonly_fields = ['jours_deduits', 'date_creation', 'date_modification']
    date_hierarchy = 'date_debut'
    
    @admin.display(description="Utilisateur")
    def utilisateur_link(self, obj):
        url = f"/alimanaka-admin/users/user/{obj.utilisateur.id}/change/"
        return format_html(
            '<a href="{}" style="font-weight: 600;">{}</a>',
            url, obj.utilisateur.get_display_name()
        )
    
    @admin.display(description="Type")
    def type_conge_badge(self, obj):
        colors = {
            'matin': '#ff9800',
            'midi': '#4caf50',
            'journee': '#2196f3'
        }
        color = colors.get(obj.type_conge, '#9e9e9e')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 0.85em;">{}</span>',
            color, obj.get_type_conge_display()
        )
    
    @admin.display(description="Période")
    def periode(self, obj):
        if obj.date_debut == obj.date_fin:
            return str(obj.date_debut)
        return f"{obj.date_debut} → {obj.date_fin}"
    
    @admin.display(description="Jours")
    def jours_deduits_badge(self, obj):
        color = "#4caf50" if obj.jours_deduits <= 1 else "#ff9800" if obj.jours_deduits <= 2 else "#f44336"
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 10px; font-weight: bold;">{}j</span>',
            color, obj.jours_deduits
        )
    
    @admin.display(description="Statut")
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#ff9800',
            'approuve': '#4caf50',
            'refuse': '#f44336',
            'annule': '#9e9e9e'
        }
        labels = {
            'en_attente': '⏳ En attente',
            'approuve': '✅ Approuvé',
            'refuse': '❌ Refusé',
            'annule': '🚫 Annulé'
        }
        color = colors.get(obj.statut, '#9e9e9e')
        label = labels.get(obj.statut, obj.statut)
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 0.85em;">{}</span>',
            color, label
        )


# Enregistrement sur l'admin Alimanaka personnalisé
alimanaka_admin.register(TypeCongeConfig, TypeCongeConfigAdmin)
alimanaka_admin.register(JourFerie, JourFerieAdmin)
alimanaka_admin.register(JourExceptionnel, JourExceptionnelAdmin)
alimanaka_admin.register(CongeAnnuel, CongeAnnuelAdmin)
alimanaka_admin.register(Conge, CongeAdmin)
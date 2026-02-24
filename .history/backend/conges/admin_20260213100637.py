from django.contrib import admin
from .models import TypeCongeConfig, JourFerie, JourExceptionnel, CongeAnnuel, Conge
from users.admin_site import alimanaka_admin


@admin.register(TypeCongeConfig)
class TypeCongeConfigAdmin(admin.ModelAdmin):
    list_display = ['type_conge', 'heure_debut', 'heure_fin', 'deduction_jours', 'vendredi_deduction', 'jeudi_deduction']
    list_editable = ['heure_debut', 'heure_fin', 'deduction_jours', 'vendredi_deduction', 'jeudi_deduction']


@admin.register(JourFerie)
class JourFerieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'jour', 'mois', 'est_actif']
    list_editable = ['est_actif']
    list_filter = ['est_actif', 'mois']
    search_fields = ['nom']


@admin.register(JourExceptionnel)
class JourExceptionnelAdmin(admin.ModelAdmin):
    list_display = ['type_jour', 'date', 'annee', 'description']
    list_filter = ['type_jour', 'annee']
    search_fields = ['description']


@admin.register(CongeAnnuel)
class CongeAnnuelAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_debut', 'date_fin', 'annee', 'est_actif']
    list_filter = ['annee', 'est_actif']
    list_editable = ['est_actif']


@admin.register(Conge)
class CongeAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'type_conge', 'date_debut', 'date_fin', 'jours_deduits', 'statut', 'date_creation']
    list_filter = ['statut', 'type_conge', 'date_debut']
    search_fields = ['utilisateur__username', 'utilisateur__first_name', 'utilisateur__last_name', 'motif']
    readonly_fields = ['jours_deduits', 'date_creation', 'date_modification']
    date_hierarchy = 'date_debut'
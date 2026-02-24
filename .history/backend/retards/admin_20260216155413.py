from django.contrib import admin
from .models import TypeRetardConfig, Retard, Rattrapage


@admin.register(TypeRetardConfig)
class TypeRetardConfigAdmin(admin.ModelAdmin):
    list_display = ['type_retard', 'minutes_min', 'minutes_max', 'multiplicateur']


class RattrapageInline(admin.TabularInline):
    model = Rattrapage
    extra = 0
    readonly_fields = ['heures_rattrapees', 'date_validation']


@admin.register(Retard)
class RetardAdmin(admin.ModelAdmin):
    list_display = [
        'utilisateur', 'date', 'heure_debut_prevue', 'heure_arrivee_reelle',
        'minutes_retard', 'heures_restantes', 'statut'
    ]
    list_filter = ['statut', 'type_retard', 'date']
    inlines = [RattrapageInline]


@admin.register(Rattrapage)
class RattrapageAdmin(admin.ModelAdmin):
    list_display = ['retard', 'date_rattrapage', 'heure_debut', 'heure_fin', 'heures_rattrapees']
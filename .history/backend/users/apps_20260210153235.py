from django.apps import AppConfig
from django.contrib.admin import AdminSite


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'


class AlimanakaAdminSite(AdminSite):
    site_header = "Administration Alimanaka"
    site_title = "Alimanaka Admin"
    index_title = "Tableau de bord"

alimanaka_admin = AlimanakaAdminSite(name='alimanaka_admin')

# Enregistre tes modèles
alimanaka_admin.register(User, CustomUserAdmin)
alimanaka_admin.register(Pole, PoleAdmin)
alimanaka_admin.register(Equipe, EquipeAdmin)
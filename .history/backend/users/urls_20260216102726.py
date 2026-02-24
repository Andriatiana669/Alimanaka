# backend/users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router existant (ne pas toucher)
router = DefaultRouter()
router.register(r'equipes', views.EquipeViewSet, basename='equipe')
router.register(r'poles', views.PoleViewSet, basename='pole')
router.register(r'users', views.UserViewSet, basename='user')

# NOUVEAU : Router pour les listes filtrées (sans conflit)
public_router = DefaultRouter()
public_router.register(r'poles', views.PoleViewSet, basename='public-pole')

urlpatterns = [
    # Routes API simples existantes (ne pas toucher)
    path('users/current/', views.current_user, name='current_user'),
    path('users/update-pseudo/', views.update_pseudo, name='update_pseudo'),
    path('profile/', views.current_user, name='user_profile'),
    path('users/list/', views.user_list, name='user_list'),
    path('users/solde/', views.user_solde_conge, name='user_solde'),
    
    # NOUVEAU : Routes publiques pour les filtres (sans conflit avec le router existant)
    path('org/', include(public_router.urls)),  # ← /api/org/poles/
    
    # Router existant (ne pas toucher)
    path('', include(router.urls)),
]
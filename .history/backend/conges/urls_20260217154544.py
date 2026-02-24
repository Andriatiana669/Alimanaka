from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    TypeCongeConfigViewSet, JourFerieViewSet, 
    JourExceptionnelViewSet, CongeAnnuelViewSet,
    CongeViewSet, DroitViewSet  # ← AJOUTER DroitViewSet
)

router = DefaultRouter()
router.register(r'types-conge', views.TypeCongeConfigViewSet, basename='types-conge')
router.register(r'jours-feries', views.JourFerieViewSet, basename='jours-feries')
router.register(r'jours-exceptionnels', views.JourExceptionnelViewSet, basename='jours-exceptionnels')
router.register(r'conges-annuels', views.CongeAnnuelViewSet, basename='conges-annuels')
router.register(r'conges', views.CongeViewSet, basename='conges')
router.register(r'droits', DroitViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # Routes d'export (en plus des routes router)
    path('conges/export/', views.CongeViewSet.as_view({'get': 'export'}), name='conges_export'),
    path('conges/export_mine/', views.CongeViewSet.as_view({'get': 'export_mine'}), name='conges_export_mine'),
]
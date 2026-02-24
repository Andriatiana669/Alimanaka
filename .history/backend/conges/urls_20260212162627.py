from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'types-conge', views.TypeCongeConfigViewSet, basename='types-conge')
router.register(r'jours-feries', views.JourFerieViewSet, basename='jours-feries')
router.register(r'jours-exceptionnels', views.JourExceptionnelViewSet, basename='jours-exceptionnels')
router.register(r'conges-annuels', views.CongeAnnuelViewSet, basename='conges-annuels')
router.register(r'conges', views.CongeViewSet, basename='conges')

urlpatterns = [
    path('', include(router.urls)),
]
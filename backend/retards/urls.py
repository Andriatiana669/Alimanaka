from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'types-retard', views.TypeRetardConfigViewSet, basename='types-retard')
router.register(r'retards', views.RetardViewSet, basename='retards')
router.register(r'rattrapages', views.RattrapageViewSet, basename='rattrapages')

urlpatterns = [
    path('', include(router.urls)),
    path('retards/export/', views.RetardViewSet.as_view({'get': 'export'}), name='retards_export'),
    path('retards/export_mine/', views.RetardViewSet.as_view({'get': 'export_mine'}), name='retards_export_mine'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'types-retard', views.TypeRetardConfigViewSet, basename='types-retard')
router.register(r'retards', views.RetardViewSet, basename='retards')

urlpatterns = [
    path('', include(router.urls)),
    path('retards/export/', views.RetardViewSet.as_view({'get': 'export'}), name='retards_export'),
]
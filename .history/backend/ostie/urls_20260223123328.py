from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'osties', views.OstieViewSet, basename='osties')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'repos-medicaux', views.ReposMedicalViewSet, basename='repos-medicaux')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'equipes', views.EquipeViewSet, basename='equipe')
router.register(r'poles', views.PoleViewSet, basename='pole')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    

    
    # Routes API simples
    #path('users/current/', views.current_user, name='current_user'),
    # path('users/update-pseudo/', views.update_pseudo, name='update_pseudo'),
    
    # Routes pour le profil
    # path('profile/', views.current_user, name='user_profile'),
    
    # Lister les personnes ***
    # path('users/list/', views.user_list, name='user_list'),
    
    
    path('auth/current/', views.current_user, name='current_user'),
    path('auth/update-pseudo/', views.update_pseudo, name='update_pseudo'),
    path('auth/profile/', views.current_user, name='user_profile'),
    path('users/list-all/', views.user_list, name='user_list'),
    
        path('', include(router.urls)),
]



# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# router = DefaultRouter()
# router.register(r'users', views.UserViewSet, basename='user')

# urlpatterns = [
#     # Routes API ViewSet
#     path('', include(router.urls)),
    
#     # Routes API simples
#     path('current/', views.current_user, name='current_user'),
#     path('update-pseudo/', views.update_pseudo, name='update_pseudo'),
    
#     # Routes pour le profil
#     path('profile/', views.current_user, name='user_profile'),  # Alias
# ]


# backend/users/urls.py
from django.urls import path
from . import views

# PAS DE ROUTER DRF !

urlpatterns = [
    # Routes personnelles - NOUVEAUX CHEMINS sans conflit
    path('me/profile/', views.current_user, name='current_user'),
    path('me/update-pseudo/', views.update_pseudo, name='update_pseudo'),

    
    # Routes admin
    path('all/', views.user_list, name='user-list'),
    path('<int:user_id>/detail/', views.user_detail, name='user-detail'),
]
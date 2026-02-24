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



from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crée un router mais exclue certaines méthodes
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

# URLs personnalisées
custom_urls = [
    path('current/', views.current_user, name='current_user'),
    path('update-pseudo/', views.update_pseudo, name='update_pseudo'),
    path('update-email/', views.update_email, name='update_email'),
    path('profile/', views.current_user, name='user_profile'),
]

# Combine les URLs
urlpatterns = custom_urls + router.urls
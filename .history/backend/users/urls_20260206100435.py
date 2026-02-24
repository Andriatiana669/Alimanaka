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

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    # ⚠️ IMPORTANT : Routes API simples EN PREMIER
    path('current/', views.current_user, name='current_user'),
    path('update-pseudo/', views.update_pseudo, name='update_pseudo'),
    path('profile/', views.current_user, name='user_profile'),  # Alias
    
    # Routes API ViewSet EN DERNIER
    path('', include(router.urls)),
]
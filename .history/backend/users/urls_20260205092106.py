from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # API pour les utilisateurs
    path('users/current/', views.current_user_view, name='current-user'),
    path('users/profile/', views.update_profile_view, name='update-profile'),
    
    # Gestion des utilisateurs (admin ou superuser)
    path('users/', views.user_list_view, name='user-list'),
    path('users/<int:user_id>/', views.user_detail_view, name='user-detail'),
    path('users/<int:user_id>/activate/', views.activate_user_view, name='activate-user'),
    path('users/<int:user_id>/deactivate/', views.deactivate_user_view, name='deactivate-user'),
    
    # Rôles et permissions
    path('users/<int:user_id>/roles/', views.user_roles_view, name='user-roles'),
    path('roles/', views.role_list_view, name='role-list'),
]
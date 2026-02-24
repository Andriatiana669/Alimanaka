from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    # OAuth2 Flow
    path('login/', views.sso_login_view, name='sso-login'),
    path('callback/', views.sso_callback_view, name='sso-callback'),
    
    # Web logout (redirection)
    path('logout/', views.logout_view, name='logout'),
    
    # API endpoints (pour le frontend)
    path('session/', views.session_status_view, name='session-status'),
    path('api/logout/', views.logout_api_view, name='api-logout'),
]
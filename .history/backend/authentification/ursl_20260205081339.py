from django.urls import path
from . import views

app_name = 'authentification'

urlpatterns = [
    path('login/', views.sso_login_view, name='sso-login'),
    path('callback/', views.sso_callback_view, name='sso-callback'),
    path('logout/', views.logout_view, name='logout'),
]
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from urllib.parse import urlencode
import uuid
import json
from django.contrib.auth.decorators import login_required

from .services import KeycloakService
from django.conf import settings

def sso_login_view(request):
    """Affiche la page de login SSO avec redirection automatique"""
    # Si l'utilisateur est déjà connecté, rediriger vers le dashboard
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    # Générer un state pour la sécurité
    state = str(uuid.uuid4())
    request.session['oauth_state'] = state
    
    # URL de redirection après login
    next_url = request.GET.get('next', '/dashboard/')
    request.session['next_url'] = next_url
    
    # URL de callback
    redirect_uri = request.build_absolute_uri(reverse('authentification:sso-callback'))
    
    # Générer l'URL Keycloak avec prompt=login pour forcer un nouveau login
    auth_url = KeycloakService.get_auth_url(redirect_uri, state)
    
    # Si on ne peut pas générer l'URL, afficher une erreur
    if not auth_url:
        return render(request, 'authentification/error.html', {
            'message': 'Impossible de se connecter au serveur d\'authentification'
        })
    
    # AJOUT CRITIQUE : Ajouter prompt=login pour forcer une nouvelle authentification
    # Cela empêche Keycloak de vous reconnecter automatiquement
    if '?' in auth_url:
        auth_url += '&prompt=login'
    else:
        auth_url += '?prompt=login'
    
    # Contexte pour le template
    context = {
        'auth_url': auth_url,
        'redirect_uri': redirect_uri,
        'state': state,
        'next_url': next_url,
    }
    
    return render(request, 'authentification/sso_login.html', context)

@csrf_exempt
def sso_callback_view(request):
    """Traite la réponse de Keycloak après authentification"""
    if request.method == 'GET':
        # Keycloak redirige ici avec un code
        code = request.GET.get('code')
        state = request.GET.get('state')
        error = request.GET.get('error')
        
        if error:
            return render(request, 'authentification/error.html', {
                'message': f'Erreur Keycloak: {error}'
            })
        
        if not code or not state:
            return render(request, 'authentification/error.html', {
                'message': 'Paramètres manquants dans la réponse'
            })
        
        # Vérifier le state (sécurité)
        if state != request.session.get('oauth_state'):
            return render(request, 'authentification/error.html', {
                'message': 'Erreur de sécurité: state invalide'
            })
        
        # URL de callback
        redirect_uri = request.build_absolute_uri(reverse('authentification:sso-callback'))
        
        # Échanger le code contre un token
        tokens = KeycloakService.exchange_code_for_token(code, redirect_uri)
        
        if not tokens or 'access_token' not in tokens:
            return render(request, 'authentification/error.html', {
                'message': 'Impossible d\'obtenir les tokens d\'accès'
            })
        
        # Authentifier l'utilisateur avec le token
        from django.contrib.auth import authenticate
        user = authenticate(request, access_token=tokens['access_token'])
        
        if user:
            # Connecter l'utilisateur
            login(request, user)
            
            # Stocker les tokens en session
            request.session['sso_access_token'] = tokens['access_token']
            if 'refresh_token' in tokens:
                request.session['sso_refresh_token'] = tokens['refresh_token']
            if 'id_token' in tokens:
                request.session['sso_id_token'] = tokens['id_token']  # Important pour logout
            
            # Rediriger vers la page demandée
            next_url = request.session.pop('next_url', '/dashboard/')
            return redirect(next_url)
        else:
            return render(request, 'authentification/error.html', {
                'message': 'Authentification échouée'
            })
    
    return render(request, 'authentification/error.html', {
        'message': 'Méthode non autorisée'
    })

def logout_view(request):
    """Déconnexion avec Single Logout vers Keycloak"""
    # Récupérer le token d'identité avant de nettoyer
    id_token = request.session.get('sso_id_token')
    access_token = request.session.get('sso_access_token')
    
    # Déconnecter de Django d'abord
    logout(request)
    
    # Nettoyer complètement la session
    request.session.flush()
    
    # AJOUT CRITIQUE : Nettoyer les cookies Django
    response = redirect(reverse('authentification:sso-login'))
    
    # Supprimer les cookies Django
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')
    
    # Supprimer les cookies Keycloak s'ils existent
    response.delete_cookie('KEYCLOAK_SESSION')
    response.delete_cookie('KEYCLOAK_IDENTITY')
    response.delete_cookie('AUTH_SESSION_ID')
    response.delete_cookie('KC_RESTART')
    
    # Single Logout vers Keycloak si nous avons l'id_token
    config = KeycloakService.get_oidc_config()
    if config and 'end_session_endpoint' in config and id_token:
        try:
            logout_url = config['end_session_endpoint']
            params = {
                'id_token_hint': id_token,
                'post_logout_redirect_uri': request.build_absolute_uri(reverse('authentification:sso-login'))
            }
            full_logout_url = f"{logout_url}?{urlencode(params)}"
            return redirect(full_logout_url)
        except Exception as e:
            print(f"Erreur Single Logout: {e}")
            # Continuer avec la redirection normale si erreur
    
    # Rediriger vers la page de login avec un paramètre pour forcer le prompt
    login_url = reverse('authentification:sso-login')
    return redirect(f"{login_url}?force_login=true")

def sso_error_view(request):
    """Page d'erreur SSO"""
    return render(request, 'authentification/error.html', {
        'message': request.GET.get('message', 'Une erreur est survenue')
    })


@login_required
def protected_test_view(request):
    """Page de test protégée par login_required"""
    return render(request, 'authentification/protected.html', {
        'user': request.user
    })
# backend/authentification/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from urllib.parse import urlencode
import uuid
import json
import time as import_time_time
from django.contrib.auth.decorators import login_required

from .services import KeycloakService

def get_frontend_url(path='/'):
    """Retourne l'URL complète du frontend"""
    base_url = settings.FRONTEND_URL.rstrip('/')
    return f"{base_url}{path}"

def sso_login_view(request):
    """Redirection vers Keycloak - pas de template intermédiaire"""
    
    print(f"🔍 SSO LOGIN - User: {request.user}, Authenticated: {request.user.is_authenticated}")
    print(f"   → Cookies reçus: {request.COOKIES}")
    
    # Si déjà connecté, rediriger vers le frontend
    if request.user.is_authenticated:
        print(f"   → Déjà auth, redirect frontend")
        return redirect(get_frontend_url('/dashboard'))
    
    # FORCER la création de la session si elle n'existe pas
    if not request.session.session_key:
        request.session.create()
        print(f"   → Nouvelle session créée: {request.session.session_key}")
    
    # IMPORTANT: Sauvegarder la session explicitement
    request.session.modified = True
    request.session.save()
    
    # Générer un state pour la sécurité
    state = str(uuid.uuid4())
    request.session['oauth_state'] = state
    request.session['state_timestamp'] = import_time_time.time()
    
    # URL de redirection finale après auth
    next_path = request.GET.get('next', '/dashboard')
    request.session['post_auth_redirect'] = next_path
    
    # SAUVEGARDER EXPLICITEMENT la session avant redirection
    request.session.save()
    
    print(f"   → State stocké: {state[:8]}...")
    print(f"   → Session key: {request.session.session_key}")
    print(f"   → Session après sauvegarde: {dict(request.session)}")
    
    # URL de callback (doit rester sur le backend pour traitement)
    redirect_uri = request.build_absolute_uri(reverse('authentification:sso-callback'))
    
    # Générer l'URL Keycloak
    auth_url = KeycloakService.get_auth_url(redirect_uri, state)
    
    if not auth_url:
        return JsonResponse({
            'error': 'Impossible de se connecter au serveur d\'authentification'
        }, status=503)
    
    # Forcer nouveau login si demandé
    if '?' in auth_url:
        auth_url += '&prompt=login'
    else:
        auth_url += '?prompt=login'
    
    # CRÉER LA RÉPONSE AVEC COOKIE FORCÉ
    response = redirect(auth_url)
    
    # FORCER LE COOKIE DE SESSION
    session_cookie_name = settings.SESSION_COOKIE_NAME
    session_key = request.session.session_key
    
    if session_key:
        # Supprimer l'ancien cookie s'il existe
        if session_cookie_name in request.COOKIES:
            response.delete_cookie(session_cookie_name)
        
        # Définir le nouveau cookie avec tous les paramètres
        response.set_cookie(
            session_cookie_name,
            session_key,
            max_age=settings.SESSION_COOKIE_AGE,
            expires=None,
            path='/',
            domain=settings.SESSION_COOKIE_DOMAIN,
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )
        
        print(f"   → Cookie session défini: {session_key[:8]}...")
        print(f"   → Paramètres cookie - domain: {settings.SESSION_COOKIE_DOMAIN}, secure: {settings.SESSION_COOKIE_SECURE}, samesite: {settings.SESSION_COOKIE_SAMESITE}")
    
    return response

@csrf_exempt
def sso_callback_view(request):
    """Callback Keycloak -> Création session -> Redirection Frontend"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    print(f"🔍 SSO CALLBACK - Code: {code[:20] if code else 'None'}..., State: {state[:8] if state else 'None'}...")
    print(f"   → Session key: {request.session.session_key}")
    print(f"   → Session data: {dict(request.session)}")
    print(f"   → Cookies reçus: {request.COOKIES}")
    
    if error:
        print(f"   → Erreur Keycloak: {error}")
        frontend_error_url = get_frontend_url(f'/auth/error?message={error}')
        return redirect(frontend_error_url)
    
    if not code or not state:
        print(f"   → Paramètres manquants")
        return redirect(get_frontend_url('/auth/error?message=Paramètres manquants'))
    
    # RÉCUPÉRER LE STATE STOCKÉ
    stored_state = request.session.get('oauth_state')
    print(f"   → Stored state: {stored_state[:8] if stored_state else 'None'}...")
    
    # SI PAS DE STATE EN SESSION, ESSAYER DE LE RÉCUPÉRER DES COOKIES
    if not stored_state:
        # Essayer de charger la session à partir du cookie
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        if session_key:
            print(f"   → Tentative de restauration session avec cookie: {session_key[:8]}...")
            from django.contrib.sessions.backends.db import SessionStore
            session = SessionStore(session_key=session_key)
            if session.exists(session_key):
                request.session = session
                stored_state = request.session.get('oauth_state')
                print(f"   → Session restaurée, stored_state: {stored_state[:8] if stored_state else 'None'}...")
    
    if state != stored_state:
        print(f"   → ❌ STATE MISMATCH!")
        print(f"   → State reçu: {state}")
        print(f"   → State stocké: {stored_state}")
        
        # OPTION: Accepter quand même en développement
        if settings.DEBUG:
            print("   → ✅ DEBUG mode: on ignore le state check")
        else:
            return redirect(get_frontend_url('/auth/error?message=State invalide'))
    
    # Échanger le code contre un token
    redirect_uri = request.build_absolute_uri(reverse('authentification:sso-callback'))
    tokens = KeycloakService.exchange_code_for_token(code, redirect_uri)
    
    if not tokens or 'access_token' not in tokens:
        print(f"   → Échec échange token")
        return redirect(get_frontend_url('/auth/error?message=Échec authentification'))
    
    # Authentifier l'utilisateur
    from django.contrib.auth import authenticate
    user = authenticate(request, access_token=tokens['access_token'])
    
    if not user:
        print(f"   → Utilisateur non reconnu")
        return redirect(get_frontend_url('/auth/error?message=Utilisateur non reconnu'))
    
    print(f"   → User authentifié: {user.username}")
    
    # Connecter et créer la session Django
    login(request, user)
    
    # Stocker tokens en session
    request.session['sso_access_token'] = tokens['access_token']
    if 'refresh_token' in tokens:
        request.session['sso_refresh_token'] = tokens['refresh_token']
    if 'id_token' in tokens:
        request.session['sso_id_token'] = tokens['id_token']
    
    # Nettoyer le state utilisé
    request.session.pop('oauth_state', None)
    request.session.pop('state_timestamp', None)
    
    # SAUVEGARDER FORCÉMENT
    request.session.save()
    
    # Rediriger vers le frontend
    redirect_path = request.session.pop('post_auth_redirect', '/dashboard')
    print(f"   → Redirect vers: {redirect_path}")
    
    # CRÉER LA RÉPONSE AVEC COOKIE
    response = redirect(get_frontend_url(f'{redirect_path}?auth=success'))
    
    # S'assurer que le cookie de session est bien défini
    session_key = request.session.session_key
    if session_key:
        response.set_cookie(
            settings.SESSION_COOKIE_NAME,
            session_key,
            max_age=settings.SESSION_COOKIE_AGE,
            path='/',
            domain=settings.SESSION_COOKIE_DOMAIN,
            secure=settings.SESSION_COOKIE_SECURE,
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            samesite=settings.SESSION_COOKIE_SAMESITE,
        )
        print(f"   → Cookie session renouvelé: {session_key[:8]}...")
    
    return response

def logout_view(request):
    """Déconnexion SSO complète"""
    id_token = request.session.get('sso_id_token')
    
    # Déconnecter de Django
    logout(request)
    request.session.flush()
    
    # Préparer la réponse de redirection vers le frontend
    frontend_login = get_frontend_url('/login')
    
    # Single Logout Keycloak si id_token disponible
    config = KeycloakService.get_oidc_config()
    if config and 'end_session_endpoint' in config and id_token:
        try:
            logout_url = config['end_session_endpoint']
            params = {
                'id_token_hint': id_token,
                'post_logout_redirect_uri': frontend_login
            }
            full_logout_url = f"{logout_url}?{urlencode(params)}"
            return redirect(full_logout_url)
        except Exception as e:
            print(f"Erreur SLO: {e}")
    
    return redirect(frontend_login)

# ============================================================================
# API ENDPOINTS (pour le frontend)
# ============================================================================

@login_required
def session_status_view(request):
    """API: Vérifier si la session est valide"""
    print(f"✅ SESSION CHECK - User: {request.user.username}")
    return JsonResponse({
        'authenticated': True,
        'user': {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'pseudo': request.user.pseudo,
            'display_name': request.user.get_display_name(),
        }
    })

@login_required
def logout_api_view(request):
    """API: Déconnexion depuis le frontend (AJAX)"""
    id_token = request.session.get('sso_id_token')
    logout(request)
    request.session.flush()
    
    # Retourner l'URL de logout Keycloak pour redirection frontend
    config = KeycloakService.get_oidc_config()
    logout_url = None
    if config and 'end_session_endpoint' in config and id_token:
        params = {
            'id_token_hint': id_token,
            'post_logout_redirect_uri': get_frontend_url('/login')
        }
        logout_url = f"{config['end_session_endpoint']}?{urlencode(params)}"
    
    return JsonResponse({
        'success': True,
        'redirect_url': logout_url or get_frontend_url('/login')
    })

# ============================================================================
# VUE D'ERREUR POUR LE BACKEND (si besoin)
# ============================================================================

def error_view(request):
    """Page d'erreur d'authentification"""
    message = request.GET.get('message', 'Erreur inconnue')
    return render(request, 'authentification/error.html', {
        'message': message,
        'frontend_url': get_frontend_url('/login')
    })
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
import json

@login_required
def current_user_view(request):
    """Retourne les informations de l'utilisateur courant"""
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'groups': list(user.groups.values_list('name', flat=True)),
        'permissions': list(user.get_all_permissions()),
    }
    return JsonResponse(data)

@csrf_exempt
@login_required
def update_profile_view(request):
    """Met à jour le profil de l'utilisateur courant"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user
        
        # Mettre à jour les champs autorisés
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data and data['email'] != user.email:
            # Vérifier si l'email n'est pas déjà utilisé
            if not User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                user.email = data['email']
            else:
                return JsonResponse({'error': 'Cet email est déjà utilisé'}, status=400)
        
        user.save()
        return JsonResponse({'message': 'Profil mis à jour avec succès'})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_list_view(request):
    """Liste tous les utilisateurs (admin seulement)"""
    users = User.objects.all().order_by('-date_joined')
    user_list = []
    
    for user in users:
        user_list.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'groups': list(user.groups.values_list('name', flat=True)),
        })
    
    return JsonResponse({'users': user_list})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_detail_view(request, user_id):
    """Détails d'un utilisateur spécifique (admin seulement)"""
    user = get_object_or_404(User, id=user_id)
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'groups': list(user.groups.values_list('name', flat=True)),
    }
    
    return JsonResponse(data)

@csrf_exempt
@login_required
@permission_required('auth.change_user', raise_exception=True)
def activate_user_view(request, user_id):
    """Active un utilisateur (admin seulement)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    
    return JsonResponse({'message': f'Utilisateur {user.username} activé'})

@csrf_exempt
@login_required
@permission_required('auth.change_user', raise_exception=True)
def deactivate_user_view(request, user_id):
    """Désactive un utilisateur (admin seulement)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    
    return JsonResponse({'message': f'Utilisateur {user.username} désactivé'})

@login_required
@permission_required('auth.view_user', raise_exception=True)
def user_roles_view(request, user_id):
    """Récupère les rôles d'un utilisateur (admin seulement)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'GET':
        groups = user.groups.all()
        group_list = [{'id': g.id, 'name': g.name} for g in groups]
        return JsonResponse({'groups': group_list})
    
    elif request.method == 'POST':
        # Ajouter/supprimer des rôles
        try:
            data = json.loads(request.body)
            action = data.get('action')  # 'add' ou 'remove'
            group_id = data.get('group_id')
            
            if not action or not group_id:
                return JsonResponse({'error': 'Paramètres manquants'}, status=400)
            
            group = get_object_or_404(Group, id=group_id)
            
            if action == 'add':
                user.groups.add(group)
                return JsonResponse({'message': f'Rôle {group.name} ajouté'})
            elif action == 'remove':
                user.groups.remove(group)
                return JsonResponse({'message': f'Rôle {group.name} retiré'})
            else:
                return JsonResponse({'error': 'Action invalide'}, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données JSON invalides'}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

@login_required
@permission_required('auth.view_group', raise_exception=True)
def role_list_view(request):
    """Liste tous les groupes/roles disponibles (admin seulement)"""
    groups = Group.objects.all().order_by('name')
    group_list = []
    
    for group in groups:
        group_list.append({
            'id': group.id,
            'name': group.name,
            'user_count': group.user_set.count(),
        })
    
    return JsonResponse({'roles': group_list})
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Q
import json

from .models import User, Pole, Equipe
from .serializers import (
    UserSerializer, UserProfileSerializer, UserListSerializer,
    PoleSerializer, EquipeSerializer, EquipeTreeSerializer
)


# ============================================================================
# VIEWS POUR LES PÔLES
# ============================================================================

class PoleViewSet(viewsets.ModelViewSet):
    """CRUD pour les pôles (admin uniquement pour écriture)"""
    queryset = Pole.objects.filter(est_actif=True)
    serializer_class = PoleSerializer
    lookup_field = 'pk'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def actifs(self, request):
        """Liste tous les pôles actifs"""
        poles = self.get_queryset()
        serializer = self.get_serializer(poles, many=True)
        return Response(serializer.data)


# ============================================================================
# VIEWS POUR LES ÉQUIPES (avec hiérarchie)
# ============================================================================

class EquipeViewSet(viewsets.ModelViewSet):
    """CRUD pour les équipes avec gestion hiérarchique"""
    queryset = Equipe.objects.filter(est_actif=True)
    serializer_class = EquipeSerializer
    lookup_field = 'pk'
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'arbre', 'membres']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        """Filtre selon les permissions"""
        user = self.request.user
        
        # Admin voit tout
        if user.is_staff or user.is_superuser:
            return Equipe.objects.filter(est_actif=True)
        
        # Chef d'équipe voit son équipe et sous-équipes
        if user.equipes_gerees.exists():
            equipes_ids = [eq.id for eq in user.sous_equipes_accessibles]
            return Equipe.objects.filter(id__in=equipes_ids, est_actif=True)
        
        # Utilisateur normal voit juste son équipe
        if user.equipe:
            return Equipe.objects.filter(id=user.equipe.id)
        
        return Equipe.objects.none()
    
    @action(detail=False, methods=['get'])
    def arbre(self, request):
        """Retourne l'arborescence complète des équipes"""
        # Racines : équipes sans parent
        racines = Equipe.objects.filter(equipe_parente__isnull=True, est_actif=True)
        serializer = EquipeTreeSerializer(racines, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def membres(self, request, pk=None):
        """Liste les membres d'une équipe"""
        equipe = self.get_object()
        
        # Vérifier les permissions
        user = request.user
        if not (user.is_staff or user.is_superuser or 
                equipe.manager == user or 
                user.equipe == equipe):
            return Response({'error': 'Permission refusée'}, status=403)
        
        membres = equipe.membres.filter(is_active=True)
        serializer = UserListSerializer(membres, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def changer_manager(self, request, pk=None):
        """Change le manager d'une équipe (admin ou manager actuel)"""
        equipe = self.get_object()
        user = request.user
        
        if not (user.is_staff or user.is_superuser or equipe.manager == user):
            return Response({'error': 'Permission refusée'}, status=403)
        
        nouveau_manager_id = request.data.get('manager_id')
        if not nouveau_manager_id:
            return Response({'error': 'manager_id requis'}, status=400)
        
        try:
            nouveau_manager = User.objects.get(id=nouveau_manager_id)
            equipe.manager = nouveau_manager
            equipe.save()
            
            # Mettre à jour l'équipe du nouveau manager si nécessaire
            if not nouveau_manager.equipe:
                nouveau_manager.equipe = equipe
                nouveau_manager.save()
            
            return Response({'success': True, 'message': 'Manager mis à jour'})
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)


# ============================================================================
# VIEWS POUR LES UTILISATEURS
# ============================================================================

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des utilisateurs"""
    queryset = User.objects.all().order_by('last_name', 'first_name')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre le queryset selon les permissions"""
        user = self.request.user
        
        # Admin voit tout
        if user.is_staff or user.is_superuser:
            return User.objects.all().order_by('last_name', 'first_name')
        
        # Chef d'équipe voit les membres de ses équipes
        if user.equipes_gerees.exists():
            equipes_accessibles = user.sous_equipes_accessibles
            return User.objects.filter(
                Q(equipe__in=equipes_accessibles) | Q(id=user.id)
            ).distinct().order_by('last_name', 'first_name')
        
        # Utilisateur normal voit seulement son profil
        return User.objects.filter(id=user.id)
    
    def get_serializer_class(self):
        if self.action == 'list' and not self.request.user.is_staff:
            return UserListSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Récupère le profil de l'utilisateur connecté"""
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Met à jour le profil de l'utilisateur connecté"""
        user = request.user
        serializer = UserProfileSerializer(
            user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            # Empêcher la modification des champs SSO et organisation par l'utilisateur
            data = serializer.validated_data.copy()
            
            # Champs non modifiables par l'utilisateur lui-même
            protected_fields = [
                'username', 'first_name', 'last_name', 'email', 
                'keycloak_id', 'pole', 'equipe'
            ]
            for field in protected_fields:
                if field in data:
                    del data[field]
            
            # Mettre à jour seulement les champs autorisés
            for attr, value in data.items():
                setattr(user, attr, value)
            
            user.save()
            return Response(UserProfileSerializer(user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def update_pole_equipe(self, request):
        """Met à jour le pôle et l'équipe (admin uniquement)"""
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'error': 'Permission refusée'}, status=403)
        
        user_id = request.data.get('user_id')
        pole_id = request.data.get('pole_id')
        equipe_id = request.data.get('equipe_id')
        
        try:
            target_user = User.objects.get(id=user_id)
            
            if pole_id is not None:
                if pole_id == 0:  # 0 = retirer le pôle
                    target_user.pole = None
                else:
                    target_user.pole = Pole.objects.get(id=pole_id)
            
            if equipe_id is not None:
                if equipe_id == 0:  # 0 = retirer l'équipe
                    target_user.equipe = None
                else:
                    target_user.equipe = Equipe.objects.get(id=equipe_id)
            
            target_user.save()
            return Response({
                'success': True,
                'message': 'Pôle et équipe mis à jour',
                'user': UserSerializer(target_user).data
            })
            
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)
        except (Pole.DoesNotExist, Equipe.DoesNotExist):
            return Response({'error': 'Pôle ou équipe non trouvé'}, status=404)


    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            # Permettre à un user de modifier son propre profil ?
            return [IsAuthenticated()]
        return super().get_permissions()
    
    
# ============================================================================
# VUES API SIMPLES (pour compatibilité)
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Récupère les informations de l'utilisateur actuel"""
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'pseudo': user.pseudo,
        'pseudo_format': user.pseudo_format,
        'email': user.email,
        'full_name': user.get_full_name(),
        'display_name': user.get_display_name(),
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        # Nouveaux champs
        'pole': {
            'id': user.pole.id,
            'code': user.pole.code,
            'nom': user.pole.nom
        } if user.pole else None,
        'equipe': {
            'id': user.equipe.id,
            'nom': user.equipe.nom,
            'manager_id': user.equipe.manager_id
        } if user.equipe else None,
        'est_chef_equipe': user.est_chef_equipe,
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list(request):
    """Liste des utilisateurs"""
    user = request.user
    
    # Filtre selon permissions
    if user.is_staff or user.is_superuser:
        users = User.objects.all().order_by('last_name', 'first_name')
        serializer = UserSerializer(users, many=True)
    elif user.equipes_gerees.exists():
        # Chef d'équipe : voit membres de ses équipes
        equipes = user.sous_equipes_accessibles
        users = User.objects.filter(
            Q(equipe__in=equipes) | Q(id=user.id)
        ).distinct().order_by('last_name', 'first_name')
        serializer = UserListSerializer(users, many=True)
    else:
        # Utilisateur normal : ne se voit que lui-même
        serializer = UserListSerializer([user], many=True)
    
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_pseudo(request):
    """Met à jour le pseudo OU le format du pseudo"""
    user = request.user
    
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        # Option 1: Mettre à jour le format
        if 'pseudo_format' in data:
            new_format = data.get('pseudo_format', '').strip()
            
            valid_formats = [choice[0] for choice in User.pseudo_format_choices]
            if new_format not in valid_formats:
                return Response(
                    {'error': 'Format de pseudo invalide'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.pseudo_format = new_format
            
            if new_format != 'custom':
                user.pseudo = user.get_display_name()
            elif 'pseudo' not in data:
                pass
            
            user.save()
            
            return Response({
                'success': True,
                'message': 'Format de pseudo mis à jour',
                'pseudo_format': user.pseudo_format,
                'pseudo': user.pseudo,
                'display_name': user.get_display_name()
            })
        
        # Option 2: Mettre à jour le pseudo personnalisé
        elif 'pseudo' in data:
            pseudo = data.get('pseudo', '').strip()
            
            if not pseudo:
                return Response(
                    {'error': 'Le pseudo ne peut pas être vide'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(pseudo) > 100:
                return Response(
                    {'error': 'Le pseudo ne peut pas dépasser 100 caractères'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.pseudo = pseudo
            user.pseudo_format = 'custom'
            user.save()
            
            return Response({
                'success': True,
                'message': 'Pseudo personnalisé mis à jour',
                'pseudo': user.pseudo,
                'pseudo_format': user.pseudo_format,
                'display_name': user.get_display_name()
            })
        
        else:
            return Response(
                {'error': 'Données manquantes: fournissez pseudo ou pseudo_format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Données JSON invalides'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
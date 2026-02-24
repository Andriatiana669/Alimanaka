from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer, UserProfileSerializer
import json

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des utilisateurs"""
    queryset = User.objects.all().order_by('last_name', 'first_name')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtre le queryset selon les permissions"""
        user = self.request.user
        
        # Si l'utilisateur est admin, voir tous les utilisateurs
        if user.is_superuser or user.is_staff:
            return User.objects.all()
        
        # Sinon, seulement son propre profil
        return User.objects.filter(id=user.id)
    
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
            partial=True if request.method == 'PATCH' else False
        )
        
        if serializer.is_valid():
            # Empêcher la modification des champs SSO
            data = serializer.validated_data.copy()
            
            # Champs non modifiables via SSO
            protected_fields = ['username', 'first_name', 'last_name', 'email', 'keycloak_id']
            for field in protected_fields:
                if field in data:
                    del data[field]
            
            # Mettre à jour seulement les champs autorisés
            for attr, value in data.items():
                setattr(user, attr, value)
            
            user.save()
            return Response(UserProfileSerializer(user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Récupère les informations de l'utilisateur actuel"""
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,  # Matricule
        'first_name': user.first_name,  # Nom
        'last_name': user.last_name,  # Prénom
        'pseudo': user.pseudo,
        'email': user.email,
        'full_name': user.get_full_name(),
        'display_name': user.get_display_name(),
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_pseudo(request):
    user = request.user
    data = json.loads(request.body)
    
    if 'pseudo' in data:
        # Mettre à jour le pseudo personnalisé
        user.pseudo = data['pseudo']
        user.pseudo_format = 'custom'
    elif 'pseudo_format' in data:
        # Mettre à jour le format
        user.pseudo_format = data['pseudo_format']
        # Générer le pseudo automatiquement si pas custom
        if data['pseudo_format'] != 'custom':
            user.pseudo = user.get_display_name()
    
    user.save()
    
    return Response({
        'success': True,
        'pseudo': user.pseudo,
        'pseudo_format': user.pseudo_format,
        'display_name': user.get_display_name()
    })
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date

from .models import ReposMedical
from .serializers import (
    ReposMedicalSerializer, ReposMedicalCreateSerializer,
    ReposMedicalValidationSerializer, ReposMedicalTransformationSerializer,
    ReposMedicalAnnulationSerializer
)
from conges.models import TypeCongeConfig


class ReposMedicalViewSet(viewsets.ModelViewSet):
    """Gestion des repos médicaux"""
    serializer_class = ReposMedicalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin voit tout
        if user.is_staff or user.is_superuser:
            return ReposMedical.objects.all().select_related('utilisateur', 'conge_genere')
        
        # Manager voit les repos médicaux de son équipe
        if hasattr(user, 'equipes_gerees') and user.equipes_gerees.exists():
            equipes = set()
            for eq in user.equipes_gerees.all():
                equipes.add(eq.id)
                for sous in eq.sous_equipes.all():
                    equipes.add(sous.id)
                    for sous_sous in sous.sous_equipes.all():
                        equipes.add(sous_sous.id)
            
            for eq in user.equipes_co_gerees.all():
                equipes.add(eq.id)
                for sous in eq.sous_equipes.all():
                    equipes.add(sous.id)
                    for sous_sous in sous.sous_equipes.all():
                        equipes.add(sous_sous.id)
            
            return ReposMedical.objects.filter(
                utilisateur__equipe_id__in=equipes
            ).select_related('utilisateur', 'conge_genere')
        
        # Utilisateur normal voit ses repos médicaux
        return ReposMedical.objects.filter(utilisateur=user).select_related('utilisateur', 'conge_genere')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReposMedicalCreateSerializer
        return ReposMedicalSerializer
    
    def perform_create(self, serializer):
        """Crée un repos médical pour l'utilisateur spécifié"""
        user = self.request.user
        data = self.request.data
        
        # user_id est obligatoire (seul un manager peut créer)
        target_user_id = data.get('user_id')
        if not target_user_id:
            raise serializers.ValidationError({'user_id': "L'utilisateur est requis"})
        
        if not self._can_manage_user(user, target_user_id):
            raise serializers.ValidationError({'user_id': "Vous ne pouvez pas gérer cet utilisateur"})
        
        from users.models import User
        target_user = User.objects.get(id=target_user_id)
        
        serializer.save(utilisateur=target_user)
    
    def _can_manage_user(self, manager, target_user_id):
        """Vérifie si le manager peut gérer l'utilisateur cible"""
        if manager.is_superuser:
            return True
        
        from users.models import User
        try:
            target = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return False
        
        # Vérifier si dans les équipes gérées
        equipes_manager = set()
        for eq in manager.equipes_gerees.all():
            equipes_manager.add(eq.id)
            for sous in eq.sous_equipes.all():
                equipes_manager.add(sous.id)
        
        for eq in manager.equipes_co_gerees.all():
            equipes_manager.add(eq.id)
            for sous in eq.sous_equipes.all():
                equipes_manager.add(sous.id)
        
        return target.equipe_id in equipes_manager
    
    @action(detail=False, methods=['get'])
    def mes_repos(self, request):
        """Liste les repos médicaux de l'utilisateur connecté avec filtres"""
        queryset = ReposMedical.objects.filter(utilisateur=request.user)
        
        # Filtre par année
        annee = request.query_params.get('annee')
        if annee:
            queryset = queryset.filter(date__year=annee)
        
        # Filtre par statut
        statut = request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendrier(self, request):
        """Retourne les événements pour le calendrier"""
        annee = int(request.query_params.get('annee', datetime.now().year))
        statut_filter = request.query_params.get('statut')
        
        events = []
        
        # Récupérer les repos médicaux selon les permissions
        repos_queryset = self.get_queryset().filter(date__year=annee)
        
        if statut_filter:
            repos_queryset = repos_queryset.filter(statut=statut_filter)
        
        for repos in repos_queryset:
            events.append(repos.to_calendar_event())
        
        return Response(events)
    
    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Valider directement un repos médical"""
        repos_medical = self.get_object()
        
        if repos_medical.statut != 'en_attente':
            return Response(
                {'error': 'Ce repos médical ne peut pas être validé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        repos_medical.valider(user=request.user)
        
        return Response({
            'success': True,
            'message': 'Repos médical validé avec succès',
            'statut': repos_medical.statut
        })
    
    @action(detail=True, methods=['post'])
    def transformer_en_conge(self, request, pk=None):
        """Transformer le repos médical en congé"""
        repos_medical = self.get_object()
        
        if repos_medical.statut != 'en_attente':
            return Response(
                {'error': 'Seuls les repos médicaux en attente peuvent être transformés en congé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReposMedicalTransformationSerializer(data=request.data)
        if serializer.is_valid():
            # Vérifier que le type de congé existe
            try:
                type_conge = serializer.validated_data['type_conge']
                TypeCongeConfig.objects.get(type_conge=type_conge)
            except TypeCongeConfig.DoesNotExist:
                return Response(
                    {'error': 'Type de congé invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            conge = repos_medical.transformer_en_conge(
                type_conge=type_conge,
                user=request.user
            )
            
            return Response({
                'success': True,
                'message': 'Repos médical transformé en congé avec succès',
                'conge_id': conge.id,
                'statut': repos_medical.statut
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annuler un repos médical"""
        repos_medical = self.get_object()
        user = request.user
        
        # Vérifier les permissions
        if not user.is_staff and not self._can_manage_user(user, repos_medical.utilisateur.id):
            return Response({'error': 'Permission refusée'}, status=403)
        
        if repos_medical.statut == 'annule':
            return Response({'error': 'Déjà annulé'}, status=400)
        
        if repos_medical.statut not in ['en_attente']:
            return Response(
                {'error': 'Ce repos médical ne peut pas être annulé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReposMedicalAnnulationSerializer(data=request.data)
        if serializer.is_valid():
            commentaire = serializer.validated_data.get('commentaire', '')
            
            repos_medical.annuler(user=user, commentaire=commentaire)
            
            return Response({
                'success': True,
                'message': 'Repos médical annulé',
                'annule_par': user.get_display_name(),
                'date_annulation': repos_medical.date_annulation
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def utilisateurs_gerables(self, request):
        """Liste les utilisateurs pour lesquels le manager peut créer des repos médicaux"""
        from users.models import User
        
        user = request.user
        
        if user.is_superuser:
            users = User.objects.filter(is_active=True)
        elif user.is_staff:
            equipes = set()
            for eq in user.equipes_gerees.all():
                equipes.add(eq.id)
                for sous in eq.sous_equipes.all():
                    equipes.add(sous.id)
                    for sous_sous in sous.sous_equipes.all():
                        equipes.add(sous_sous.id)
            
            for eq in user.equipes_co_gerees.all():
                equipes.add(eq.id)
                for sous in eq.sous_equipes.all():
                    equipes.add(sous.id)
                    for sous_sous in sous.sous_equipes.all():
                        equipes.add(sous_sous.id)
            
            users = User.objects.filter(
                Q(equipe_id__in=equipes) | Q(id=user.id),
                is_active=True
            ).distinct()
        else:
            users = User.objects.filter(id=user.id)
        
        data = [{
            'id': u.id,
            'display_name': u.get_display_name(),
            'username': u.username,
            'equipe_nom': u.equipe.nom if u.equipe else '',
        } for u in users]
        
        return Response(data)
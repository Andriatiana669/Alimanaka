from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal

from .models import Permission
from .serializers import (
    PermissionSerializer, PermissionCreateSerializer,
    PermissionRetourSerializer, PermissionRattrapageSerializer,
    PermissionTransformationSerializer, PermissionAnnulationSerializer
)
from conges.models import TypeCongeConfig


class PermissionViewSet(viewsets.ModelViewSet):
    """Gestion des permissions"""
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin voit tout
        if user.is_staff or user.is_superuser:
            return Permission.objects.all().select_related('utilisateur', 'conge_genere')
        
        # Manager voit les permissions de son équipe
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
            
            return Permission.objects.filter(
                utilisateur__equipe_id__in=equipes
            ).select_related('utilisateur', 'conge_genere')
        
        # Utilisateur normal voit ses permissions
        return Permission.objects.filter(utilisateur=user).select_related('utilisateur', 'conge_genere')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PermissionCreateSerializer
        return PermissionSerializer
    
    def perform_create(self, serializer):
        """Crée une permission pour l'utilisateur spécifié ou l'utilisateur connecté"""
        user = self.request.user
        data = self.request.data
        
        # Si user_id fourni et que l'utilisateur peut gérer d'autres
        target_user_id = data.get('user_id')
        if target_user_id and self._can_manage_user(user, target_user_id):
            from users.models import User
            target_user = User.objects.get(id=target_user_id)
        else:
            target_user = user
        
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
    def mes_permissions(self, request):
        """Liste les permissions de l'utilisateur connecté avec filtres"""
        queryset = Permission.objects.filter(utilisateur=request.user)
        
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
        
        # Récupérer les permissions selon les permissions
        perm_queryset = self.get_queryset().filter(date__year=annee)
        
        if statut_filter:
            perm_queryset = perm_queryset.filter(statut=statut_filter)
        
        for perm in perm_queryset:
            events.append(perm.to_calendar_event())
        
        return Response(events)
    
    @action(detail=True, methods=['post'])
    def retour(self, request, pk=None):
        """Enregistrer le retour de permission (bouton 'De retour')"""
        permission = self.get_object()
        
        if permission.statut != 'en_attente':
            return Response(
                {'error': 'Cette permission n\'est pas en attente de retour'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if permission.date > date.today():
            return Response(
                {'error': 'La date de permission n\'est pas encore arrivée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PermissionRetourSerializer(data=request.data)
        if serializer.is_valid():
            heures_a_rattraper = permission.enregistrer_retour(
                serializer.validated_data['heure_arrivee_reelle']
            )
            
            return Response({
                'success': True,
                'message': 'Retour enregistré avec succès',
                'statut': permission.statut,
                'heures_a_rattraper': float(heures_a_rattraper),
                'minutes_depassement': permission.minutes_depassement
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def ajouter_rattrapage(self, request, pk=None):
        """Ajouter une session de rattrapage"""
        permission = self.get_object()
        
        if permission.statut not in ['retourne', 'rattrapage']:
            return Response(
                {'error': 'Cette permission n\'est pas en état de rattrapage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if permission.heures_restantes <= 0:
            return Response(
                {'error': 'Il n\'y a plus d\'heures à rattraper'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PermissionRattrapageSerializer(data=request.data)
        if serializer.is_valid():
            heures = permission.ajouter_rattrapage(
                date_rattrapage=serializer.validated_data['date_rattrapage'],
                heure_debut=serializer.validated_data['heure_debut'],
                heure_fin=serializer.validated_data['heure_fin'],
                commentaire=serializer.validated_data.get('commentaire', ''),
                user=request.user
            )
            
            return Response({
                'success': True,
                'message': 'Rattrapage ajouté avec succès',
                'heures_rattrapees': float(heures),
                'heures_restantes': float(permission.heures_restantes),
                'statut': permission.statut,
                'rattrapages': permission.rattrapages
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def transformer_en_conge(self, request, pk=None):
        """Transformer la permission en congé"""
        permission = self.get_object()
        
        if permission.statut != 'retourne':
            return Response(
                {'error': 'Seules les permissions retournées peuvent être transformées en congé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if permission.minutes_depassement <= 0:
            return Response(
                {'error': 'Cette permission n\'a pas de dépassement à transformer en congé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PermissionTransformationSerializer(data=request.data)
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
            
            conge = permission.transformer_en_conge(
                type_conge=type_conge,
                user=request.user
            )
            
            return Response({
                'success': True,
                'message': 'Permission transformée en congé avec succès',
                'conge_id': conge.id,
                'statut': permission.statut
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annuler une permission"""
        permission = self.get_object()
        user = request.user
        
        # Vérifier les permissions
        if permission.utilisateur != user and not user.is_staff and not self._can_manage_user(user, permission.utilisateur.id):
            return Response({'error': 'Permission refusée'}, status=403)
        
        if permission.statut == 'annule':
            return Response({'error': 'Déjà annulé'}, status=400)
        
        serializer = PermissionAnnulationSerializer(data=request.data)
        if serializer.is_valid():
            commentaire = serializer.validated_data.get('commentaire', '')
            
            permission.statut = 'annule'
            permission.annule_par = user
            permission.date_annulation = timezone.now()
            permission.commentaire_annulation = commentaire
            permission.save()
            
            return Response({
                'success': True,
                'message': 'Permission annulée',
                'annule_par': user.get_display_name(),
                'date_annulation': permission.date_annulation
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def utilisateurs_gerables(self, request):
        """Liste les utilisateurs pour lesquels le manager peut créer des permissions"""
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
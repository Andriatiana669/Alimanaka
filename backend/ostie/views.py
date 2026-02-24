from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, date

from .models import Ostie
from .serializers import (
    OstieSerializer, OstieCreateSerializer,
    OstieValidationSerializer, OstieTransformationSerializer,
    OstieAnnulationSerializer
)


class OstieViewSet(viewsets.ModelViewSet):
    """Gestion des OSTIES"""
    serializer_class = OstieSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin voit tout
        if user.is_staff or user.is_superuser:
            return Ostie.objects.all().select_related('utilisateur', 'repos_genere')
        
        # Manager voit les OSTIES de son équipe
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
            
            return Ostie.objects.filter(
                utilisateur__equipe_id__in=equipes
            ).select_related('utilisateur', 'repos_genere')
        
        # Utilisateur normal voit ses OSTIES
        return Ostie.objects.filter(utilisateur=user).select_related('utilisateur', 'repos_genere')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OstieCreateSerializer
        return OstieSerializer
    
    def perform_create(self, serializer):
        """Crée un OSTIE pour l'utilisateur spécifié"""
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
    def mes_osties(self, request):
        """Liste les OSTIES de l'utilisateur connecté avec filtres"""
        queryset = Ostie.objects.filter(utilisateur=request.user)
        
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
        
        # Récupérer les OSTIES selon les permissions
        osties_queryset = self.get_queryset().filter(date__year=annee)
        
        if statut_filter:
            osties_queryset = osties_queryset.filter(statut=statut_filter)
        
        for ostie in osties_queryset:
            events.append(ostie.to_calendar_event())
            
        # 2. AJOUTER les jours fériés (du module conges)
        from conges.models import JourFerie
        jours_feries = JourFerie.objects.filter(est_actif=True)
        for jf in jours_feries:
            try:
                date_jf = datetime(annee, jf.mois, jf.jour).date()
                events.append({
                    'id': f"ferie_{jf.id}",
                    'title': f"🎉 {jf.nom}",
                    'start': date_jf.isoformat(),
                    'allDay': True,
                    'color': '#ffeb3b',
                    'type': 'ferie',
                    'isBlocked': True
                })
            except ValueError:
                continue
        
        # 3. AJOUTER les jours exceptionnels
        from conges.models import JourExceptionnel
        jours_exc = JourExceptionnel.objects.filter(annee=annee)
        for je in jours_exc:
            events.append({
                'id': f"exc_{je.id}",
                'title': f"⛔ {je.description or 'Exceptionnel'}",
                'start': je.date.isoformat(),
                'allDay': True,
                'color': '#ff5722' if je.type_jour == 'exceptionnel' else '#4caf50',
                'type': 'exceptionnel',
                'isBlocked': je.type_jour == 'exceptionnel'
            })
        
        # 4. AJOUTER les weekends (en dernier)
        from datetime import timedelta
        current = datetime(annee, 1, 1).date()
        while current.year == annee:
            if current.weekday() >= 5:  # Samedi ou Dimanche
                events.append({
                    'id': f"weekend_{current.isoformat()}",
                    'title': "📅 Weekend",
                    'start': current.isoformat(),
                    'allDay': True,
                    'color': '#e0e0e0',
                    'type': 'weekend',
                    'isBlocked': True
                })
            current += timedelta(days=1)
        
        return Response(events)
    
    @action(detail=True, methods=['post'])
    def valider(self, request, pk=None):
        """Valider directement un OSTIE"""
        ostie = self.get_object()
        
        if ostie.statut != 'en_attente':
            return Response(
                {'error': 'Cet OSTIE ne peut pas être validé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OstieValidationSerializer(data=request.data)
        if serializer.is_valid():
            heure_fin = serializer.validated_data['heure_fin']
            
            ostie.valider(heure_fin=heure_fin, user=request.user)
            
            return Response({
                'success': True,
                'message': 'OSTIE validé avec succès',
                'statut': ostie.statut,
                'heure_fin': str(ostie.heure_fin)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def transformer_en_repos(self, request, pk=None):
        """Transformer l'OSTIE en repos médical"""
        ostie = self.get_object()
        
        if ostie.statut != 'en_attente':
            return Response(
                {'error': 'Seuls les OSTIES en attente peuvent être transformés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OstieTransformationSerializer(data=request.data)
        if serializer.is_valid():
            heure_fin_ostie = serializer.validated_data['heure_fin_ostie']
            heure_fin_repos = serializer.validated_data['heure_fin_repos']
            
            repos = ostie.transformer_en_repos_medical(
                heure_fin_ostie=heure_fin_ostie,
                heure_fin_repos=heure_fin_repos,
                user=request.user
            )
            
            return Response({
                'success': True,
                'message': 'OSTIE transformé en repos médical avec succès',
                'statut': ostie.statut,
                'repos_id': repos.id,
                'repos_statut': repos.statut
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annuler un OSTIE"""
        ostie = self.get_object()
        user = request.user
        
        # Vérifier les permissions
        if not user.is_staff and not self._can_manage_user(user, ostie.utilisateur.id):
            return Response({'error': 'Permission refusée'}, status=403)
        
        if ostie.statut == 'annule':
            return Response({'error': 'Déjà annulé'}, status=400)
        
        if ostie.statut not in ['en_attente']:
            return Response(
                {'error': 'Cet OSTIE ne peut pas être annulé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OstieAnnulationSerializer(data=request.data)
        if serializer.is_valid():
            commentaire = serializer.validated_data.get('commentaire', '')
            
            ostie.annuler(user=user, commentaire=commentaire)
            
            return Response({
                'success': True,
                'message': 'OSTIE annulé',
                'annule_par': user.get_display_name(),
                'date_annulation': ostie.date_annulation
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def utilisateurs_gerables(self, request):
        """Liste les utilisateurs pour lesquels le manager peut créer des OSTIES"""
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
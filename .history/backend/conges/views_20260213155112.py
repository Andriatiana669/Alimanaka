from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime

from .models import TypeCongeConfig, JourFerie, JourExceptionnel, CongeAnnuel, Conge
from .serializers import (
    TypeCongeConfigSerializer, JourFerieSerializer,
    JourExceptionnelSerializer, CongeAnnuelSerializer,
    CongeSerializer, CongeCreateSerializer
)


class TypeCongeConfigViewSet(viewsets.ReadOnlyModelViewSet):
    """Configuration des types de congés (lecture seule pour les utilisateurs)"""
    queryset = TypeCongeConfig.objects.all()
    serializer_class = TypeCongeConfigSerializer
    permission_classes = [permissions.IsAuthenticated]


class JourFerieViewSet(viewsets.ReadOnlyModelViewSet):
    """Jours fériés"""
    queryset = JourFerie.objects.filter(est_actif=True)
    serializer_class = JourFerieSerializer
    permission_classes = [permissions.IsAuthenticated]


class JourExceptionnelViewSet(viewsets.ReadOnlyModelViewSet):
    """Jours exceptionnels et non-exceptionnels"""
    serializer_class = JourExceptionnelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        annee = self.request.query_params.get('annee', datetime.now().year)
        return JourExceptionnel.objects.filter(annee=annee)


class CongeAnnuelViewSet(viewsets.ReadOnlyModelViewSet):
    """Périodes de congés annuels"""
    queryset = CongeAnnuel.objects.filter(est_actif=True)
    serializer_class = CongeAnnuelSerializer
    permission_classes = [permissions.IsAuthenticated]


class CongeViewSet(viewsets.ModelViewSet):
    """Gestion des demandes de congés"""
    serializer_class = CongeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin voit tout
        if user.is_staff or user.is_superuser:
            return Conge.objects.all()
        
        # Utilisateur normal voit seulement ses congés
        return Conge.objects.filter(utilisateur=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CongeCreateSerializer
        return CongeSerializer
    
    def perform_create(self, serializer):
        """Crée le congé et met à jour le solde de l'utilisateur"""
        conge = serializer.save(utilisateur=self.request.user)
        
        # Déduire du solde si approuvé automatiquement ou en attente
        if conge.statut in ['en_attente', 'approuve']:
            conge.utilisateur.consommer_conge(float(conge.jours_deduits))
            conge.utilisateur.motif_conge = conge.motif
            conge.utilisateur.save()
        
        return conge
    
    @action(detail=False, methods=['get'])
    def mes_conges(self, request):
        """Liste les congés de l'utilisateur connecté avec filtres"""
        queryset = self.get_queryset().filter(utilisateur=request.user)
        
        # Filtre par année
        annee = request.query_params.get('annee')
        if annee:
            queryset = queryset.filter(date_debut__year=annee)
        
        # Filtre par statut
        statut = request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calendrier(self, request):
        """Retourne tous les événements pour le calendrier (congés + jours spéciaux)"""
        annee = int(request.query_params.get('annee', datetime.now().year))
        
        events = []
        
        # 1. Congés de l'utilisateur
        mes_conges = Conge.objects.filter(
            utilisateur=request.user,
            date_debut__year=annee,
            statut__in=['en_attente', 'approuve']
        )
        for conge in mes_conges:
            events.append({
                'id': f"conge_{conge.id}",
                'title': f"{conge.utilisateur} - {conge.get_type_conge_display()}",
                'start': conge.date_debut.isoformat(),
                'end': conge.date_fin.isoformat() if conge.date_fin != conge.date_debut else None,
                'allDay': True,
                'color': self._get_conge_color(conge.type_conge),
                'type': 'conge'
            })
        
        # 2. Jours fériés
        jours_feries = JourFerie.objects.filter(est_actif=True)
        for jf in jours_feries:
            # Créer une date pour l'année demandée
            try:
                date_jf = datetime(annee, jf.mois, jf.jour).date()
                events.append({
                    'id': f"ferie_{jf.id}",
                    'title': f"🎉 {jf.nom}",
                    'start': date_jf.isoformat(),
                    'allDay': True,
                    'color': '#ffeb3b',
                    'type': 'ferie',
                    'isBlocked': True  # Pour le frontend
                })
            except ValueError:
                continue  # Date invalide (29 février sur année non bissextile)
        
        # 3. Jours exceptionnels
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
        
        # 4. Congés annuels
        conges_annuels = CongeAnnuel.objects.filter(annee=annee, est_actif=True)
        for ca in conges_annuels:
            events.append({
                'id': f"annuel_{ca.id}",
                'title': f"🏖️ {ca.nom}",
                'start': ca.date_debut.isoformat(),
                'end': ca.date_fin.isoformat(),
                'allDay': True,
                'color': '#9c27b0',
                'type': 'conge_annuel',
                'isBlocked': True
            })
        
        # 5. Weekends (générés dynamiquement)
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
    
    def _get_conge_color(self, type_conge):
        colors = {
            'matin': '#c8e6c9',  # vert clair
            'midi': '#ffe0b2',   # orange clair
            'journee': '#bbdefb' # bleu clair
        }
        return colors.get(type_conge, '#e3f2fd')
    
    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annuler une demande de congé et rembourser le solde"""
        conge = self.get_object()
        
        if conge.utilisateur != request.user and not request.user.is_staff:
            return Response({'error': 'Permission refusée'}, status=403)
        
        if conge.statut == 'annule':
            return Response({'error': 'Déjà annulé'}, status=400)
        
        # Rembourser le solde
        if conge.jours_deduits > 0:
            conge.utilisateur.solde_conge_actuelle += float(conge.jours_deduits)
            conge.utilisateur.solde_conge_consomme -= float(conge.jours_deduits)
            conge.utilisateur.save()
        
        conge.statut = 'annule'
        conge.save()
        
        return Response({'success': True, 'message': 'Congé annulé et solde remboursé'})
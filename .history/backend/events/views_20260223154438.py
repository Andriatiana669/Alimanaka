from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime

from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """API pour les événements (lecture seule)"""
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin voit tout
        if user.is_staff or user.is_superuser:
            return Event.objects.all()
        
        # Manager voit les événements de son équipe + événements système
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
            
            return Event.objects.filter(
                Q(user__isnull=True) |  # Événements système
                Q(user__equipe_id__in=equipes)  # Événements de son équipe
            ).distinct()
        
        # Utilisateur normal voit ses événements + événements système
        return Event.objects.filter(
            Q(user=user) | Q(user__isnull=True)
        ).distinct()
    
    @action(detail=False, methods=['get'])
    def calendrier(self, request):
        """Retourne les événements pour le calendrier"""
        annee = int(request.query_params.get('annee', datetime.now().year))
        mois = request.query_params.get('mois')
        type_filter = request.query_params.get('type')
        statut_filter = request.query_params.get('statut')
        
        queryset = self.get_queryset().filter(start_date__year=annee)
        
        if mois:
            queryset = queryset.filter(start_date__month=mois)
        
        if type_filter:
            queryset = queryset.filter(event_type=type_filter)
        
        if statut_filter:
            queryset = queryset.filter(statut=statut_filter)
        
        events = [event.to_calendar_dict() for event in queryset]
        
        return Response(events)
    
    @action(detail=False, methods=['get'])
    def utilisateurs(self, request):
        """Retourne la liste des utilisateurs avec des événements"""
        from users.models import User
        
        user_ids = self.get_queryset().filter(
            user__isnull=False
        ).values_list('user_id', flat=True).distinct()
        
        users = User.objects.filter(id__in=user_ids)
        
        data = [{
            'id': u.id,
            'display_name': u.get_display_name(),
            'username': u.username,
            'equipe_nom': u.equipe.nom if u.equipe else '',
        } for u in users]
        
        return Response(data)
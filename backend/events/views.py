from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.cache import cache
from datetime import datetime, timedelta
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
        """Retourne tous les événements pour le calendrier (utilisateurs + système)"""
        annee = int(request.query_params.get('annee', datetime.now().year))
        mois = request.query_params.get('mois')
        type_filter = request.query_params.get('type')
        statut_filter = request.query_params.get('statut')
        skip_cache = request.query_params.get('skip_cache', 'false').lower() == 'true'
        
        # Clé de cache (différente selon les filtres)
        cache_key = f'calendrier_{annee}_{mois}_{type_filter}_{statut_filter}'
        
        # Vérifier le cache (sauf si skip_cache est true)
        if not skip_cache:
            cached_events = cache.get(cache_key)
            if cached_events is not None:
                return Response(cached_events)
        
        # 1. Récupérer les événements de la base (congés, retards, etc.)
        queryset = self.get_queryset().filter(start_date__year=annee)
        
        if mois:
            queryset = queryset.filter(start_date__month=mois)
        
        if type_filter:
            queryset = queryset.filter(event_type=type_filter)
        
        if statut_filter:
            queryset = queryset.filter(statut=statut_filter)
        
        events = [event.to_calendar_dict() for event in queryset]
        
        # Si on filtre par type, on n'ajoute que les types demandés
        add_feries = not type_filter or type_filter == 'ferie'
        add_exceptionnels = not type_filter or type_filter == 'exceptionnel'
        add_weekends = not type_filter or type_filter == 'weekend'
        
        # 2. AJOUTER les jours fériés (du module conges)
        if add_feries:
            from conges.models import JourFerie
            jours_feries = JourFerie.objects.filter(est_actif=True)
            for jf in jours_feries:
                try:
                    date_jf = datetime(annee, jf.mois, jf.jour).date()
                    # Vérifier que la date est dans l'année demandée
                    if date_jf.year == annee:
                        events.append({
                            'id': f"ferie_{jf.id}",
                            'title': f"🎉 {jf.nom}",
                            'start': date_jf.isoformat(),
                            'allDay': True,
                            'color': '#ffeb3b',
                            'type': 'ferie',
                            'isBlocked': True,
                            'isSystem': True
                        })
                except ValueError:
                    continue
        
        # 3. AJOUTER les jours exceptionnels
        if add_exceptionnels:
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
                    'isBlocked': je.type_jour == 'exceptionnel',
                    'isSystem': True
                })
        
        # 4. AJOUTER les weekends (calculés à la volée)
        if add_weekends:
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
                        'isBlocked': True,
                        'isSystem': True
                    })
                current += timedelta(days=1)
        
        # Mettre en cache pour 1 heure (3600 secondes)
        cache.set(cache_key, events, 3600)
        
        return Response(events)
    
    @action(detail=False, methods=['get'])
    def utilisateurs(self, request):
        """Retourne la liste des utilisateurs avec des événements"""
        from users.models import User
        
        # Récupérer les IDs des utilisateurs qui ont des événements
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
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Retourne la liste des types d'événements disponibles"""
        from .models import Event
        
        types = Event.objects.values_list('event_type', flat=True).distinct()
        
        # Ajouter les types système
        system_types = ['ferie', 'exceptionnel', 'weekend']
        
        all_types = list(set(list(types) + system_types))
        
        type_labels = {
            'conge': 'Congés',
            'retard': 'Retards',
            'permission': 'Permissions',
            'repos_medical': 'Repos médicaux',
            'ostie': 'OSTIES',
            'ferie': 'Jours fériés',
            'exceptionnel': 'Jours exceptionnels',
            'weekend': 'Weekends',
            'system': 'Système'
        }
        
        data = [{
            'value': t,
            'label': type_labels.get(t, t),
            'color': self._get_type_color(t)
        } for t in all_types]
        
        return Response(data)
    
    def _get_type_color(self, type_value):
        """Retourne la couleur associée à un type d'événement"""
        colors = {
            'conge': '#3498db',
            'retard': '#f39c12',
            'permission': '#27ae60',
            'repos_medical': '#e74c3c',
            'ostie': '#9b59b6',
            'ferie': '#ffeb3b',
            'exceptionnel': '#ff5722',
            'weekend': '#e0e0e0',
        }
        return colors.get(type_value, '#95a5a6')
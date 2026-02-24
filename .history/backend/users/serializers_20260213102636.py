from rest_framework import serializers
from .models import User, Pole, Equipe



class PoleSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les pôles"""
    equipes_count = serializers.IntegerField(source='equipes.count', read_only=True)
    utilisateurs_count = serializers.IntegerField(source='utilisateurs.count', read_only=True)
    
    class Meta:
        model = Pole
        fields = ['id', 'code', 'nom', 'description', 'est_actif', 
                  'equipes_count', 'utilisateurs_count', 'date_creation']
        read_only_fields = ['date_creation']
        
        
class EquipeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les équipes avec hiérarchie"""
    pole_details = PoleSerializer(source='pole', read_only=True)
    manager_details = serializers.SerializerMethodField()
    membres_count = serializers.IntegerField(source='membres.count', read_only=True)
    sous_equipes_count = serializers.IntegerField(source='sous_equipes.count', read_only=True)
    niveau_hierarchique = serializers.IntegerField(read_only=True)
    co_managers_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipe
        fields = [
            'id', 'nom', 'description', 'pole', 'pole_details',
            'manager', 'manager_details', 'equipe_parente', 'co_managers', 'co_managers_details',
            'membres_count', 'sous_equipes_count', 'niveau_hierarchique',
            'est_actif', 'date_creation'
        ]
        read_only_fields = ['date_creation', 'niveau_hierarchique']
    
    def get_manager_details(self, obj):
        if obj.manager:
            return {
                'id': obj.manager.id,
                'display_name': obj.manager.get_display_name(),
                'username': obj.manager.username,
                'first_name': obj.manager.first_name,
                'last_name': obj.manager.last_name,
                'pseudo': obj.manager.pseudo
            }
        return None
    
    def get_co_managers_details(self, obj):
        if obj.co_managers.exists():
            return [
                {
                    'id': user.id,
                    'display_name': user.get_display_name(),
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'pseudo': user.pseudo
                }
                for user in obj.co_managers.all()
            ]
        return []
    
    def validate(self, data):
        # Empêcher une équipe d'être sa propre parente
        if data.get('equipe_parente') == self.instance:
            raise serializers.ValidationError(
                "Une équipe ne peut pas être sa propre équipe parente."
            )
        return data
    
    
class EquipeTreeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'arborescence des équipes"""
    sous_equipes = serializers.SerializerMethodField()
    pole_details = PoleSerializer(source='pole', read_only=True)  # AJOUTE
    manager_details = serializers.SerializerMethodField()  # AJOUTE
    membres_count = serializers.IntegerField(source='membres.count', read_only=True)
    co_managers_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipe
        fields = [
            'id', 'nom', 'description',
            'manager', 'manager_details',
            'co_managers', 'co_managers_details',
            'pole', 'pole_details',
            'membres_count', 'sous_equipes', 
            'date_creation', 'est_actif'
        ]
        
    def get_manager_details(self, obj):
        if obj.manager:
            return {
                'id': obj.manager.id,
                'display_name': obj.manager.get_display_name(),
                'username': obj.manager.username,
                'first_name': obj.manager.first_name, 
                'last_name': obj.manager.last_name, 
                'pseudo': obj.manager.pseudo
            }
        return None
    
    def get_co_managers_details(self, obj):
        if obj.co_managers.exists():
            return [
                {
                    'id': user.id,
                    'display_name': user.get_display_name(),
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'pseudo': user.pseudo
                }
                for user in obj.co_managers.all()
            ]
        return []
    
    def get_sous_equipes(self, obj):
        """Récupère récursivement les sous-équipes"""
        inclure_inactives = self.context.get('inclure_inactives', False)
        
        filtre = {'equipe_parente': obj}
        if not inclure_inactives:
            filtre['est_actif'] = True
            
        sous_equipes = Equipe.objects.filter(**filtre)
        return EquipeTreeSerializer(sous_equipes, many=True, context=self.context).data
    
    
    
class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour l'utilisateur (admin)"""
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    pseudo_format_display = serializers.CharField(source='get_pseudo_format_display', read_only=True)
    
    
    pole_details = PoleSerializer(source='pole', read_only=True)
    equipe_details = EquipeSerializer(source='equipe', read_only=True)
    est_chef_equipe = serializers.BooleanField(read_only=True)
    
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'pseudo', 'pseudo_format', 'pseudo_format_display', 'email',
            'keycloak_id', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'last_updated', 'full_name', 'display_name',
            
            'pole', 'pole_details',
            'equipe', 'equipe_details',
            'est_chef_equipe'
        ]
        read_only_fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'solde_conge_consomme',
            'keycloak_id', 'date_joined', 'last_login', 'last_updated','est_chef_equipe'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_display_name(self, obj):
        return obj.get_display_name()


class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le profil utilisateur (modifiable)"""
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    pseudo_format_display = serializers.CharField(source='get_pseudo_format_display', read_only=True)
    
    
    # Nouveaux champs en lecture seule
    pole_details = PoleSerializer(source='pole', read_only=True)
    equipe_details = EquipeSerializer(source='equipe', read_only=True)
    equipes_managerisees = serializers.SerializerMethodField()
    
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'pseudo', 'pseudo_format',
            'pseudo_format_display', 'email', 'full_name', 'display_name', 'date_joined', 'last_login',
            
            # Nouveaux champs
            'pole', 'pole_details',
            'equipe', 'equipe_details',
            'equipes_managerisees'
        ]
        read_only_fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'date_joined', 'last_login'
        ]
    
    def get_equipes_managerisees(self, obj):
        """Liste des équipes gérées par l'utilisateur"""
        return [{
            'id': eq.id,
            'nom': eq.nom,
            'membres_count': eq.membres.count()
        } for eq in obj.equipes_gerees.filter(est_actif=True)]
        
        
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    
    
    
    
class UserListSerializer(serializers.ModelSerializer):
    """Sérialiseur allégé pour la liste publique"""
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    pole_nom = serializers.CharField(source='pole.nom', read_only=True)
    equipe_nom = serializers.CharField(source='equipe.nom', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'display_name', 'pseudo', 
            'username', 'first_name', 'last_name',
            'pole_nom', 'equipe_nom', 'is_staff', 'date_joined'
        ]
        
        

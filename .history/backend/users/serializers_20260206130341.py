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
    
    class Meta:
        model = Equipe
        fields = [
            'id', 'nom', 'description', 'pole', 'pole_details',
            'manager', 'manager_details', 'equipe_parente',
            'membres_count', 'sous_equipes_count', 'niveau_hierarchique',
            'est_actif', 'date_creation'
        ]
        read_only_fields = ['date_creation', 'niveau_hierarchique']
    
    def get_manager_details(self, obj):
        if obj.manager:
            return {
                'id': obj.manager.id,
                'display_name': obj.manager.get_display_name(),
                'username': obj.manager.username
            }
        return None
    
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
    
    class Meta:
        model = Equipe
        fields = ['id', 'nom', 'manager', 'sous_equipes', 'est_actif']
    
    def get_sous_equipes(self, obj):
        # Récursion limitée à 3 niveaux pour éviter les boucles infinies
        niveau = self.context.get('niveau', 0)
        if niveau >= 3:
            return []
        
        serializer = EquipeTreeSerializer(
            obj.sous_equipes.filter(est_actif=True),
            many=True,
            context={'niveau': niveau + 1}
        )
        return serializer.data
    
    
    
class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour l'utilisateur (admin)"""
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    pseudo_format_display = serializers.CharField(source='get_pseudo_format_display', read_only=True)
    
    
    # Nouveaux champs
    pole_details = PoleSerializer(source='pole', read_only=True)
    equipe_details = EquipeSerializer(source='equipe', read_only=True)
    est_chef_equipe = serializers.BooleanField(read_only=True)
    
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'pseudo', 'pseudo_format', 'pseudo_format_display', 'email',
            'keycloak_id', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'last_updated', 'full_name', 'display_name',
            
            # Nouveaux champs
            'pole', 'pole_details',
            'equipe', 'equipe_details',
            'est_chef_equipe'
        ]
        read_only_fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 
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
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'pseudo', 'pseudo_format',
            'pseudo_format_display', 'email', 'full_name', 'display_name', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'date_joined', 'last_login'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_display_name(self, obj):
        return obj.get_display_name()
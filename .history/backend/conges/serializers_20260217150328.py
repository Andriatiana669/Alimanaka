from rest_framework import serializers
from .models import TypeCongeConfig, JourFerie, JourExceptionnel, CongeAnnuel, Conge, Droit
from users.serializers import UserListSerializer


class DroitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Droit
        fields = ['id', 'nom', 'description', 'est_actif', 'ordre']
        
class TypeCongeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeCongeConfig
        fields = '__all__'


class JourFerieSerializer(serializers.ModelSerializer):
    class Meta:
        model = JourFerie
        fields = '__all__'


class JourExceptionnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = JourExceptionnel
        fields = '__all__'


class CongeAnnuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CongeAnnuel
        fields = '__all__'


class CongeSerializer(serializers.ModelSerializer):
    utilisateur_details = UserListSerializer(source='utilisateur', read_only=True)
    type_conge_display = serializers.CharField(source='get_type_conge_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    valide_par_details = UserListSerializer(source='valide_par', read_only=True)
    refuse_par_details = UserListSerializer(source='refuse_par', read_only=True)
    
    class Meta:
        model = Conge
        fields = [
            'id', 'utilisateur', 'utilisateur_details',
            'type_conge', 'type_conge_display',
            'date_debut', 'date_fin', 'motif',
            'statut', 'statut_display', 'jours_deduits', 'jours_valides',
            'date_creation', 'date_modification',
            'valide_par', 'valide_par_details', 'date_validation',
            'refuse_par', 'refuse_par_details', 'date_refus', 'commentaire_refus', 'conge_original',
        ]
        read_only_fields = ['jours_deduits', 'date_creation', 'date_modification', 'valide_par', 'date_validation', 'refuse_par', 'date_refus', 'jours_valides']
    
    def create(self, validated_data):
        conge = super().create(validated_data)
        conge.calculer_deduction()
        conge.save()
        return conge


class CongeCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la création depuis le frontend"""
    
    class Meta:
        model = Conge
        fields = ['type_conge', 'date_debut', 'date_fin', 'motif']
    
    def validate(self, data):
        user = self.context['request'].user
        
        # Vérifier que date_fin >= date_debut
        if data['date_fin'] < data['date_debut']:
            raise serializers.ValidationError("La date de fin doit être après la date de début")
        
        # Calcul temporaire pour vérifier le solde
        # temp_conge = Conge(
        #     utilisateur=user,
        #     type_conge=data['type_conge'],
        #     date_debut=data['date_debut'],
        #     date_fin=data['date_fin']
        # )
        # jours_necessaires = temp_conge.calculer_deduction()
        
        # if user.solde_conge_actuelle < jours_necessaires:
        #     raise serializers.ValidationError(
        #         f"Solde insuffisant. Disponible: {user.solde_conge_actuelle}, "
        #         f"Requis: {jours_necessaires}"
        #     )
        
        return data
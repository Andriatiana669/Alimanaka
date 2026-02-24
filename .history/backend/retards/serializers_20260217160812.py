from rest_framework import serializers
from .models import TypeRetardConfig, Retard, Rattrapage
from users.serializers import UserListSerializer


class TypeRetardConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeRetardConfig
        fields = '__all__'


class RattrapageSerializer(serializers.ModelSerializer):
    valide_par_details = UserListSerializer(source='valide_par', read_only=True)
    
    class Meta:
        model = Rattrapage
        fields = [
            'id', 'retard', 'date_rattrapage', 'heure_debut', 'heure_fin',
            'heures_rattrapees', 'valide_par', 'valide_par_details',
            'date_validation', 'commentaire'
        ]
        read_only_fields = ['heures_rattrapees', 'date_validation']


class RetardSerializer(serializers.ModelSerializer):
    utilisateur_details = UserListSerializer(source='utilisateur', read_only=True)
    approuve_par_details = UserListSerializer(source='approuve_par', read_only=True)
    annule_par_details = UserListSerializer(source='annule_par', read_only=True)
    rattrapages = RattrapageSerializer(many=True, read_only=True)
    type_retard_display = serializers.CharField(source='get_type_retard_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Retard
        fields = [
            'id', 'utilisateur', 'utilisateur_details',
            'date', 'heure_debut_prevue', 'heure_arrivee_reelle',
            'minutes_retard', 'heures_a_rattraper', 'heures_restantes',
            'type_retard', 'type_retard_display',
            'motif_retard', 'statut', 'statut_display',
            'date_creation', 'date_modification',
            'approuve_par', 'approuve_par_details', 'date_approbation',
            'annule_par', 'annule_par_details', 'date_annulation', 'commentaire_annulation',
            'retard_original', 'rattrapages'
        ]
        read_only_fields = [
            'minutes_retard', 'heures_a_rattraper', 'type_retard',
            'date_creation', 'date_modification'
        ]


class RetardCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la création depuis le frontend"""
    
    class Meta:
        model = Retard
        fields = ['date', 'heure_arrivee_reelle', 'motif_retard']
    
    def validate(self, data):
        user = self.context['request'].user
        
        # Récupérer l'heure de début prévue depuis la config admin
        # Note: À adapter selon votre logique métier
        from datetime import time
        data['heure_debut_prevue'] = time(8, 0)  # Exemple: 8h00
        
        return data


class RattrapageCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer un rattrapage"""
    
    class Meta:
        model = Rattrapage
        fields = ['date_rattrapage', 'heure_debut', 'heure_fin', 'commentaire']
    
    def validate(self, data):
        # Validation que la date de rattrapage n'est pas dans le futur
        from datetime import date
        if data['date_rattrapage'] > date.today():
            raise serializers.ValidationError(
                "La date de rattrapage ne peut pas être dans le futur"
            )
        return data
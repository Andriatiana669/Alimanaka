from rest_framework import serializers
from .models import TypeRetardConfig, Retard, Rattrapage
from users.serializers import UserListSerializer


class TypeRetardConfigSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les configurations de types de retard"""
    
    class Meta:
        model = TypeRetardConfig
        fields = '__all__'


class RattrapageSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les rattrapages"""
    valide_par_details = UserListSerializer(source='valide_par', read_only=True)
    
    class Meta:
        model = Rattrapage
        fields = '__all__'
        read_only_fields = ['heures_rattrapees', 'date_validation']


class RattrapageCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la création de rattrapage"""
    
    class Meta:
        model = Rattrapage
        fields = ['date_rattrapage', 'heure_debut', 'heure_fin', 'commentaire']
    
    def validate(self, data):
        # Validation que la date n'est pas dans le futur
        from datetime import date
        if data['date_rattrapage'] > date.today():
            raise serializers.ValidationError(
                "La date de rattrapage ne peut pas être dans le futur"
            )
        
        # Validation que l'heure de fin est après l'heure de début
        if data['heure_fin'] <= data['heure_debut']:
            raise serializers.ValidationError(
                "L'heure de fin doit être après l'heure de début"
            )
        
        return data


class RetardSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour les retards"""
    utilisateur_details = UserListSerializer(source='utilisateur', read_only=True)
    type_retard_details = TypeRetardConfigSerializer(source='type_retard', read_only=True)
    rattrapages = RattrapageSerializer(many=True, read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    approuve_par_details = UserListSerializer(source='approuve_par', read_only=True)
    annule_par_details = UserListSerializer(source='annule_par', read_only=True)
    
    class Meta:
        model = Retard
        fields = [
            'id', 'utilisateur', 'utilisateur_details',
            'date', 'type_retard', 'type_retard_details',
            'heure_debut_prevue', 'heure_arrivee_reelle',
            'minutes_retard', 'heures_a_rattraper', 'heures_restantes',
            'motif_retard',
            'statut', 'statut_display',
            'date_creation', 'date_modification',
            'approuve_par', 'approuve_par_details', 'date_approbation',
            'annule_par', 'annule_par_details', 'date_annulation', 'commentaire_annulation',
            'rattrapages', 'retard_original'
        ]
        read_only_fields = [
            'minutes_retard', 'heures_a_rattraper', 'heures_restantes',
            'date_creation', 'date_modification', 'approuve_par', 'date_approbation',
            'annule_par', 'date_annulation'
        ]


class RetardCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la création de retard"""
    
    class Meta:
        model = Retard
        fields = ['date', 'heure_arrivee_reelle', 'motif_retard', 'type_retard']
    
    def validate(self, data):
        # Vérifier que la date n'est pas dans le futur
        from datetime import date
        if data['date'] > date.today():
            raise serializers.ValidationError({
                'date': "La date du retard ne peut pas être dans le futur"
            })
        
        # Vérifier que le type_retard est fourni
        if not data.get('type_retard'):
            raise serializers.ValidationError({
                'type_retard': "Le type de retard est requis"
            })
        
        # Récupérer la configuration pour avoir l'heure de début prévue
        try:
            type_config = data['type_retard']
            heure_prevue = type_config.heure_debut_prevue
        except AttributeError:
            raise serializers.ValidationError({
                'type_retard': "Configuration de retard invalide"
            })
        
        # Vérifier que l'heure d'arrivée est après l'heure prévue
        if data['heure_arrivee_reelle'] <= heure_prevue:
            raise serializers.ValidationError({
                'heure_arrivee_reelle': f"L'heure d'arrivée doit être après {heure_prevue}"
            })
        
        return data
    
    def create(self, validated_data):
        # Récupérer l'heure de début prévue depuis la configuration
        type_config = validated_data['type_retard']
        
        # Créer le retard avec l'heure de début prévue
        retard = Retard.objects.create(
            **validated_data,
            heure_debut_prevue=type_config.heure_debut_prevue
        )
        return retard
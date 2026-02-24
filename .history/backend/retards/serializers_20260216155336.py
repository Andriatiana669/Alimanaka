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
        read_only_fields = ['heures_rattrapees', 'valide_par', 'date_validation']


class RetardSerializer(serializers.ModelSerializer):
    utilisateur_details = UserListSerializer(source='utilisateur', read_only=True)
    type_retard_display = serializers.CharField(source='get_type_retard_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    approuve_par_details = UserListSerializer(source='approuve_par', read_only=True)
    annule_par_details = UserListSerializer(source='annule_par', read_only=True)
    rattrapages = RattrapageSerializer(many=True, read_only=True)
    total_rattrape = serializers.SerializerMethodField()
    
    class Meta:
        model = Retard
        fields = [
            'id', 'utilisateur', 'utilisateur_details',
            'date', 'heure_debut_prevue', 'heure_arrivee_reelle',
            'minutes_retard', 'heures_a_rattraper', 'heures_restantes',
            'motif_retard', 'type_retard', 'type_retard_display',
            'statut', 'statut_display',
            'date_creation', 'date_modification',
            'approuve_par', 'approuve_par_details', 'date_approbation',
            'annule_par', 'annule_par_details', 'date_annulation', 'commentaire_annulation',
            'retard_original', 'rattrapages', 'total_rattrape'
        ]
        read_only_fields = [
            'minutes_retard', 'heures_a_rattraper', 'heures_restantes',
            'type_retard', 'date_creation', 'date_modification',
            'approuve_par', 'date_approbation',
            'annule_par', 'date_annulation'
        ]
    
    def get_total_rattrape(self, obj):
        """Calcule le total des heures déjà rattrapées"""
        return sum(r.heures_rattrapees for r in obj.rattrapages.all())


class RetardCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la création"""
    
    class Meta:
        model = Retard
        fields = ['date', 'heure_arrivee_reelle', 'motif_retard']
    
    def validate(self, data):
        user = self.context['request'].user
        
        # Vérifier qu'il n'y a pas déjà un retard ce jour-là
        if Retard.objects.filter(
            utilisateur=user,
            date=data['date'],
            statut__in=['en_attente', 'approuve']
        ).exists():
            raise serializers.ValidationError(
                "Vous avez déjà déclaré un retard pour cette date"
            )
        
        return data


class RattrapageCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer un rattrapage"""
    
    class Meta:
        model = Rattrapage
        fields = ['date_rattrapage', 'heure_debut', 'heure_fin', 'commentaire']
    
    def validate(self, data):
        if data['heure_fin'] <= data['heure_debut']:
            raise serializers.ValidationError(
                "L'heure de fin doit être après l'heure de début"
            )
        return data
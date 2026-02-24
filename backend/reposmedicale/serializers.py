from rest_framework import serializers
from .models import ReposMedical
from users.serializers import UserListSerializer
from conges.serializers import CongeSerializer


class ReposMedicalSerializer(serializers.ModelSerializer):
    utilisateur_details = UserListSerializer(source='utilisateur', read_only=True)
    valide_par_details = UserListSerializer(source='valide_par', read_only=True)
    annule_par_details = UserListSerializer(source='annule_par', read_only=True)
    conge_genere_details = CongeSerializer(source='conge_genere', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = ReposMedical
        fields = [
            'id', 'utilisateur', 'utilisateur_details',
            'date', 'heure_debut', 'heure_fin', 'duree_heures',
            'motif', 'avertissement',
            'statut', 'statut_display',
            'conge_genere', 'conge_genere_details',
            'date_creation', 'date_modification',
            'valide_par', 'valide_par_details', 'date_validation',
            'annule_par', 'annule_par_details', 'date_annulation', 'commentaire_annulation',
        ]
        read_only_fields = ['duree_heures', 'date_creation', 'date_modification']


class ReposMedicalCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'un repos médical"""
    
    class Meta:
        model = ReposMedical
        fields = ['date', 'heure_debut', 'heure_fin', 'motif', 'avertissement']
    
    def validate(self, data):
        # Vérifier que la date n'est pas dans le passé
        from datetime import date
        if data['date'] < date.today():
            raise serializers.ValidationError({
                'date': "La date du repos médical ne peut pas être dans le passé"
            })
        
        # Vérifier que l'heure de fin est après l'heure de début
        if data['heure_fin'] <= data['heure_debut']:
            raise serializers.ValidationError({
                'heure_fin': "L'heure de fin doit être après l'heure de début"
            })
        
        return data


class ReposMedicalValidationSerializer(serializers.Serializer):
    """Sérialiseur pour valider directement un repos médical"""
    pass  # Pas de données nécessaires


class ReposMedicalTransformationSerializer(serializers.Serializer):
    """Sérialiseur pour transformer en congé"""
    type_conge = serializers.ChoiceField(choices=['matin', 'midi', 'journee'])


class ReposMedicalAnnulationSerializer(serializers.Serializer):
    """Sérialiseur pour annuler un repos médical"""
    commentaire = serializers.CharField(required=False, allow_blank=True)
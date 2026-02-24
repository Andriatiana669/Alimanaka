from rest_framework import serializers
from .models import Permission
from users.serializers import UserListSerializer
from conges.serializers import CongeSerializer


class PermissionSerializer(serializers.ModelSerializer):
    utilisateur_details = UserListSerializer(source='utilisateur', read_only=True)
    valide_par_details = UserListSerializer(source='valide_par', read_only=True)
    annule_par_details = UserListSerializer(source='annule_par', read_only=True)
    conge_genere_details = CongeSerializer(source='conge_genere', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Permission
        fields = [
            'id', 'utilisateur', 'utilisateur_details',
            'date', 'heure_depart', 'heure_arrivee_max', 'heure_arrivee_reelle',
            'motif',
            'minutes_depassement', 'heures_a_rattraper', 'heures_restantes',
            'statut', 'statut_display',
            'rattrapages',
            'conge_genere', 'conge_genere_details',
            'date_creation', 'date_modification',
            'valide_par', 'valide_par_details', 'date_validation',
            'annule_par', 'annule_par_details', 'date_annulation', 'commentaire_annulation',
        ]
        read_only_fields = [
            'minutes_depassement', 'heures_a_rattraper',
            'date_creation', 'date_modification'
        ]


class PermissionCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'une permission"""
    
    class Meta:
        model = Permission
        fields = ['date', 'heure_depart', 'motif']
    
    def validate(self, data):
        user = self.context['request'].user
        
        # Vérifier que la date n'est pas dans le passé
        from datetime import date
        if data['date'] < date.today():
            raise serializers.ValidationError({
                'date': "La date de permission ne peut pas être dans le passé"
            })
        
        return data


class PermissionRetourSerializer(serializers.Serializer):
    """Sérialiseur pour enregistrer le retour"""
    heure_arrivee_reelle = serializers.TimeField()


class PermissionRattrapageSerializer(serializers.Serializer):
    """Sérialiseur pour ajouter un rattrapage"""
    date_rattrapage = serializers.DateField()
    heure_debut = serializers.TimeField()
    heure_fin = serializers.TimeField()
    commentaire = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        # Vérifier que la date de rattrapage n'est pas dans le futur
        from datetime import date
        if data['date_rattrapage'] > date.today():
            raise serializers.ValidationError({
                'date_rattrapage': "La date de rattrapage ne peut pas être dans le futur"
            })
        
        # Vérifier que l'heure de fin est après l'heure de début
        if data['heure_fin'] <= data['heure_debut']:
            raise serializers.ValidationError({
                'heure_fin': "L'heure de fin doit être après l'heure de début"
            })
        
        return data


class PermissionTransformationSerializer(serializers.Serializer):
    """Sérialiseur pour transformer en congé"""
    type_conge = serializers.ChoiceField(choices=['matin', 'midi', 'journee'])


class PermissionAnnulationSerializer(serializers.Serializer):
    """Sérialiseur pour annuler une permission"""
    commentaire = serializers.CharField(required=False, allow_blank=True)
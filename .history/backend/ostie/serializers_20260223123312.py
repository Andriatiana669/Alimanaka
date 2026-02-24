from rest_framework import serializers
from .models import Ostie
from users.serializers import UserListSerializer
from reposmedicale.serializers import ReposMedicalSerializer


class OstieSerializer(serializers.ModelSerializer):
    utilisateur_details = UserListSerializer(source='utilisateur', read_only=True)
    valide_par_details = UserListSerializer(source='valide_par', read_only=True)
    annule_par_details = UserListSerializer(source='annule_par', read_only=True)
    repos_genere_details = ReposMedicalSerializer(source='repos_genere', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    
    class Meta:
        model = Ostie
        fields = [
            'id', 'utilisateur', 'utilisateur_details',
            'date', 'heure_debut', 'heure_fin',
            'motif',
            'statut', 'statut_display',
            'repos_genere', 'repos_genere_details',
            'date_creation', 'date_modification',
            'valide_par', 'valide_par_details', 'date_validation',
            'annule_par', 'annule_par_details', 'date_annulation', 'commentaire_annulation',
        ]
        read_only_fields = ['date_creation', 'date_modification']


class OstieCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'un OSTIE"""
    
    class Meta:
        model = Ostie
        fields = ['date', 'heure_debut', 'motif']
    
    def validate(self, data):
        # Vérifier que la date n'est pas dans le passé
        from datetime import date
        if data['date'] < date.today():
            raise serializers.ValidationError({
                'date': "La date de l'OSTIE ne peut pas être dans le passé"
            })
        
        return data


class OstieValidationSerializer(serializers.Serializer):
    """Sérialiseur pour valider directement un OSTIE"""
    heure_fin = serializers.TimeField(help_text="Heure de fin de l'OSTIE")


class OstieTransformationSerializer(serializers.Serializer):
    """Sérialiseur pour transformer en repos médical"""
    heure_fin_ostie = serializers.TimeField(help_text="Heure de fin de l'OSTIE")
    heure_fin_repos = serializers.TimeField(help_text="Heure de fin du repos médical")
    
    def validate(self, data):
        # Vérifier que l'heure de fin du repos est après l'heure de fin de l'OSTIE
        from datetime import datetime, date
        aujourdhui = date.today()
        
        fin_ostie_dt = datetime.combine(aujourdhui, data['heure_fin_ostie'])
        fin_repos_dt = datetime.combine(aujourdhui, data['heure_fin_repos'])
        
        if fin_repos_dt <= fin_ostie_dt:
            raise serializers.ValidationError({
                'heure_fin_repos': "L'heure de fin du repos médical doit être après l'heure de fin de l'OSTIE"
            })
        
        return data


class OstieAnnulationSerializer(serializers.Serializer):
    """Sérialiseur pour annuler un OSTIE"""
    commentaire = serializers.CharField(required=False, allow_blank=True)
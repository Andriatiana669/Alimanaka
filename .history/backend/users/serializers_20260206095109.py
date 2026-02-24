from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour l'utilisateur (admin)"""
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    pseudo_format_display = serializers.CharField(source='get_pseudo_format_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'pseudo', 'email',
            'keycloak_id', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'last_updated', 'full_name', 'display_name'
        ]
        read_only_fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 
            'keycloak_id', 'date_joined', 'last_login', 'last_updated'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_display_name(self, obj):
        return obj.get_display_name()


class UserProfileSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le profil utilisateur (modifiable)"""
    full_name = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'pseudo', 'email',
            'full_name', 'display_name', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'date_joined', 'last_login'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_display_name(self, obj):
        return obj.get_display_name()
from rest_framework import serializers
from .models import Event
from users.serializers import UserListSerializer


class EventSerializer(serializers.ModelSerializer):
    user_details = UserListSerializer(source='user', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type',
            'start_date', 'end_date', 'start_time', 'end_time', 'all_day',
            'color', 'icon', 'is_blocked', 'is_system',
            'user', 'user_details', 'statut',
            'created_at', 'updated_at'
        ]
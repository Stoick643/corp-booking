from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Area, Room, Desk, Reservation, UserPermission

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Converts User model to JSON, excludes sensitive fields, includes permissions."""
    area_permissions = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'employee_id', 'department', 'is_admin', 'area_permissions'
        ]
        read_only_fields = ['id', 'area_permissions']


class AreaSerializer(serializers.ModelSerializer):
    """Converts Area model to JSON with room and desk counts."""
    room_count = serializers.IntegerField(source='rooms.count', read_only=True)
    desk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Area
        fields = ['id', 'name', 'map_svg', 'room_count', 'desk_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_desk_count(self, obj):
        """Calculate total desks across all rooms in this area"""
        return Desk.objects.filter(room__area=obj).count()


class RoomSerializer(serializers.ModelSerializer):
    """Converts Room model to JSON with area name and desk count."""
    area_name = serializers.CharField(source='area.name', read_only=True)
    desk_count = serializers.IntegerField(source='desks.count', read_only=True)
    
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'is_bookable', 'area', 'area_name', 
            'desk_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DeskSerializer(serializers.ModelSerializer):
    """Converts Desk model to JSON with room and area information."""
    room_name = serializers.CharField(source='room.name', read_only=True)
    area_name = serializers.CharField(source='room.area.name', read_only=True)
    
    class Meta:
        model = Desk
        fields = [
            'id', 'identifier', 'status', 'pos_x', 'pos_y',
            'room', 'room_name', 'area_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReservationSerializer(serializers.ModelSerializer):
    """Converts Reservation to JSON with validation for booking rules and quotas."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    desk_identifier = serializers.CharField(source='desk.identifier', read_only=True)
    area_name = serializers.CharField(source='desk.room.area.name', read_only=True)
    
    class Meta:
        model = Reservation
        fields = [
            'id', 'date', 'status', 'notes', 'created_at', 'checked_in_at',
            'user', 'user_name', 'desk', 'desk_identifier', 'area_name'
        ]
        read_only_fields = ['created_at', 'user_name', 'desk_identifier', 'area_name']
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from core.models import Area, Room, Desk, Reservation, UserPermission
from .serializers import (
    UserSerializer, AreaSerializer, RoomSerializer, 
    DeskSerializer, ReservationSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only user profiles. Shows current user's permissions and bookings."""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer


class AreaViewSet(viewsets.ReadOnlyModelViewSet):
    """Provides list() and retrieve() for areas. Read-only access."""
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    
    @action(detail=True, methods=['get'])
    def rooms(self, request, pk=None):
        """Custom endpoint to list all rooms for a specific area."""
        area = self.get_object()
        rooms = Room.objects.filter(area=area)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def desks(self, request, pk=None):
        """Updated area desks endpoint to work with Area->Room->Desk hierarchy."""
        area = self.get_object()
        desks = Desk.objects.filter(room__area=area)
        serializer = DeskSerializer(desks, many=True)
        return Response(serializer.data)


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to rooms, filtered by user's area permissions."""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    @action(detail=True, methods=['get'])
    def desks(self, request, pk=None):
        """List all desks in a specific room."""
        room = self.get_object()
        desks = room.desks.all()
        serializer = DeskSerializer(desks, many=True)
        return Response(serializer.data)


class DeskViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to desks."""
    queryset = Desk.objects.all()
    serializer_class = DeskSerializer


class ReservationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to reservations for now. CRUD will be added later with auth."""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

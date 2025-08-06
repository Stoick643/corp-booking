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


class ReservationViewSet(viewsets.ModelViewSet):
    """Reservations CRUD. Allows creating quick bookings."""
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    
    @action(detail=False, methods=['post'])
    def quick_book(self, request):
        """
        Quick booking endpoint for one-click desk reservations.
        Expects: {'desk_id': int, 'date': 'YYYY-MM-DD'}
        Returns: Reservation data or error message
        """
        desk_id = request.data.get('desk_id')
        date_str = request.data.get('date')
        
        if not desk_id or not date_str:
            return Response(
                {'error': 'desk_id and date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the desk
            desk = Desk.objects.get(id=desk_id)
            
            # For now, use the first user (TODO: use authenticated user)
            user = User.objects.first()
            if not user:
                return Response(
                    {'error': 'No users found in system'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Parse date
            from datetime import datetime
            try:
                reservation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if desk is available (not permanent, not disabled)
            if desk.status != 'available':
                return Response(
                    {'error': f'Desk {desk.identifier} is not available for booking'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the reservation
            reservation = Reservation.objects.create(
                user=user,
                desk=desk,
                date=reservation_date,
                status='confirmed'
            )
            
            # Return reservation data
            serializer = self.get_serializer(reservation)
            return Response({
                'success': True,
                'message': f'Desk {desk.identifier} booked successfully for {date_str}',
                'reservation': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Desk.DoesNotExist:
            return Response(
                {'error': f'Desk with id {desk_id} not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Handle duplicate booking or other errors
            if 'unique constraint' in str(e).lower():
                return Response(
                    {'error': f'Desk {desk.identifier} is already booked for {date_str}'}, 
                    status=status.HTTP_409_CONFLICT
                )
            return Response(
                {'error': f'Booking failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

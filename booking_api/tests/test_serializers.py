from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from core.models import Area, Room, Desk, Reservation, UserPermission
from booking_api.serializers import (
    UserSerializer, AreaSerializer, RoomSerializer,
    DeskSerializer, ReservationSerializer
)

User = get_user_model()


class UserSerializerTest(TestCase):
    """Test UserSerializer functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='john.doe',
            email='john.doe@company.com',
            password='secret123',
            first_name='John',
            last_name='Doe',
            employee_id='EMP001',
            department='Engineering',
            is_admin=True
        )
        
        # Create area permission
        self.area = Area.objects.create(name="Level 1 - Left Wing")
        UserPermission.objects.create(user=self.user, area=self.area)
    
    def test_user_serializer_excludes_sensitive_fields(self):
        """Password and other sensitive fields not exposed"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        # Should include these fields
        expected_fields = {
            'id', 'username', 'email', 'first_name', 'last_name',
            'employee_id', 'department', 'is_admin', 'area_permissions'
        }
        self.assertEqual(set(data.keys()), expected_fields)
        
        # Should NOT include sensitive fields
        self.assertNotIn('password', data)
        self.assertNotIn('is_superuser', data)
        self.assertNotIn('user_permissions', data)
        
        # Verify values
        self.assertEqual(data['username'], 'john.doe')
        self.assertEqual(data['employee_id'], 'EMP001')
        self.assertEqual(data['department'], 'Engineering')
        self.assertTrue(data['is_admin'])
    
    def test_user_serializer_area_permissions(self):
        """Area permissions included correctly"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(len(data['area_permissions']), 1)
        self.assertIn('Level 1 - Left Wing', str(data['area_permissions']))


class AreaSerializerTest(TestCase):
    """Test AreaSerializer functionality"""
    
    def setUp(self):
        self.area = Area.objects.create(name="Level 1 - Left Wing")
        
        # Create rooms and desks for counting
        self.room1 = Room.objects.create(area=self.area, name="Office 1.L.01")
        self.room2 = Room.objects.create(area=self.area, name="Office 1.L.02")
        
        Desk.objects.create(room=self.room1, identifier="1.L.01")
        Desk.objects.create(room=self.room1, identifier="1.L.01A")
        Desk.objects.create(room=self.room2, identifier="1.L.02")
    
    def test_area_serializer_calculated_fields(self):
        """room_count and desk_count calculated correctly"""
        serializer = AreaSerializer(self.area)
        data = serializer.data
        
        # Check structure
        expected_fields = {
            'id', 'name', 'map_svg', 'room_count', 'desk_count',
            'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)
        
        # Check calculated values
        self.assertEqual(data['name'], "Level 1 - Left Wing")
        self.assertEqual(data['room_count'], 2)
        self.assertEqual(data['desk_count'], 3)
        self.assertIsNone(data['map_svg'])
        self.assertTrue(data['created_at'])
        self.assertTrue(data['updated_at'])
    
    def test_area_serializer_empty_area(self):
        """Empty area shows zero counts"""
        empty_area = Area.objects.create(name="Empty Area")
        serializer = AreaSerializer(empty_area)
        data = serializer.data
        
        self.assertEqual(data['room_count'], 0)
        self.assertEqual(data['desk_count'], 0)


class RoomSerializerTest(TestCase):
    """Test RoomSerializer functionality"""
    
    def setUp(self):
        self.area = Area.objects.create(name="Level 1 - Left Wing")
        self.room = Room.objects.create(
            area=self.area,
            name="Office 1.L.01",
            is_bookable=True
        )
        
        # Add desks for counting
        Desk.objects.create(room=self.room, identifier="1.L.01A")
        Desk.objects.create(room=self.room, identifier="1.L.01B")
    
    def test_room_serializer_with_area_name_and_desk_count(self):
        """Room serializer includes area name and desk count"""
        serializer = RoomSerializer(self.room)
        data = serializer.data
        
        expected_fields = {
            'id', 'name', 'is_bookable', 'area', 'area_name',
            'desk_count', 'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)
        
        self.assertEqual(data['name'], "Office 1.L.01")
        self.assertEqual(data['area_name'], "Level 1 - Left Wing")
        self.assertTrue(data['is_bookable'])
        self.assertEqual(data['desk_count'], 2)
        self.assertEqual(data['area'], self.area.id)


class DeskSerializerTest(TestCase):
    """Test DeskSerializer functionality"""
    
    def setUp(self):
        self.area = Area.objects.create(name="Level 1 - Left Wing")
        self.room = Room.objects.create(area=self.area, name="Office 1.L.01")
        self.desk = Desk.objects.create(
            room=self.room,
            identifier="1.L.01",
            status='available',
            pos_x=150,
            pos_y=300
        )
    
    def test_desk_serializer_nested_names(self):
        """room_name and area_name populated correctly"""
        serializer = DeskSerializer(self.desk)
        data = serializer.data
        
        expected_fields = {
            'id', 'identifier', 'status', 'pos_x', 'pos_y',
            'room', 'room_name', 'area_name', 'created_at', 'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)
        
        self.assertEqual(data['identifier'], "1.L.01")
        self.assertEqual(data['status'], 'available')
        self.assertEqual(data['pos_x'], 150)
        self.assertEqual(data['pos_y'], 300)
        self.assertEqual(data['room_name'], "Office 1.L.01")
        self.assertEqual(data['area_name'], "Level 1 - Left Wing")
        self.assertEqual(data['room'], self.room.id)
    
    def test_desk_serializer_no_coordinates(self):
        """Desk without coordinates handled correctly"""
        desk_no_coords = Desk.objects.create(
            room=self.room,
            identifier="1.L.02",
            status='permanent'
        )
        
        serializer = DeskSerializer(desk_no_coords)
        data = serializer.data
        
        self.assertEqual(data['identifier'], "1.L.02")
        self.assertEqual(data['status'], 'permanent')
        self.assertIsNone(data['pos_x'])
        self.assertIsNone(data['pos_y'])


class ReservationSerializerTest(TestCase):
    """Test ReservationSerializer functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='john.doe',
            first_name='John',
            last_name='Doe'
        )
        self.area = Area.objects.create(name="Level 1 - Left Wing")
        self.room = Room.objects.create(area=self.area, name="Office 1.L.01")
        self.desk = Desk.objects.create(
            room=self.room,
            identifier="1.L.01"
        )
        
        tomorrow = date.today() + timedelta(days=1)
        self.reservation = Reservation.objects.create(
            user=self.user,
            desk=self.desk,
            date=tomorrow,
            status='confirmed',
            notes='Test reservation'
        )
    
    def test_reservation_serializer_readonly_fields(self):
        """Calculated and readonly fields work correctly"""
        serializer = ReservationSerializer(self.reservation)
        data = serializer.data
        
        expected_fields = {
            'id', 'date', 'status', 'notes', 'created_at', 'checked_in_at',
            'user', 'user_name', 'desk', 'desk_identifier', 'area_name'
        }
        self.assertEqual(set(data.keys()), expected_fields)
        
        # Check readonly calculated fields
        self.assertEqual(data['user_name'], 'John Doe')
        self.assertEqual(data['desk_identifier'], '1.L.01')
        self.assertEqual(data['area_name'], 'Level 1 - Left Wing')
        
        # Check writable fields
        self.assertEqual(data['status'], 'confirmed')
        self.assertEqual(data['notes'], 'Test reservation')
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['desk'], self.desk.id)
    
    def test_reservation_serializer_no_notes(self):
        """Reservation without notes handled correctly"""
        tomorrow = date.today() + timedelta(days=2)
        reservation_no_notes = Reservation.objects.create(
            user=self.user,
            desk=self.desk,
            date=tomorrow,
            status='pending_approval'
        )
        
        serializer = ReservationSerializer(reservation_no_notes)
        data = serializer.data
        
        self.assertEqual(data['status'], 'pending_approval')
        self.assertEqual(data['notes'], '')
        self.assertIsNone(data['checked_in_at'])
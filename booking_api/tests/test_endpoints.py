from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from core.models import Area, Room, Desk, Reservation, UserPermission

User = get_user_model()


class APIEndpointsTestCase(TestCase):
    """Test cases for all API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create test data structure: Area -> Room -> Desk
        self.area1 = Area.objects.create(name="Level 1 - Left Wing")
        self.area2 = Area.objects.create(name="Level 2 - Right Wing")
        
        # Rooms in area1
        self.room1 = Room.objects.create(area=self.area1, name="Office 1.L.01")
        self.room2 = Room.objects.create(area=self.area1, name="Office 1.L.02")
        
        # Room in area2  
        self.room3 = Room.objects.create(area=self.area2, name="Office 2.R.01")
        
        # Desks in rooms
        self.desk1 = Desk.objects.create(room=self.room1, identifier="1.L.01", status='available')
        self.desk2 = Desk.objects.create(room=self.room1, identifier="1.L.01A", status='available')
        self.desk3 = Desk.objects.create(room=self.room2, identifier="1.L.02", status='permanent')
        self.desk4 = Desk.objects.create(room=self.room3, identifier="2.R.01", status='available')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@company.com',
            employee_id='EMP001',
            department='Engineering'
        )
        
        # Create reservation
        tomorrow = date.today() + timedelta(days=1)
        self.reservation = Reservation.objects.create(
            user=self.user,
            desk=self.desk1,
            date=tomorrow,
            status='confirmed'
        )

    def test_areas_endpoint_structure(self):
        """Areas endpoint returns correct JSON structure with counts"""
        url = reverse('area-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        area1_data = next(area for area in response.data if area['name'] == "Level 1 - Left Wing")
        self.assertEqual(area1_data['room_count'], 2)
        self.assertEqual(area1_data['desk_count'], 3)
        
        # Check required fields
        required_fields = {'id', 'name', 'map_svg', 'room_count', 'desk_count', 'created_at', 'updated_at'}
        self.assertEqual(set(area1_data.keys()), required_fields)

    def test_area_desks_cross_room_filtering(self):
        """Area desks endpoint gets desks from all rooms in area"""
        url = reverse('area-desks', kwargs={'pk': self.area1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 2 desks in room1, 1 in room2
        
        # All desks should belong to area1 (through their rooms)
        for desk in response.data:
            self.assertEqual(desk['area_name'], "Level 1 - Left Wing")
            self.assertIn(desk['identifier'], ['1.L.01', '1.L.01A', '1.L.02'])

    def test_area_rooms_endpoint(self):
        """Area rooms endpoint filters rooms by area"""
        url = reverse('area-rooms', kwargs={'pk': self.area1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        room_names = [room['name'] for room in response.data]
        self.assertIn("Office 1.L.01", room_names)
        self.assertIn("Office 1.L.02", room_names)
        
        # Check room structure
        first_room = response.data[0]
        required_fields = {'id', 'name', 'is_bookable', 'area', 'area_name', 'desk_count', 'created_at', 'updated_at'}
        self.assertEqual(set(first_room.keys()), required_fields)

    def test_room_desks_endpoint(self):
        """Room desks endpoint filters desks by specific room"""
        url = reverse('room-desks', kwargs={'pk': self.room1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only desks in room1
        
        desk_ids = [desk['identifier'] for desk in response.data]
        self.assertIn("1.L.01", desk_ids)
        self.assertIn("1.L.01A", desk_ids)
        self.assertNotIn("1.L.02", desk_ids)  # This desk is in room2

    def test_users_exclude_sensitive_data(self):
        """Users endpoint doesn't expose passwords or sensitive data"""
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        user_data = response.data[0]
        
        # Should include these fields
        expected_fields = {'id', 'username', 'email', 'first_name', 'last_name', 'employee_id', 'department', 'is_admin', 'area_permissions'}
        self.assertEqual(set(user_data.keys()), expected_fields)
        
        # Should NOT include sensitive fields
        self.assertNotIn('password', user_data)
        self.assertNotIn('is_superuser', user_data)
        
        self.assertEqual(user_data['employee_id'], 'EMP001')
        self.assertEqual(user_data['department'], 'Engineering')

    def test_reservations_include_nested_data(self):
        """Reservations endpoint includes proper relationship data"""
        url = reverse('reservation-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        reservation_data = response.data[0]
        
        # Check nested relationship fields
        self.assertEqual(reservation_data['user_name'], '')  # User has no first/last name
        self.assertEqual(reservation_data['desk_identifier'], '1.L.01')
        self.assertEqual(reservation_data['area_name'], 'Level 1 - Left Wing')
        self.assertEqual(reservation_data['status'], 'confirmed')

    def test_area_not_found_returns_404(self):
        """Non-existent area ID returns 404"""
        url = reverse('area-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_area_returns_empty_lists(self):
        """Area with no rooms/desks returns empty lists"""
        empty_area = Area.objects.create(name="Empty Floor")
        
        # Test desks endpoint
        url = reverse('area-desks', kwargs={'pk': empty_area.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # Test rooms endpoint
        url = reverse('area-rooms', kwargs={'pk': empty_area.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_desk_list_includes_all_relationship_data(self):
        """Desk list endpoint includes room and area names"""
        url = reverse('desk-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # All desks
        
        desk1_data = next(desk for desk in response.data if desk['identifier'] == '1.L.01')
        self.assertEqual(desk1_data['room_name'], 'Office 1.L.01')
        self.assertEqual(desk1_data['area_name'], 'Level 1 - Left Wing')
        self.assertEqual(desk1_data['status'], 'available')

    def test_room_list_includes_area_info(self):
        """Room list endpoint includes area names and desk counts"""
        url = reverse('room-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # All rooms
        
        room1_data = next(room for room in response.data if room['name'] == 'Office 1.L.01')
        self.assertEqual(room1_data['area_name'], 'Level 1 - Left Wing')
        self.assertEqual(room1_data['desk_count'], 2)  # room1 has 2 desks
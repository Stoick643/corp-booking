from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from datetime import date, timedelta
from core.models import Area, Room, Desk, Reservation, UserPermission

User = get_user_model()


class AreaModelTest(TestCase):
    """Test Area model functionality"""
    
    def test_area_creation_and_str(self):
        """Basic area creation and string representation"""
        area = Area.objects.create(name="Test Floor - Left Wing")
        self.assertEqual(str(area), "Test Floor - Left Wing")
        self.assertEqual(area.name, "Test Floor - Left Wing")
        self.assertFalse(area.map_svg)  # FileField is falsy when empty
        self.assertTrue(area.created_at)
        self.assertTrue(area.updated_at)


class RoomModelTest(TestCase):
    """Test Room model functionality"""
    
    def setUp(self):
        self.area = Area.objects.create(name="Level 1 - Test Wing")
    
    def test_room_area_relationship(self):
        """Room properly belongs to area"""
        room = Room.objects.create(
            area=self.area,
            name="Office 1.T.01",
            is_bookable=True
        )
        
        self.assertEqual(room.area, self.area)
        self.assertEqual(str(room), "Level 1 - Test Wing - Office 1.T.01")
        self.assertTrue(room.is_bookable)
        
        # Test reverse relationship
        self.assertIn(room, self.area.rooms.all())
        self.assertEqual(self.area.rooms.count(), 1)
    
    def test_room_unique_constraint(self):
        """Room names must be unique within an area"""
        Room.objects.create(area=self.area, name="Office 1.T.01")
        
        # This should raise IntegrityError due to unique_together constraint
        with self.assertRaises(IntegrityError):
            Room.objects.create(area=self.area, name="Office 1.T.01")


class DeskModelTest(TestCase):
    """Test Desk model functionality"""
    
    def setUp(self):
        self.area = Area.objects.create(name="Level 1 - Test Wing")
        self.room = Room.objects.create(area=self.area, name="Office 1.T.01")
    
    def test_desk_room_relationship(self):
        """Desk belongs to room, area accessible via room"""
        desk = Desk.objects.create(
            room=self.room,
            identifier="1.T.01",
            status='available',
            pos_x=100,
            pos_y=200
        )
        
        self.assertEqual(desk.room, self.room)
        self.assertEqual(desk.room.area, self.area)  # Area accessible via room
        self.assertEqual(str(desk), "Desk 1.T.01")
        self.assertEqual(desk.status, 'available')
        self.assertEqual(desk.pos_x, 100)
        self.assertEqual(desk.pos_y, 200)
        
        # Test reverse relationship
        self.assertIn(desk, self.room.desks.all())
    
    def test_desk_status_choices(self):
        """Desk status choices work correctly"""
        desk = Desk.objects.create(
            room=self.room,
            identifier="1.T.02",
            status='permanent'
        )
        self.assertEqual(desk.status, 'permanent')
        
        desk.status = 'disabled'
        desk.save()
        desk.refresh_from_db()
        self.assertEqual(desk.status, 'disabled')


class UserModelTest(TestCase):
    """Test custom User model functionality"""
    
    def test_user_custom_fields(self):
        """Employee ID, department, is_admin work correctly"""
        user = User.objects.create_user(
            username='john.doe',
            email='john.doe@company.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            employee_id='EMP001',
            department='Engineering',
            is_admin=True
        )
        
        self.assertEqual(user.employee_id, 'EMP001')
        self.assertEqual(user.department, 'Engineering')
        self.assertTrue(user.is_admin)
        self.assertEqual(user.get_full_name(), 'John Doe')
        self.assertTrue(user.check_password('password123'))
    
    def test_user_employee_id_unique(self):
        """Employee IDs must be unique"""
        User.objects.create_user(
            username='user1',
            employee_id='EMP001'
        )
        
        # This should raise IntegrityError due to unique constraint
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='user2',
                employee_id='EMP001'
            )


class ReservationModelTest(TestCase):
    """Test Reservation model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            employee_id='EMP001'
        )
        self.area = Area.objects.create(name="Level 1 - Test Wing")
        self.room = Room.objects.create(area=self.area, name="Office 1.T.01")
        self.desk = Desk.objects.create(
            room=self.room,
            identifier="1.T.01",
            status='available'
        )
    
    def test_reservation_creation(self):
        """Basic reservation creation works"""
        tomorrow = date.today() + timedelta(days=1)
        reservation = Reservation.objects.create(
            user=self.user,
            desk=self.desk,
            date=tomorrow,
            status='confirmed',
            notes='Test booking'
        )
        
        self.assertEqual(reservation.user, self.user)
        self.assertEqual(reservation.desk, self.desk)
        self.assertEqual(reservation.date, tomorrow)
        self.assertEqual(reservation.status, 'confirmed')
        self.assertEqual(reservation.notes, 'Test booking')
        self.assertTrue(reservation.created_at)
        self.assertIsNone(reservation.checked_in_at)
        
        expected_str = f"{self.user.username} - {self.desk.identifier} on {tomorrow}"
        self.assertEqual(str(reservation), expected_str)
    
    def test_reservation_prevents_double_booking(self):
        """Database constraint prevents double booking same desk/date"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Create first reservation
        Reservation.objects.create(
            user=self.user,
            desk=self.desk,
            date=tomorrow
        )
        
        # Create another user
        user2 = User.objects.create_user(
            username='testuser2',
            employee_id='EMP002'
        )
        
        # This should raise IntegrityError due to unique_together constraint
        with self.assertRaises(IntegrityError):
            Reservation.objects.create(
                user=user2,
                desk=self.desk,
                date=tomorrow
            )
    
    def test_reservation_status_choices(self):
        """Reservation status choices work correctly"""
        tomorrow = date.today() + timedelta(days=1)
        reservation = Reservation.objects.create(
            user=self.user,
            desk=self.desk,
            date=tomorrow,
            status='pending_approval'
        )
        
        self.assertEqual(reservation.status, 'pending_approval')
        
        reservation.status = 'checked_in'
        reservation.save()
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, 'checked_in')


class UserPermissionModelTest(TestCase):
    """Test UserPermission model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            employee_id='EMP001'
        )
        self.area1 = Area.objects.create(name="Level 1 - Left Wing")
        self.area2 = Area.objects.create(name="Level 2 - Right Wing")
    
    def test_user_permission_creation(self):
        """User permission creation and relationships work"""
        permission = UserPermission.objects.create(
            user=self.user,
            area=self.area1
        )
        
        self.assertEqual(permission.user, self.user)
        self.assertEqual(permission.area, self.area1)
        self.assertTrue(permission.created_at)
        
        expected_str = f"{self.user.username} can access {self.area1.name}"
        self.assertEqual(str(permission), expected_str)
        
        # Test reverse relationships
        self.assertIn(permission, self.user.area_permissions.all())
        self.assertIn(permission, self.area1.user_permissions.all())
    
    def test_user_permission_unique_constraint(self):
        """User can't have duplicate area access"""
        UserPermission.objects.create(
            user=self.user,
            area=self.area1
        )
        
        # This should raise IntegrityError due to unique_together constraint
        with self.assertRaises(IntegrityError):
            UserPermission.objects.create(
                user=self.user,
                area=self.area1
            )
    
    def test_user_multiple_area_access(self):
        """User can have access to multiple areas"""
        perm1 = UserPermission.objects.create(user=self.user, area=self.area1)
        perm2 = UserPermission.objects.create(user=self.user, area=self.area2)
        
        user_permissions = self.user.area_permissions.all()
        self.assertEqual(user_permissions.count(), 2)
        self.assertIn(perm1, user_permissions)
        self.assertIn(perm2, user_permissions)
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import random

from core.models import Area, Room, Desk, Reservation, UserPermission

User = get_user_model()


class Command(BaseCommand):
    help = 'Load realistic fixture data for workspace booking system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading fixtures',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        with transaction.atomic():
            self.stdout.write('Creating fixture data...')
            self.create_areas()
            self.create_rooms_and_desks()
            self.create_users()
            self.create_user_permissions()
            self.create_sample_reservations()
            
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded fixture data!')
        )
        self.print_summary()

    def clear_data(self):
        """Clear existing data in correct order (foreign keys)"""
        Reservation.objects.all().delete()
        UserPermission.objects.all().delete()
        Desk.objects.all().delete()
        Room.objects.all().delete()
        Area.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write('Existing data cleared.')

    def create_areas(self):
        """Creates the 6 office areas as specified in SRS requirements."""
        areas_data = [
            "Level 1 - Left Wing",
            "Level 1 - Right Wing", 
            "Level 2 - Left Wing",
            "Level 2 - Right Wing",
            "Level 3 - Left Wing",
            "Level 3 - Right Wing",
        ]
        
        for area_name in areas_data:
            area, created = Area.objects.get_or_create(name=area_name)
            if created:
                self.stdout.write(f'Created area: {area_name}')

    def create_rooms_and_desks(self):
        """Creates ~90 rooms and ~90 desks with realistic IDs matching floor plans."""
        desk_patterns = [
            # Level 1 Left Wing
            ("1", "L", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15"]),
            # Level 1 Right Wing  
            ("1", "R", ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]),
            # Level 2 Left Wing
            ("2", "L", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15"]),
            # Level 2 Right Wing
            ("2", "R", ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]),
            # Level 3 Left Wing
            ("3", "L", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15"]),
            # Level 3 Right Wing
            ("3", "R", ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]),
        ]

        for level, wing, room_numbers in desk_patterns:
            # Get the area
            area_name = f"Level {level} - {wing}eft Wing" if wing == "L" else f"Level {level} - Right Wing"
            area = Area.objects.get(name=area_name)
            
            for room_num in room_numbers:
                # Create room
                room_name = f"Office {level}.{wing}.{room_num}"
                room, created = Room.objects.get_or_create(
                    area=area,
                    name=room_name,
                    defaults={'is_bookable': True}
                )
                
                if created:
                    # Create 1 desk per room (some rooms might have 2 in reality)
                    desk_id = f"{level}.{wing}.{room_num}"
                    
                    # Random coordinates for map positioning
                    pos_x = random.randint(50, 800) if random.random() > 0.3 else None
                    pos_y = random.randint(50, 600) if pos_x else None
                    
                    # Random status distribution: 80% available, 15% permanent, 5% disabled
                    status_choice = random.choices(
                        ['available', 'permanent', 'disabled'],
                        weights=[80, 15, 5]
                    )[0]
                    
                    desk, desk_created = Desk.objects.get_or_create(
                        room=room,
                        identifier=desk_id,
                        defaults={
                            'status': status_choice,
                            'pos_x': pos_x,
                            'pos_y': pos_y
                        }
                    )
                    
                    if desk_created:
                        self.stdout.write(f'Created room {room_name} with desk {desk_id}')

    def create_users(self):
        """Creates 150 test employees with employee IDs EMP001-150 and departments."""
        departments = [
            'Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 
            'Operations', 'Product', 'Design', 'Legal', 'IT'
        ]
        
        first_names = [
            'John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa',
            'Tom', 'Anna', 'Mark', 'Jessica', 'Paul', 'Michelle', 'Steve'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 
            'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez'
        ]

        for i in range(1, 151):  # EMP001 to EMP150
            emp_id = f"EMP{i:03d}"
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}.{last_name.lower()}.{i}"
            email = f"{username}@company.com"
            department = random.choice(departments)
            
            # 10% chance to be admin
            is_admin = random.random() < 0.1
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'employee_id': emp_id,
                    'department': department,
                    'is_admin': is_admin,
                    'is_active': True
                }
            )
            
            if created:
                user.set_password('password123')  # Default password for testing
                user.save()
                
                if i % 30 == 0:  # Progress indicator
                    self.stdout.write(f'Created {i} users...')

        self.stdout.write('Created 150 test users')

    def create_user_permissions(self):
        """Assigns users to areas they can access for testing access control."""
        areas = list(Area.objects.all())
        users = User.objects.filter(is_superuser=False)
        
        for user in users:
            # Each user gets access to 1-3 areas (realistic for employees)
            num_areas = random.choices([1, 2, 3], weights=[60, 30, 10])[0]
            user_areas = random.sample(areas, num_areas)
            
            for area in user_areas:
                UserPermission.objects.get_or_create(
                    user=user,
                    area=area
                )
                
        self.stdout.write('Assigned area permissions to users')

    def create_sample_reservations(self):
        """Creates realistic booking patterns for last 2 weeks for demo/testing."""
        # Get available desks and users
        available_desks = Desk.objects.filter(status='available')
        users = User.objects.filter(is_superuser=False)
        
        # Create bookings for the past 2 weeks
        start_date = date.today() - timedelta(days=14)
        end_date = date.today() - timedelta(days=1)
        
        current_date = start_date
        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                # Simulate 60% occupancy rate
                num_bookings = int(len(available_desks) * 0.6)
                
                # Random sample of desks and users
                booked_desks = random.sample(list(available_desks), num_bookings)
                booking_users = random.sample(list(users), num_bookings)
                
                for desk, user in zip(booked_desks, booking_users):
                    # Check if user has permission to this area
                    if UserPermission.objects.filter(
                        user=user, 
                        area=desk.room.area
                    ).exists():
                        
                        # Random status distribution
                        status = random.choices(
                            ['confirmed', 'checked_in', 'no_show'],
                            weights=[20, 70, 10]  # Most people check in
                        )[0]
                        
                        reservation, created = Reservation.objects.get_or_create(
                            user=user,
                            desk=desk,
                            date=current_date,
                            defaults={'status': status}
                        )
                        
            current_date += timedelta(days=1)
            
        reservation_count = Reservation.objects.count()
        self.stdout.write(f'Created {reservation_count} sample reservations')

    def print_summary(self):
        """Print summary of created data"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('FIXTURE DATA SUMMARY:')
        self.stdout.write('='*50)
        self.stdout.write(f'Areas: {Area.objects.count()}')
        self.stdout.write(f'Rooms: {Room.objects.count()}')
        self.stdout.write(f'Desks: {Desk.objects.count()}')
        self.stdout.write(f'Users: {User.objects.filter(is_superuser=False).count()}')
        self.stdout.write(f'User Permissions: {UserPermission.objects.count()}')
        self.stdout.write(f'Reservations: {Reservation.objects.count()}')
        self.stdout.write('\nDESK STATUS DISTRIBUTION:')
        for status, label in Desk.STATUS_CHOICES:
            count = Desk.objects.filter(status=status).count()
            self.stdout.write(f'{label}: {count}')
        self.stdout.write('='*50)
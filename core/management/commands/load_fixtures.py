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
        """Creates ~30 rooms and ~90 desks with realistic distribution (6→30→90 hierarchy)."""
        
        # Define realistic room types and desk counts per area
        room_types = [
            {'name': 'Open Office A', 'desk_count': 6, 'type': 'open'},
            {'name': 'Open Office B', 'desk_count': 4, 'type': 'open'},
            {'name': 'Meeting Room', 'desk_count': 0, 'type': 'meeting'},
            {'name': 'Individual Office 1', 'desk_count': 1, 'type': 'private'},
            {'name': 'Individual Office 2', 'desk_count': 1, 'type': 'private'},
            {'name': 'Shared Office', 'desk_count': 3, 'type': 'shared'},
        ]
        
        areas = Area.objects.all().order_by('name')
        desk_counter = 1
        
        for area in areas:
            level = area.name.split()[1]  # Extract "1", "2", "3"
            wing = "L" if "Left" in area.name else "R"
            
            self.stdout.write(f'Creating rooms and desks for {area.name}')
            
            # Create 5 rooms per area (6 areas × 5 = 30 rooms total)
            for i, room_config in enumerate(room_types[:5], 1):  # Take first 5 room types
                room_name = f"{level}.{wing} - {room_config['name']}"
                
                room, created = Room.objects.get_or_create(
                    area=area,
                    name=room_name,
                    defaults={
                        'is_bookable': room_config['type'] == 'meeting'
                    }
                )
                
                if created:
                    # Create desks for this room
                    desks_to_create = room_config['desk_count']
                    
                    # Adjust desk count to reach exactly 90 total desks
                    # (6 areas × 15 desks average = 90 desks)
                    if area == areas.last() and i == 5:  # Last room of last area
                        remaining_desks = 90 - (desk_counter - 1)
                        desks_to_create = remaining_desks
                    
                    for desk_num in range(desks_to_create):
                        desk_identifier = f"{level}.{wing}.{desk_counter:02d}"
                        
                        # Position calculation based on room type
                        if room_config['type'] == 'open':
                            # Open office - arranged in grid
                            pos_x = 100 + (desk_num % 3) * 150
                            pos_y = 100 + (desk_num // 3) * 100
                        elif room_config['type'] == 'private':
                            # Private office - center of room
                            pos_x = 200
                            pos_y = 150
                        elif room_config['type'] == 'shared':
                            # Shared office - around table
                            pos_x = 150 + (desk_num * 80)
                            pos_y = 120
                        else:
                            # Random positioning
                            pos_x = random.randint(50, 400)
                            pos_y = random.randint(50, 300)
                        
                        # Status distribution: 75% available, 20% permanent, 5% disabled
                        status_choice = random.choices(
                            ['available', 'permanent', 'disabled'],
                            weights=[75, 20, 5]
                        )[0]
                        
                        desk, desk_created = Desk.objects.get_or_create(
                            room=room,
                            identifier=desk_identifier,
                            defaults={
                                'status': status_choice,
                                'pos_x': pos_x,
                                'pos_y': pos_y
                            }
                        )
                        
                        if desk_created:
                            desk_counter += 1
                    
                    if desks_to_create > 0:
                        self.stdout.write(f'  Created {room_name} with {desks_to_create} desks')
                    else:
                        self.stdout.write(f'  Created {room_name} (meeting room, no desks)')
        
        self.stdout.write(f'Total desks created: {desk_counter - 1}')

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
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser"""
    employee_id = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Employee ID (e.g., 'EMP001')"
    )
    is_admin = models.BooleanField(
        default=False,
        help_text="Designates whether this user is an administrator"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Employee's department"
    )


class Area(models.Model):
    """Represents a bookable area/floor in the office"""
    name = models.CharField(max_length=100, unique=True)
    map_svg = models.FileField(
        upload_to='floor_plans/', 
        null=True, 
        blank=True,
        help_text="SVG file for the floor plan visual"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    """Represents a room within an area"""
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    name = models.CharField(
        max_length=100,
        help_text="Room name or identifier (e.g., 'Office 1.14', 'Meeting Room A')"
    )
    is_bookable = models.BooleanField(
        default=True,
        help_text="Whether the entire room can be booked"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['area', 'name']
        unique_together = ['area', 'name']

    def __str__(self):
        return f"{self.area.name} - {self.name}"


class Desk(models.Model):
    """Represents a bookable desk"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('permanent', 'Permanently Assigned'),
        ('disabled', 'Disabled'),
    ]

    identifier = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Unique desk identifier (e.g., '1.L.12')"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available'
    )
    pos_x = models.IntegerField(
        null=True, 
        blank=True,
        help_text="X-coordinate for map view"
    )
    pos_y = models.IntegerField(
        null=True, 
        blank=True,
        help_text="Y-coordinate for map view"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='desks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['identifier']

    def __str__(self):
        return f"Desk {self.identifier}"


class Reservation(models.Model):
    """Represents a desk booking by a user"""
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending_approval', 'Pending Approval'),
        ('checked_in', 'Checked In'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    desk = models.ForeignKey(
        Desk,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='confirmed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-created_at']
        unique_together = ['desk', 'date']  # Prevent double booking
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['desk', 'date']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.desk.identifier} on {self.date}"


class UserPermission(models.Model):
    """Links users to areas they can access"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='area_permissions'
    )
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name='user_permissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'area']
        ordering = ['user', 'area']

    def __str__(self):
        return f"{self.user.username} can access {self.area.name}"

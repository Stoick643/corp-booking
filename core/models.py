from django.db import models


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
    area = models.ForeignKey(
        Area,
        on_delete=models.CASCADE,
        related_name='desks',
        null=True,  # Temporary, will be required later when we add Room
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['identifier']

    def __str__(self):
        return f"Desk {self.identifier}"

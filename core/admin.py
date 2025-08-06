from django.contrib import admin
from .models import Area, Desk


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'map_svg', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'area', 'status', 'pos_x', 'pos_y']
    list_filter = ['status', 'area']
    search_fields = ['identifier']
    readonly_fields = ['created_at', 'updated_at']

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Area, Room, Desk, Reservation, UserPermission


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'employee_id', 'department', 'is_admin', 'is_staff']
    list_filter = ['is_admin', 'is_staff', 'is_active', 'department']
    search_fields = ['username', 'email', 'employee_id']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Employee Info', {
            'fields': ('employee_id', 'department', 'is_admin')
        }),
    )


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'room_count', 'desk_count', 'map_svg', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [RoomInline]
    
    def room_count(self, obj):
        return obj.rooms.count()
    room_count.short_description = 'Rooms'
    
    def desk_count(self, obj):
        return Desk.objects.filter(room__area=obj).count()
    desk_count.short_description = 'Desks'


class DeskInline(admin.TabularInline):
    model = Desk
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'area', 'is_bookable', 'desk_count', 'created_at']
    list_filter = ['area', 'is_bookable']
    search_fields = ['name', 'area__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DeskInline]
    
    def desk_count(self, obj):
        return obj.desks.count()
    desk_count.short_description = 'Desks'


@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = ['identifier', 'room', 'area_name', 'status', 'pos_x', 'pos_y']
    list_filter = ['status', 'room__area']
    search_fields = ['identifier', 'room__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def area_name(self, obj):
        return obj.room.area.name
    area_name.short_description = 'Area'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['user', 'desk', 'date', 'status', 'created_at']
    list_filter = ['status', 'date', 'desk__room__area']
    search_fields = ['user__username', 'desk__identifier']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'area', 'created_at']
    list_filter = ['area']
    search_fields = ['user__username', 'area__name']

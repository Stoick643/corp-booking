from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, AreaViewSet, RoomViewSet, 
    DeskViewSet, ReservationViewSet
)

# Router configuration for all API endpoints:
# - /api/users/ - list users
# - /api/areas/ - list all areas
# - /api/areas/{id}/ - get specific area
# - /api/areas/{id}/rooms/ - list rooms in area
# - /api/areas/{id}/desks/ - list desks in area
# - /api/rooms/ - list all rooms
# - /api/rooms/{id}/desks/ - list desks in room
# - /api/desks/ - list all desks
# - /api/reservations/ - list all reservations

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'areas', AreaViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'desks', DeskViewSet)
router.register(r'reservations', ReservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
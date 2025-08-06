# Corporate Workspace Booking System

A Django-based workspace booking system for managing office desk reservations with real-time updates and interactive floor plans.

## Quick Start

### Prerequisites
- Python 3.12+
- pip-tools

### Setup
```bash
# Clone and navigate to project
git clone https://github.com/Stoick643/corp-booking.git
cd corp-booking

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip-sync requirements/dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load realistic fixture data (6 areas, 90 rooms, 90 desks, 150 users)
python manage.py load_fixtures

# Start development server
./run_server.sh
# OR: python manage.py runserver
```

### URLs
- **API:** http://localhost:8000/api/
- **Admin:** http://localhost:8000/admin/

## Development

### Running Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test booking_api

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Schema (Per SRS Section 5)

```
Area (6 total - office areas)
├── id (PK)
├── name (e.g., "1st Floor - Left Wing")  
└── map_svg (SVG floor plan file)

Room (per area, ~15 each)
├── id (PK)
├── area (FK → Area)
├── name (e.g., "Office 1.14")
└── is_bookable (Boolean)

Desk (~90 total, ~1-2 per room)
├── id (PK) 
├── room (FK → Room)
├── identifier (e.g., "1.L.12")
├── status (Available/Permanent/Disabled)
├── pos_x, pos_y (coordinates for map)

User (150 employees for 60% occupancy)
├── Standard Django User fields
├── employee_id
└── is_admin

Reservation (bookings)
├── id (PK)
├── user (FK → User)  
├── desk (FK → Desk)
├── date
├── status (Confirmed/Pending/CheckedIn/NoShow)
├── created_at
└── checked_in_at

UserPermission (access control)
├── user (FK → User)
└── area (FK → Area)
```

### API Endpoints

```
# Users
GET /api/users/                    # List all users

# Areas
GET /api/areas/                    # List all areas with room/desk counts
GET /api/areas/{id}/               # Area details
GET /api/areas/{id}/rooms/         # Rooms in area
GET /api/areas/{id}/desks/         # All desks in area (across rooms)

# Rooms
GET /api/rooms/                    # List all rooms
GET /api/rooms/{id}/               # Room details
GET /api/rooms/{id}/desks/         # Desks in specific room

# Desks  
GET /api/desks/                    # List all desks with room/area info

# Reservations (Read-only for now)
GET /api/reservations/             # List all reservations
```

## Business Rules

- **Booking Quota:** 3 weekdays max per calendar week
- **Advance Booking:** Up to 3 weeks in future
- **Exception Workflow:** 4th booking requires admin approval
- **Real-time Updates:** WebSocket updates for desk status changes

## Technology Stack

- **Backend:** Django 5.0.7 + Django REST Framework
- **Frontend:** Vue.js 3 (planned)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Real-time:** Django Channels
- **Deployment:** Render.com

## Project Structure

```
booking/
├── core/                  # Models, admin
├── booking_api/          # REST API endpoints  
├── booking_system/       # Django settings
├── requirements/         # pip-tools dependencies
├── media/               # Uploaded files (SVG floor plans)
├── docs/                # SRS and floor plan images
└── venv/                # Virtual environment
```
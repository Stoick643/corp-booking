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
- **Frontend:** http://localhost:5173/ (Vue.js dev server)

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
POST /api/reservations/            # Create new reservation
```

## Vue.js Frontend

### Setup and Development

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies
npm install

# Start development server (requires Django running on port 8000)
npm run dev

# Build for production
npm run build
```

### Frontend URLs
- **Development:** http://localhost:5173/
- **Areas View:** http://localhost:5173/
- **Rooms View:** http://localhost:5173/areas/{id}
- **Desks View:** http://localhost:5173/areas/{areaId}/rooms/{roomId}
- **Booking:** http://localhost:5173/desks/{deskId}/book

### Manual Testing Workflow

1. **Start Backend:**
   ```bash
   # Terminal 1: Django API server
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Start Frontend:**
   ```bash
   # Terminal 2: Vue.js dev server
   cd frontend/
   npm run dev
   ```

3. **Test Complete Booking Flow:**
   - Navigate to http://localhost:5173/
   - Click on any office area (e.g., "Level 1 - Left Wing")
   - Select a room with available desks
   - Click on an available (green) desk
   - Fill out the booking form and submit
   - Verify booking success modal appears

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/           # Reusable Vue components
│   │   ├── NavigationBar.vue    # Top navigation with breadcrumbs
│   │   ├── AreaCard.vue         # Individual area display
│   │   ├── RoomCard.vue         # Individual room display  
│   │   ├── DeskCard.vue         # Individual desk display
│   │   └── BookingForm.vue      # Reservation form
│   ├── views/               # Page-level components
│   │   ├── AreasView.vue        # Areas list page
│   │   ├── RoomsView.vue        # Rooms list page
│   │   ├── DesksView.vue        # Desks list page
│   │   └── BookingView.vue      # Booking form page
│   ├── services/           # API integration
│   │   └── api.js              # Axios HTTP client for Django API
│   ├── stores/             # State management
│   │   └── booking.js          # Reactive store for app state
│   ├── router/             # Vue Router configuration
│   │   └── index.js            # Route definitions
│   └── styles/             # Global styles
│       └── main.css            # Bootstrap overrides and custom CSS
├── package.json            # Dependencies and scripts
├── vite.config.js         # Vite dev server configuration
└── index.html             # Main HTML template
```

### Key Features Implemented

- **Responsive Design:** Bootstrap 5 with mobile-first approach
- **Real-time Navigation:** Vue Router with breadcrumb navigation  
- **API Integration:** Axios client consuming Django REST API
- **Form Validation:** Client-side validation with error handling
- **Loading States:** Spinners and loading indicators
- **Error Handling:** Global error display with user-friendly messages
- **Status Filtering:** Filter desks by availability status
- **Booking Workflow:** Complete end-to-end reservation process

### Test Data Available

- **6 Office Areas:** Level 1-3, Left/Right Wings
- **30 Rooms:** 5 rooms per area (Open Office, Meeting, Private, Shared)
- **90 Desks:** 66 available, 19 permanent, 5 disabled
- **150 Users:** Realistic employee data with departments
- **126 Sample Reservations:** Historical booking data for testing

## Business Rules

- **Booking Quota:** 3 weekdays max per calendar week
- **Advance Booking:** Up to 3 weeks in future
- **Exception Workflow:** 4th booking requires admin approval
- **Real-time Updates:** WebSocket updates for desk status changes

## Technology Stack

- **Backend:** Django 5.0.7 + Django REST Framework
- **Frontend:** Vue.js 3 + Vite + Bootstrap 5
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Real-time:** Django Channels (planned)
- **Deployment:** Render.com (planned)

## Project Structure

```
booking/
├── core/                  # Models, admin
├── booking_api/          # REST API endpoints  
├── booking_system/       # Django settings
├── frontend/             # Vue.js 3 frontend application
│   ├── src/             # Vue.js source code
│   ├── package.json     # Node.js dependencies
│   └── vite.config.js   # Vite configuration
├── requirements/         # pip-tools dependencies
├── media/               # Uploaded files (SVG floor plans)
├── docs/                # SRS and floor plan images
└── venv/                # Virtual environment
```
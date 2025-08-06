
### **Software Requirements Specification (SRS): Workspace Booking System**
* **Version:** 1.2
* **Date:** August 6, 2025

### 1. Introduction
This document outlines the requirements for the Workspace Booking System, a web application designed to manage and streamline office desk reservations. The system will provide employees with an interactive, real-time view of office layouts to book available desks, while giving administrators the tools to manage users, spaces, booking policies, and analyze usage patterns.

---

### 2. User Roles & Personas
The system will support two primary user roles with distinct permissions:

* **Employee (Standard User):**
    * Can view floor plans for areas they are permitted to access.
    * Can book available desks for themselves within policy limits.
    * Can view their own upcoming reservations.
    * Can cancel their own reservations.

* **Administrator:**
    * Has all the capabilities of an Employee.
    * Can view and manage all areas, rooms, desks, and users.
    * Can book desks on behalf of any employee (to be implemented post-v1).
    * Can approve or deny booking requests that exceed user quotas.
    * Can configure user permissions, assigning employees to specific work areas.
    * Can designate desks as permanently assigned or disabled.
    * Is responsible for uploading and managing floor plan layouts.

---

### 3. Functional Requirements

#### 3.1. User Authentication
* **3.1.1. Login:** For development and initial rollout, the system will support a standard username/password login system.
* **3.1.2. Single Sign-On (SSO):** For production, the system should be designed to integrate with a corporate SSO provider (e.g., Google Workspace, Microsoft 365) to allow seamless and secure user login.
* **3.1.3. Logout:** Users must be able to log out of the system.

#### 3.2. Workspace Viewing & Navigation
* **3.2.1. Area Selection:** Users will select one of the 6 office areas from a dropdown menu.
* **3.2.2. Date Selection:** A calendar interface will allow users to select a date up to 3 weeks in the future to view availability.
* **3.2.3. Modular Visual Views:** The system will support two distinct visual modes for displaying an area:
    * **Map View:** An interactive view displaying an SVG floor plan (`tloris`) with clickable desk icons overlaid at their specific `x,y` coordinates. This is the primary view.
    * **Schematic View:** A block-based or list-based view that groups desks by room. This view does not require an SVG file and serves as a fallback or alternative.
* **3.2.4. Real-Time Status:** Desk availability (Available, Reserved, Permanent) must be displayed in real-time using a clear color-code (e.g., Green, Red, Grey).

#### 3.3. Desk Reservation Management
* **3.3.1. Create Booking:** An authenticated employee can book an available desk by clicking on it in either view and confirming.
* **3.3.2. Booking Quota:** A user can book a maximum of **3 weekdays** (Mon-Fri) per calendar week (Mon-Sun). Weekend bookings do not count towards this quota.
* **3.3.3. Exception Workflow:** If a user attempts to book a 4th weekday, the system will issue a warning and create the reservation with a "Pending Approval" status. An administrator must approve it.
* **3.3.4. Cancellation:** Users can cancel any of their future bookings. Doing so will credit the day back to their weekly quota if applicable.
* **3.3.5. Recurring Bookings:** Users can make a recurring booking for the same desk on a weekly basis, up to the 3-week advance limit.

#### 3.4. Administrator Panel
* The system will feature a comprehensive admin panel (using the built-in Django Admin) for all management tasks.
* **3.4.1. User Management:** Admins can add, edit, and remove users.
* **3.4.2. Access Control:** Admins can assign users or groups of users to specific, bookable `Areas`.
* **3.4.3. Space Management:** Admins can create and edit `Areas`, `Rooms`, and `Desks`, including their `x,y` coordinates for the map view and uploading SVG files.
* **3.4.4. Reservation Approval:** A dedicated view will show admins all "Pending Approval" reservations for them to approve or deny.

#### 3.5. Live Simulation Mode
* The system will include a marketing/demo feature that simulates a day's booking activity.
* **3.5.1. Probabilistic Bookings:** The simulation will be based on a configurable daily participation rate (e.g., 50% of employees).
* **3.5.2. Time Compression:** The simulation will compress an 8-hour workday into approximately 5 minutes.
* **3.5.3. Advance Booking Simulation:** The simulation will reflect the primary use case of users booking for the next day during the afternoon of the current day.

#### 3.6. Analytics & Reporting Dashboard
* The system will include a dedicated dashboard within the Admin Panel to provide insights into workspace utilization.
* **3.6.1. Key Metrics & KPIs:** The dashboard will display key statistics which can be filtered by date range (e.g., This Week, Last Month) and by `Area`.
    * **Occupancy Rate:** The percentage of bookable desks that were reserved.
    * **Peak Usage Days:** A breakdown of which days of the week are most popular.
    * **Popularity Analysis:** Reports on the most frequently booked `Areas` and individual `Desks` ("hot desks").
* **3.6.2. Data Visualizations:** Data will be presented using a mix of clear, interactive charts and visuals.
    * Bar charts for comparing usage across days of the week and different `Areas`.
    * A **Heatmap** overlay on the floor plan view to visually represent desk popularity.
* **3.6.3. User Check-in & No-Show Tracking:** To enable accurate usage data, a check-in system will be implemented.
    * A reservation will have a "Check-in" button that is active on the day of the booking (e.g., from 8:00 AM to 12:00 PM).
    * If a user fails to check in, their reservation will be marked as a "No-Show." The dashboard will report the no-show rate.

---

### 4. Non-Functional Requirements

#### 4.1. Security
* **4.1.1. API Protection:** All API endpoints must be secured. Authentication is required for all actions, and permission checks must be performed on every request.
* **4.1.2. Authorization:** A user must not be able to view or book in an area they are not assigned to. Admin endpoints must be inaccessible to regular users.

#### 4.2. Performance
* **4.2.1. Real-Time Updates:** When a desk is booked, the change must be reflected on the screens of all other active users viewing that area in near real-time (sub-second) using WebSockets.
* **4.2.2. Concurrency:** The backend must safely handle concurrent booking attempts on the same desk using database transactions to prevent double-bookings.

#### 4.3. Usability & Reliability
* **4.3.1. Graceful Fallback:** If an `Area`'s SVG map fails to load or does not exist, the UI must gracefully and automatically fall back to the `SchematicView`.
* **4.3.2. Timezone Consistency:** All date/time data will be stored in the database in UTC. The frontend will be responsible for converting and displaying times in the user's local timezone.

#### **4.4. Architectural Principles**
* **4.4.1. Modular View Architecture:** The frontend architecture must decouple the office layout data from its visual representation. The system shall support interchangeable "view components" (or "plug-ins") for displaying an `Area`. The initial implementation will include two such components: a `MapView` (for SVG-based floor plans) and a `SchematicView` (for block-based layouts). The system must be designed so that new view types could be added in the future with minimal changes to the core application logic.

---

### 5. Data Model
The system will use a hierarchical relational model to represent the office space and booking information.

#### **Area Model**
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | Primary Key | Unique ID for the area. |
| `name` | Text | Descriptive name (e.g., "1st Floor - Left Wing"). |
| **`map_svg`** | **File** | **The SVG file for the floor plan visual. This field is optional (can be null).** |

#### **Room Model**
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | Primary Key | Unique ID for the room. |
| `area` | Foreign Key | Links this room to a parent `Area`. |
| `name` | Text | The room's name or identifier. |
| `is_bookable` | Boolean | Flags if the entire room can be booked. |

#### **Desk Model**
| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `id` | Primary Key | Unique ID for the desk. |
| `room` | Foreign Key | Links this desk to a parent `Room`. |
| `identifier` | Text | A unique label for the desk (e.g., "1.L.12"). |
| `status` | Text (Choices) | The current availability status: `Available`, `Permanent`, `Disabled`. |
| `pos_x` | Integer | The X-coordinate for the map. Optional. |
| `pos_y` | Integer | The Y-coordinate for the map. Optional. |

#### **Other Core Models**
* **User:** Stores employee information, credentials, and admin status.
* **Reservation:** Links a `User` to a `Desk` for a specific `date`. Contains a reservation status (e.g., `Confirmed`, `Pending Approval`, `Checked-in`, `No-show`).
* **UserPermissions:** A linking table to manage which `Users` have access to which `Areas`.

---

### 6. Technology Stack

* **Backend:** Python with the **Django** framework.
* **API:** **Django REST Framework (DRF)**.
* **Real-Time:** **Django Channels** for WebSocket communication.
* **Frontend:** A JavaScript framework, either **React** or **Vue.js**.
* **Database:** **SQLite** for development, **PostgreSQL** for production.
* **Deployment:** To be hosted on a cloud platform like **Render**.

---

### 7. Out of Scope (Future Versions)

* **V1.1:** A fully responsive mobile-web interface.
* **V1.2:** Integration with calendar services (e.g., Google Calendar, Outlook).
* **V2.0:** Booking for assets other than desks (e.g., meeting rooms, parking spots).
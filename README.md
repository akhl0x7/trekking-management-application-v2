# Trekking Management Application V2

A full-stack trekking operations platform for managing trekking events, staff assignments, participant bookings, operational status, reporting, caching, and asynchronous background work.

## Overview

The application models three roles:

- Admin
- Trek Staff
- Trekker

The primary workflow is:

```text
Create Trek
    ↓
Approve Trek
    ↓
Assign Staff
    ↓
Open Trek
    ↓
Trekker Booking
    ↓
Trek Starts
    ↓
Trek Completes
    ↓
Historical Record
```

## Architecture

```text
Vue 3 + Bootstrap
        │
        │ HTTP / JSON
        ▼
    Flask REST API
        │
   ┌────┴─────┐
   ▼          ▼
 SQLite     Redis
              │
              ▼
            Celery
          /    │    \
         /     │     \
 reminders  reports  exports
```

The backend owns authentication, authorization, state transitions, validation, booking integrity, and persistence.

## Technology Stack

- Python 3.12+
- Flask
- Flask-SQLAlchemy
- Vue 3
- Vue Router
- Bootstrap 5
- SQLite
- Redis
- Celery
- Vite

## Roles

### Admin

- Dashboard and trekking statistics
- Trek creation and management
- Trek approval
- Staff provisioning
- Staff activation/deactivation/blacklisting
- Staff assignment and unassignment
- User management
- Booking overview
- Search
- Activity reports

### Trek Staff

- Assigned trek dashboard
- Available-slot management
- Trek opening/closing
- Trek start/completion tracking
- Participant list management

### Trekker

- Registration and login
- Trek discovery
- Search and filtering
- Booking and cancellation
- Booking history
- Profile management
- Asynchronous CSV export

## Domain Model

```text
User
 ├── TrekkerProfile
 └── StaffProfile

Trek
 ├── TrekStaffAssignment
 └── Booking
        └── User

ExportJob
 └── User
```

## Trek Lifecycle

```text
PENDING
   ↓
APPROVED
   ↓
OPEN
   ↓
CLOSED
   ↓
COMPLETED
```

The backend exposes explicit state transitions instead of allowing arbitrary status changes.

## Data Integrity

The system protects the following invariants:

```text
capacity > 0
0 <= available_slots <= capacity
active bookings <= capacity
at most one active booking per user and trek
bookings require an OPEN trek
only assigned staff can manage a trek
completed treks cannot be reopened through the normal lifecycle
historical bookings remain stored
```

Booking capacity is reserved with a conditional database update inside the booking transaction. Duplicate active bookings are protected by a database uniqueness rule.

## Background Processing

Celery handles three background workflows:

### Daily reminders

Finds bookings for upcoming treks and sends reminders through the configured notification channel.

### Monthly activity report

Generates an HTML activity report containing conducted treks, participating users, and popular treks, then delivers a notification to the configured administrator.

### Booking-history export

Generates a user-specific CSV asynchronously and exposes the completed export through the application.

## Caching

Redis is used for frequently accessed trek reads with explicit TTLs.

Cached data is invalidated after mutable operations such as booking, cancellation, assignment changes, and trek updates.

Redis failure does not prevent database-backed reads and writes from functioning.

## Repository Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── celery_app.py
│   │   ├── tasks.py
│   │   └── seed.py
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   └── router/
│   └── package.json
├── docs/
├── .github/workflows/ci.yml
└── docker-compose.yml
```

## Local Development

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app run.py init-db
.\.venv\Scripts\python.exe -m flask --app run.py seed
.\.venv\Scripts\python.exe run.py
```

The API runs at `http://127.0.0.1:5000`.

### Redis

Run Redis locally or with Docker:

```powershell
docker compose up -d redis
```

### Celery Worker

From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m celery -A app.celery_runner.celery worker --loglevel=INFO
```

### Celery Beat

From `backend/`:

```powershell
..\.venv\Scripts\python.exe -m celery -A app.celery_runner.celery beat --loglevel=INFO
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://127.0.0.1:5173`.

## Docker

```powershell
docker compose up --build
```

Services:

- frontend
- backend
- redis
- celery-worker
- celery-beat

## Demo Accounts

```text
Admin
admin@tma.local / Admin@12345

Staff
staff@example.com / Staff@12345

Trekker
trekker@example.com / Trekker@12345
```

These credentials are intended for local development only.

## Testing

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

The test suite covers authentication, role authorization, trek state transitions, capacity constraints, duplicate bookings, and full-trek rejection.

## Documentation

- `docs/requirements.md` — requirement traceability
- `docs/domain-model.md` — entities and relationships
- `docs/architecture.md` — component boundaries
- `docs/correctness.md` — invariants and correctness arguments
- `docs/api.md` — REST endpoints
- `docs/decisions.md` — design decisions
- `docs/test-plan.md` — verification matrix

## License

For educational and portfolio use.

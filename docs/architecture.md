# Architecture

## Layers

```text
Vue UI
  ↓
HTTP API
  ↓
Domain Services
  ↓
SQLAlchemy Models
  ↓
SQLite
```

Redis sits beside SQLite for read caching. Celery consumes jobs through Redis for asynchronous processing.

## API Layer

The API layer handles:

- authentication context
- authorization
- request parsing
- response formatting
- HTTP error translation

It does not own core booking or lifecycle decisions.

## Service Layer

The service layer owns:

- password verification
- trek validation
- trek state transitions
- booking transactions
- cache invalidation
- report generation
- notification delivery

## Database

SQLite is the persistent source of truth. Foreign keys are enabled explicitly. Constraints and indexes protect critical relationships and invariants.

## Frontend

Vue Router provides route-level authorization. The frontend uses the browser Fetch API and a small API wrapper; no client-side state library is required.

Vite proxies `/api` requests to Flask during development.

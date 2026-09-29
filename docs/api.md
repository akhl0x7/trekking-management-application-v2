# API

All endpoints are under `/api/v1`.

## Public

```text
GET /health
GET /treks
GET /treks/:id
```

Supported trek filters:

```text
search
difficulty
location
duration
status
```

## Authentication

```text
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
```

## Admin

```text
GET    /admin/dashboard
GET    /admin/treks
POST   /admin/treks
GET    /admin/treks/:id
PATCH  /admin/treks/:id
DELETE /admin/treks/:id
POST   /admin/treks/:id/approve
POST   /admin/treks/:id/assign
POST   /admin/treks/:id/unassign
GET    /admin/staff
POST   /admin/staff
PATCH  /admin/staff/:id/status
GET    /admin/users
PATCH  /admin/users/:id/status
GET    /admin/bookings
GET    /admin/reports
```

## Staff

```text
GET   /staff/dashboard
GET   /staff/treks
GET   /staff/treks/:id/participants
PATCH /staff/treks/:id
POST  /staff/treks/:id/start
POST  /staff/treks/:id/complete
```

## Trekker

```text
GET   /trekker/dashboard
GET   /trekker/bookings
GET   /trekker/history
POST  /trekker/treks/:id/book
POST  /trekker/bookings/:id/cancel
GET   /trekker/profile
PATCH /trekker/profile
POST  /trekker/exports
GET   /trekker/exports/:id
GET   /trekker/exports/:id/download
```

## Response format

Success:

```json
{
  "data": {},
  "error": null
}
```

Failure:

```json
{
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

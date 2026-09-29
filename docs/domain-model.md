# Domain Model

## User

Stores authentication identity and role. The role is one of `ADMIN`, `STAFF`, or `TREKKER`.

## TrekkerProfile

Stores optional trekker contact and emergency information.

## StaffProfile

Stores staff-specific employee information.

## Trek

Stores the trekking event, location, difficulty, duration, capacity, availability, dates, lifecycle status, instructions, and operational timestamps.

## TrekStaffAssignment

Associates staff profiles with treks and preserves assignment state and timestamps.

## Booking

Associates a trekker with a trek and stores booking state, payment state, and historical timestamps.

## ExportJob

Tracks asynchronous trek-history CSV generation for an individual trekker.

## Relationships

```text
User 1 ── 0..1 TrekkerProfile
User 1 ── 0..1 StaffProfile
User 1 ── N Booking
Trek 1 ── N Booking
Trek 1 ── N TrekStaffAssignment
StaffProfile 1 ── N TrekStaffAssignment
User 1 ── N ExportJob
```

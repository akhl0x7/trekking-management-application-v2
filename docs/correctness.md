# Correctness Specification

## Authentication

- Every authenticated request has one current user.
- Inactive and blacklisted accounts cannot authenticate.
- Each user has exactly one role.
- Role authorization is enforced on the server.

## Trek

- `duration_days > 0`.
- `capacity > 0`.
- `0 <= available_slots <= capacity`.
- `start_date <= end_date`.
- Lifecycle transitions are explicit.
- Completed treks do not transition to earlier lifecycle states through normal transition rules.

## Assignment

- An active assignment points to an existing trek.
- An active assignment points to an existing staff profile.
- Only active staff may receive new assignments.
- Staff actions require an active assignment to the target trek.

## Booking

- The user must be active.
- The trek must be open.
- The trek cannot have already started.
- A user may have at most one active booking for a trek.
- A booking reserves capacity using a conditional database update.
- A failed capacity reservation creates no booking.
- A cancellation restores one available slot.
- Historical booking rows are retained.

## Completion

- Completing a trek changes the trek to `COMPLETED`.
- Active bookings become `COMPLETED` when the trek completes.

## Cache

- Redis is an optimization layer rather than the source of truth.
- Mutable trek operations invalidate affected cached data.
- Redis unavailability does not invalidate database correctness.

## Async Jobs

- Export output is scoped by the export owner's user ID.
- Failed exports are recorded as `FAILED` with an error message.
- Completed exports reference a generated CSV file.

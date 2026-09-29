# Design Decisions

## Unified user table

Authentication identity is centralized so role authorization and account status have one source of truth.

## Separate staff assignment table

Staff assignments are represented independently from treks so assignment history can be retained and multiple staff members can be associated with one trek.

## Capacity plus availability

`capacity` represents the total number of places. `available_slots` represents remaining places. Booking decrements availability and cancellation restores it.

## Server-side business rules

Frontend state is not trusted for booking, role authorization, or lifecycle control. The backend and database enforce these rules.

## SQLite as source of truth

Redis accelerates reads but is never treated as authoritative state.

## Session authentication

The application uses Flask's signed session mechanism to keep the local development stack small and understandable.

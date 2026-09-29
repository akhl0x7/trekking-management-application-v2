# Test Plan

## Authentication

- valid login
- invalid credentials
- registration
- authenticated session
- unavailable account

## Authorization

- trekker blocked from admin APIs
- staff blocked from admin APIs
- staff blocked from unassigned treks
- assigned staff allowed

## Trek lifecycle

- pending to approved
- approved to open
- open to closed
- closed to completed
- invalid transitions

## Booking

- valid booking
- duplicate active booking
- full trek
- closed trek
- completed trek
- cancellation
- capacity restoration

## Data integrity

- invalid capacity
- invalid date order
- foreign-key enforcement
- unique active booking constraint

## Background work

- daily reminder task
- monthly report task
- export task
- export ownership checks

## Manual concurrency check

Create a trek with capacity 1 and issue two booking requests as distinct users concurrently. Exactly one request should succeed and the remaining availability should be zero.

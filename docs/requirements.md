# Requirements Traceability

| Requirement | Implementation | Verification |
|---|---|---|
| Admin role | `backend/app/api/admin.py` | `test_rbac.py` |
| Staff role | `backend/app/api/staff.py` | `test_rbac.py` |
| Trekker role | `backend/app/api/trekker.py` | `test_auth.py` |
| Programmatic admin | `backend/app/config.py` and seed flow | seed command |
| Trek CRUD | `backend/app/api/admin.py` | API tests |
| Staff creation | `backend/app/api/admin.py` | API tests |
| Staff assignment | `backend/app/api/admin.py` | assignment tests |
| User management | `backend/app/api/admin.py` | RBAC/API tests |
| Trek search/filter | `backend/app/api/public.py` | filter tests |
| Booking | `backend/app/services/bookings.py` | `test_bookings.py` |
| No duplicate active booking | database index + booking service | `test_bookings.py` |
| No overbooking | conditional update + transaction | `test_bookings.py` |
| Assigned staff authorization | staff assignment query | `test_rbac.py` |
| Trek lifecycle | `backend/app/services/treks.py` | `test_state.py` |
| Trek history | persistent `Booking` rows | history endpoint |
| Redis caching | `backend/app/services/cache.py` | cache fallback test |
| Daily reminders | `backend/app/tasks.py` | Celery task |
| Monthly activity report | `backend/app/tasks.py` | Celery task |
| CSV export | `backend/app/tasks.py` | export flow |

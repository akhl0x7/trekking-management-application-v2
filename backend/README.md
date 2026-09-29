# Backend

The backend exposes the REST API, domain services, SQLite persistence, Redis caching, and Celery tasks.

## Commands

```powershell
python -m flask --app run.py init-db
python -m flask --app run.py seed
python run.py
```

Celery:

```powershell
python -m celery -A app.celery_runner.celery worker --loglevel=INFO
python -m celery -A app.celery_runner.celery beat --loglevel=INFO
```

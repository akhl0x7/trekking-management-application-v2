# Verification

## Static verification

```text
python -m compileall -q backend
```

## Runtime verification

```text
python -m flask --app run.py init-db
python -m flask --app run.py seed
python run.py
```

Health endpoint:

```text
GET /api/v1/health
```

Expected status: `200`.

## Test suite

```text
cd backend
python -m pytest -q
```

## Frontend

```text
cd frontend
npm install
npm run build
```

## Docker

```text
docker compose up --build
```

The development environment should provide Flask on port 5000, Vue on port 5173, and Redis on port 6379.

# Apartment Management Service (Microservice 1)

Owns the **apartments** collection in MongoDB (`rentwise_db`) and exposes CRUD + search REST APIs.

## Run locally
```bash
cd apartment-service
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit MONGO_URI
python seed.py                  # loads 20 sample apartments (use --reset to reload)
python app.py                   # http://localhost:5001
```

## Endpoints
| Method | URL | Purpose | Success |
|---|---|---|---|
| POST | /api/apartments | Create | 201 |
| GET | /api/apartments | List all (same filters as search) | 200 |
| GET | /api/apartments/search?city=&location=&minRent=&maxRent=&bedrooms=&furnishing=&petFriendly= | Filter | 200 |
| GET | /api/apartments/:id | Read one | 200 / 404 |
| PUT | /api/apartments/:id | Update (partial allowed) | 200 / 404 |
| DELETE | /api/apartments/:id | Delete | 200 / 404 |

Errors: `400` validation, `404` not found, `503` database unavailable, `500` unexpected.
Production start command: `gunicorn app:app`.

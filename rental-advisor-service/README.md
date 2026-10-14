# Rental Advisor Service (Microservice 2)

Stateless service: **no database**. It calls the Apartment Service over HTTP (`APARTMENT_SERVICE_URL`),
scores the apartments with a rule-based algorithm and returns ranked, explained results.

## Run locally
```bash
cd rental-advisor-service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # APARTMENT_SERVICE_URL=http://localhost:5001
python app.py                   # http://localhost:5002   (start the Apartment Service first)
```

## Endpoints
| Method | URL | Purpose |
|---|---|---|
| POST | /api/recommendations | Ranked matches for the user's preferences (`?limit=6`) |
| POST | /api/compare | Compare 2-3 apartments (`apartmentIds`, optional `preferences`) |
| GET | /api/recommendations/best-value | Best value apartment (+ 3 runners-up) |
| GET | /api/recommendations/statistics | Rent / area statistics, amenity popularity |

Errors: `400` invalid request, `404` apartment not found, `503` Apartment Service unavailable, `500` unexpected.
Production start command: `gunicorn app:app`.

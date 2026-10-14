# Viva Notes – explain RentWise in simple language

**One line:** RentWise is a rental website split into two small backend programs (microservices) that talk to each other over HTTP, plus a React website that uses both.

**Why microservices?** Each service has one job, its own code, its own deployment and can fail or scale independently. A monolith would put everything in one app.

**Service 1 – Apartment Service:** like a "property office". It only stores and manages apartments in MongoDB (Create, Read, Update, Delete, search).

**Service 2 – Rental Advisor Service:** like a "consultant". It does not touch the apartment database (it has its own small DB only for saved searches). It asks the Apartment Service for apartments using a REST call (`requests.get`), gives each one a score out of 100 and explains the result.

**Communication flow:** React → Rental Advisor → (HTTP) → Apartment Service → MongoDB. The advisor can never touch MongoDB directly.

**Scoring (say this in the viva):** Budget 30 + Location 20 + Bedrooms 15 + Amenities 15 + Furnishing 10 + Commute 5 + Pet 5 = 100. Example: rent below budget gets all 30 points; if 1 of 2 requested amenities is missing, the amenities score is 7.5 of 15. It is rule-based so every number can be explained – no black-box AI.

**Error handling:** 400 bad input, 404 not found, 503 when the Apartment Service is down (the advisor catches the connection error and returns a clean JSON message instead of crashing).

**Independent deployment:** each folder has its own `requirements.txt`/`package.json`, `.env.example` and start command. They are connected only by URLs in environment variables (`APARTMENT_SERVICE_URL`, `VITE_*`).

**CORS:** the browser blocks calls from the frontend domain to a different backend domain unless the backend allows it. `ALLOWED_ORIGINS` lists the allowed frontend URLs (no wildcard).

**Likely questions**
- *Why Flask?* Lightweight, easy REST APIs. *Why MongoDB?* Apartments are flexible documents (amenities list).
- *What if the Apartment Service is down?* Advisor returns HTTP 503.
- *Where is validation?* `apartment-service/services/validation.py` and `scoring.validate_preferences`.
- *How would you scale?* Run more instances of the advisor (it is stateless); add caching/pagination.
- *Why env variables?* No secrets or URLs in code; same code runs locally and in the cloud.

**New in v2**
- *Why does the Advisor have its own DB?* Database-per-service: saved searches belong to the Advisor, so it can change them without touching the Apartment Service.
- *How do you prove the services talk in the cloud?* Open the **Status** page (calls `GET /api/status`, which makes a live HTTP call to the Apartment Service) or call the statistics endpoint.
- *Where are the images?* Local SVG illustrations in `frontend/public/images`; no external host to break.
- *How is it tested?* Postman scripts + pytest (mongomock for the DB, a fake client for the Apartment Service).

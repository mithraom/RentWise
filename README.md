# RentWise – Smart Home Rental Advisor

A microservices-based rental advisor built for the Full Stack Lab mini project.

## 1. Problem Statement
Rental websites only list apartments. Users must manually compare rent, location, bedrooms and amenities. RentWise **ranks** apartments against the user's needs and **explains** why each one is recommended.

## 2. Objectives
- Build two independent REST microservices (Flask) with their own APIs.
- Implement full CRUD with MongoDB.
- Show real service-to-service communication over HTTP.
- Provide a React UI that consumes both services.
- Make every part independently deployable to the cloud.

## 3. Features
Browse with text search, filters and sorting · add/edit/delete apartments (with picture picker) · saved searches (Advisor's own database) · System Status page (live health of both services and the link between them) · rent-by-city statistics · rule-based recommendations with score breakdown and reasons · compare 2–3 apartments · best-value apartment · rental statistics · loading/error/empty states · delete confirmation · responsive UI.

## 4. Technology Stack
| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, JavaScript, CSS, Axios, React Router |
| Microservice 1 | Python, Flask, Flask-CORS, PyMongo |
| Microservice 2 | Python, Flask, Flask-CORS, Requests |
| Database | MongoDB (Atlas in the cloud) |
| Testing | Postman |

## 5. Architecture
```mermaid
flowchart LR
    U[User Browser] --> F[React Frontend<br/>Vite]
    F -- "CRUD / search (REST)" --> A[Apartment Service<br/>Flask :5001]
    F -- "recommend / compare / stats (REST)" --> R[Rental Advisor Service<br/>Flask :5002]
    R -- "HTTP REST: GET /api/apartments" --> A
    A --> D[(MongoDB<br/>rentwise_db.apartments)]
```
The Rental Advisor never touches the apartments database; the only path to apartment data is the HTTP API of the Apartment Service. It has its **own small database** (`rentwise_advisor_db.saved_searches`) for saved searches (database-per-service):

`React → Rental Advisor Service → HTTP REST → Apartment Service → MongoDB`

## 6. Microservices
| | Apartment Service | Rental Advisor Service |
|---|---|---|
| Responsibility | Store and manage apartments (CRUD, search) | Score, rank, compare, statistics |
| Database | MongoDB `rentwise_db.apartments` | MongoDB `rentwise_advisor_db.saved_searches` (own DB; optional) |
| Port | 5001 | 5002 |
| Env vars | `MONGO_URI`, `DB_NAME`, `PORT`, `ALLOWED_ORIGINS` | `APARTMENT_SERVICE_URL`, `MONGO_URI`, `DB_NAME`, `PORT`, `ALLOWED_ORIGINS`, `REQUEST_TIMEOUT` |

Folder layout: `apartment-service/{app.py,routes/,models/,services/}`, `rental-advisor-service/{app.py,routes/,services/}`, `frontend/src/{components,pages,services}`, `postman/`.

## 7. Database Design
Database `rentwise_db`, collection `apartments`:

| Field | Type | Notes |
|---|---|---|
| _id | ObjectId | auto |
| title, description, ownerName | string | title required |
| location, city | string | required |
| rent, securityDeposit | number | rent required (> 0) |
| bedrooms, bathrooms | integer | required |
| areaSqFt | number | required |
| furnishing | string | `Unfurnished` / `Semi-Furnished` / `Fully-Furnished` |
| availableFrom | string | `YYYY-MM-DD` |
| amenities | string[] | e.g. `["WiFi","Parking"]` |
| parking, petFriendly | boolean | |
| commuteDistance | number | km |
| imageUrl | string | |
| createdAt | ISO string | set by server |

## 8. API Documentation
### Apartment Service (`:5001`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/apartments` | Create (201) |
| GET | `/api/apartments` | List |
| GET | `/api/apartments/search?q&city&location&minRent&maxRent&bedrooms&furnishing&petFriendly&parking&maxCommute&sort` | Filter / text search / sort (`newest, rentAsc, rentDesc, areaDesc, commuteAsc`) |
| GET | `/health` | Service + database health |
| GET | `/api/apartments/:id` | Get one |
| PUT | `/api/apartments/:id` | Update |
| DELETE | `/api/apartments/:id` | Delete |

### Rental Advisor Service (`:5002`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/recommendations` | Ranked matches |
| POST | `/api/compare` | Body: `{"apartmentIds":[id,id,id],"preferences":{...optional}}` |
| GET | `/api/recommendations/best-value` | Best value apartment |
| GET | `/api/recommendations/statistics` | Rent/area statistics (incl. by city) |
| GET | `/api/status` | Health of the Advisor and of its REST link to the Apartment Service |
| POST / GET | `/api/saved-searches` | Save / list searches (Advisor's own DB) |
| PUT / DELETE | `/api/saved-searches/:id` | Rename / delete a saved search |

Request for `POST /api/recommendations`:
```json
{ "budget": 25000, "preferredCity": "Coimbatore", "bedrooms": 2, "furnishing": "Semi-Furnished",
  "requiredAmenities": ["Parking", "WiFi"], "maxCommuteDistance": 8, "petFriendly": true }
```
Each result contains `apartment`, `recommendationScore`, `matchLabel`, `scoreBreakdown`, `maxScores`, `matchedAmenities`, `missingAmenities`, `affordabilityStatus`, `locationMatch`, `reason`.
All errors have the shape `{ "success": false, "error": "...", "details": [...] }` (400, 404, 405, 500, 503).

## 9. Inter-service Communication
`rental-advisor-service/services/apartment_client.py` uses `requests.get(APARTMENT_SERVICE_URL + "/api/apartments")` (and `/api/apartments/:id`). If the Apartment Service is down or times out, the client raises `ApartmentServiceError`, which the Advisor converts into a clean **503** JSON response.

## 10. Recommendation Algorithm (rule-based, explainable)
`recommendationScore = Budget 30 + Location 20 + Bedrooms 15 + Amenities 15 + Furnishing 10 + Commute 5 + Pet-friendly 5` (max 100)

| Criterion | Rule |
|---|---|
| Budget (30) | rent ≤ budget → 30; up to 20 % over → falls linearly to 0; more → 0 |
| Location (20) | city matches → 20 (if an area is also given: city 12 + area 8) |
| Bedrooms (15) | exact 15; more bedrooms 10; one fewer 5; else 0 |
| Amenities (15) | 15 × (matched ÷ requested) |
| Furnishing (10) | exact 10; Semi-Furnished vs another type 5; else 0 |
| Commute (5) | within limit 5; falls linearly to 0 at twice the limit |
| Pet (5) | 5 unless pets are required and not allowed |

Labels: ≥85 Excellent, ≥70 Good, ≥50 Fair, else Low. The `reason` text is generated from the same rules (what matched, what is missing).
**Best value** (separate score): price per sq.ft 40 + facilities 25 + short commute 20 + space 15, relative to all apartments.

## 11. Local Setup
Prerequisites: Python 3.10+, Node 18+, MongoDB (local or free Atlas cluster).
Open **three terminals**:
```bash
# 1) Apartment Service
cd apartment-service && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env     # set MONGO_URI
python seed.py && python app.py                              # :5001

# 2) Rental Advisor Service
cd rental-advisor-service && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env      # APARTMENT_SERVICE_URL=http://localhost:5001
python app.py                                                # :5002

# 3) Frontend
cd frontend && npm install && cp .env.example .env
npm run dev                                                  # http://localhost:5173
```
Windows: use `copy` instead of `cp`, and `.venv\Scripts\activate`.

## 12. Environment Variables
| Component | Variable | Example |
|---|---|---|
| Apartment Service | `MONGO_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| | `DB_NAME` | `rentwise_db` |
| | `PORT` | `5001` |
| | `ALLOWED_ORIGINS` | `http://localhost:5173,https://rentwise.vercel.app` |
| Rental Advisor | `APARTMENT_SERVICE_URL` | `https://rentwise-apartment.onrender.com` |
| | `PORT`, `ALLOWED_ORIGINS`, `REQUEST_TIMEOUT` | `5002`, same as above, `25` |
| Frontend | `VITE_APARTMENT_API_URL` | `https://rentwise-apartment.onrender.com` |
| | `VITE_ADVISOR_API_URL` | `https://rentwise-advisor.onrender.com` |

Real values are never committed (`.env` is git-ignored; only `.env.example` is in the repo).

## 13. Postman Testing
1. Import `postman/RentWise_API_Collection.json`.
2. Collection variables: `apartmentUrl` (default `http://localhost:5001`), `advisorUrl` (`http://localhost:5002`). Change them to the deployed URLs to test the cloud version.
3. Run **POST Create Apartment** first – its test script stores `apartmentId` automatically for GET/PUT/DELETE.
4. For **POST Compare**, set `apartmentId2`/`apartmentId3` from the GET list response.
Every request has an example body and an example response.

## 14. Deployment (free-tier friendly: MongoDB Atlas + Render + Vercel)
Deploy in this order, because each step needs the URL of the previous one. Push the whole repo to GitHub first.

### Step 0 – MongoDB Atlas
1. Create a free cluster → *Database Access*: add a user + password.
2. *Network Access*: allow `0.0.0.0/0` (needed for Render's changing IPs).
3. *Connect → Drivers*: copy the connection string (`mongodb+srv://...`). This is your `MONGO_URI`.
4. Load sample data once from your laptop: in `apartment-service/.env` put the Atlas `MONGO_URI`, run `python seed.py`.

### Step 1 – Apartment Service (Render → New Web Service)
- Repo: your GitHub repo · **Root Directory:** `apartment-service` · Runtime: Python 3
- Build command: `pip install -r requirements.txt` · Start command: `gunicorn app:app`
- Environment variables: `MONGO_URI` (Atlas string), `DB_NAME=rentwise_db`, `ALLOWED_ORIGINS=http://localhost:5173` (updated in Step 4)
- Deploy, then open `https://<apartment-service>.onrender.com/api/apartments` – you should see JSON.

### Step 2 – Rental Advisor Service (Render → New Web Service)
- **Root Directory:** `rental-advisor-service` · same build/start commands
- Environment variables: `APARTMENT_SERVICE_URL=https://<apartment-service>.onrender.com` (no trailing slash), `ALLOWED_ORIGINS=http://localhost:5173`
- Test `https://<advisor>.onrender.com/api/recommendations/statistics` – this proves service-to-service communication works in the cloud.

### Step 3 – React Frontend (Vercel, or Netlify)
- Import the repo · **Root Directory:** `frontend` · Framework: Vite · Build `npm run build` · Output `dist`
- Environment variables: `VITE_APARTMENT_API_URL=https://<apartment-service>.onrender.com`, `VITE_ADVISOR_API_URL=https://<advisor>.onrender.com`
- Deploy and note the URL, e.g. `https://rentwise.vercel.app`. (`vercel.json` / `public/_redirects` handle page refresh on routes.)

### Step 4 – Lock down CORS
In **both** Render services set `ALLOWED_ORIGINS=https://rentwise.vercel.app` (add `,http://localhost:5173` if you still develop locally; no trailing slash) and redeploy.

> Free Render services sleep after inactivity; the first request can take 30–60 s. Open the services once before a demo/viva. Vite variables are baked in at build time – after changing them, redeploy the frontend.

## 15. Deployment URLs
| Component | URL |
|---|---|
| Frontend | `https://<your-frontend>.vercel.app` |
| Apartment Service | `https://<your-apartment-service>.onrender.com` |
| Rental Advisor Service | `https://<your-advisor-service>.onrender.com` |

## 16. Images
All pictures are original SVG illustrations in `frontend/public/images/` (apartment types and a hero skyline). They work offline, need no external image host, and the seed script assigns the matching picture by bedrooms / furnishing / rent. Users can pick another picture in the Add/Edit form or paste their own URL.

## 16b. Automated tests
```bash
cd apartment-service && pip install -r requirements-dev.txt && pytest        # in-memory MongoDB
cd rental-advisor-service && pip install -r requirements-dev.txt && pytest   # Apartment Service mocked
```
The tests cover CRUD, validation, search/sort, ranking, compare, saved searches and the 503 behaviour when the Apartment Service is down.

## 16c. Docker (optional)
`docker compose up --build` starts MongoDB, both services and the frontend (http://localhost:5173). `render.yaml` is a Render Blueprint for the two backends.

## 16d. Screenshots
Add screenshots in `docs/screenshots/` and link them here: Home, Browse, Advisor form, Recommendations, Compare, Statistics, Postman.

## 17. Future Enhancements
User login & saved searches · owner dashboards · map view · pagination · image upload (file) · email alerts · Docker Compose · automated tests (pytest).

## Troubleshooting
- Open **http://localhost:5001/health** (Apartment Service) and **http://localhost:5002/health** (Rental Advisor). They tell you exactly what is wrong: database not reachable, or Apartment Service not reachable.
- On startup each service prints `[env] Loaded ...` or `[env] No .env file found ...`. Create `.env` by copying `.env.example` (on Windows make sure it is not saved as `.env.txt`).
- "Database unavailable" -> MongoDB is not running / wrong `MONGO_URI` / Atlas IP not allowed.
- Without any `.env` the services default to `mongodb://localhost:27017` and `http://localhost:5001` for local development.

## Testing Checklist
- [ ] `GET :5001/` and `GET :5002/` return `status: running`
- [ ] POST apartment with valid body → 201; with missing fields → 400
- [ ] GET list returns 20 seeded apartments; GET by invalid id → 400; unknown valid id → 404
- [ ] PUT changes rent; DELETE removes the apartment (then GET → 404)
- [ ] Search `city=Coimbatore&maxRent=20000&bedrooms=2` returns only matching apartments
- [ ] POST /api/recommendations returns scores sorted high→low with reason & breakdown; without `budget` → 400
- [ ] POST /api/compare with 2–3 ids works; with 1 id → 400
- [ ] GET best-value and statistics return data
- [ ] **Stop the Apartment Service** → Advisor endpoints return 503 JSON (no crash)
- [ ] Frontend: filters work, cards show, compare button limits to 3, delete asks confirmation
- [ ] Frontend: Advisor form → Top Matches page with score rings; Compare table highlights best values
- [ ] Mobile width: menu collapses, cards stack
- [ ] After deployment: all of the above using the cloud URLs, and no CORS errors in the browser console

# RentWise – Project Report
**Course:** 22MDC55 Full Stack Application Development Lab · CAT-II Mini Project
**Title:** Development and Deployment of a Microservices-Based Full Stack Application
**Team:** <names and roll numbers>

## 1. Problem and Objective
Rental portals only list homes; tenants compare rent, area, amenities and commute by hand. RentWise ranks listings against a tenant's needs and explains every score.

## 2. Architecture
React (Vite) frontend → two independent Flask REST microservices → MongoDB.
- **Apartment Service (:5001)** – owns apartment data: CRUD, validation, search, sort. DB `rentwise_db`.
- **Rental Advisor Service (:5002)** – scoring, ranking, comparison, statistics, best value, saved searches. DB `rentwise_advisor_db` (its own).
- **Communication:** the Advisor calls the Apartment Service over HTTP (`requests`) and never reads its database. Failures (timeout, service down) become a clean JSON **503**; unknown id → **404**.
- Each service has its own code, dependencies, env vars, start command and Dockerfile, so it is deployed independently.

## 3. Modules
| Module | Details |
|---|---|
| Listings | Browse, text search, filters, sorting, details, add / edit / delete |
| Advisor | 7-factor explainable score (budget 30, location 20, bedrooms 15, amenities 15, furnishing 10, commute 5, pets 5) with reasons |
| Compare | 2–3 apartments side by side, best value per row |
| Statistics | Averages, rent by bedroom and by city, amenity frequency, best value |
| Saved searches | CRUD stored in the Advisor's own database |
| System Status | Live health of both services and the inter-service link |

## 4. API summary
See README section 8 and `postman/RentWise_API_Collection.json` (every request has a test script).

## 5. Testing
- Postman collection with assertions (201 / 400 / 404 / 503 cases, inter-service status).
- `pytest` suites: 6 tests per service, all passing (CRUD, validation, search, ranking, compare, saved searches, service-down → 503).
- Manual checklist in README.

## 6. Deployment
MongoDB Atlas · Render (2 web services, `render.yaml`) · Vercel/Netlify (frontend).

| Component | URL |
|---|---|
| Frontend | <fill after deployment> |
| Apartment Service | <fill after deployment> |
| Rental Advisor Service | <fill after deployment> |

## 7. Screenshots
<Home, Browse, Advisor, Recommendations, Compare, Statistics, System Status, Postman, Render dashboard>

## 8. Conclusion and Future Work
Two independently deployed services cooperate through REST to deliver an explainable rental advisor. Future work: authentication, owner dashboards, maps, pagination, file upload, CI/CD.

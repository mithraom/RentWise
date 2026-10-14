# Evaluation criteria → where RentWise satisfies them
| # | Criterion (marks) | Evidence |
|---|---|---|
| 1 | Application & Backend (10) | Apartment Service: full CRUD, validation, search/sort (`apartment-service/routes/apartments.py`). Advisor: scoring, compare, stats, best value, saved-search CRUD. Two MongoDB databases. |
| 2 | Microservice communication (5) | `rental-advisor-service/services/apartment_client.py` (REST via `requests`), timeout + 404/400/5xx mapping → 503 JSON. `/api/status` and the System Status page prove the link. |
| 3 | Frontend (5) | React pages for every API: Browse, Details, Add/Edit, Advisor, Recommendations, Compare, Statistics, Status. Loading / error / empty states, images, responsive. |
| 4 | Deployment (5) | `render.yaml`, Procfiles, Dockerfiles, `docker-compose.yml`, `vercel.json`. **You must deploy and fill URLs in README / report.** |
| 5 | Testing & docs (5) | Postman collection with tests, pytest suites, README, `PROJECT_REPORT.md`, `VIVA_NOTES.md`. |
| Viva (10) | `VIVA_NOTES.md` |

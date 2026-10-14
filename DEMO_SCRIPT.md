# 5-minute demo script (exam day)

**Before the exam:** open both Render URLs once (free tier sleeps ~30-60 s), then keep the Status page open.

1. **Architecture (30 s)** - draw: React -> Advisor Service -> (REST) -> Apartment Service -> MongoDB. Say: "two independent services, separate code, DB and deployment."
2. **Apartment Service CRUD (60 s)** - Postman: POST create -> GET list -> PUT update -> DELETE. Show a 400 (bad input) and a 404 (unknown id).
3. **Inter-service call (60 s)** - Postman: `GET <advisor>/api/recommendations/statistics`. Explain it fetches data from the Apartment Service over HTTP. Show `GET <advisor>/api/status`.
4. **Frontend (90 s)** - Browse (search/filter/sort) -> Add an apartment -> Advisor form -> Recommendations with score reasons -> Compare 2-3 -> Statistics -> Status page (both green).
5. **Deployment proof (30 s)** - show the Render dashboard (2 services), Vercel (frontend), Atlas (data), and the deployed URLs.
6. **Error handling (30 s)** - optional: show the 503 JSON when the Apartment Service URL is wrong.

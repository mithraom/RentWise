# RentWise Frontend (React + Vite)

```bash
cd frontend
npm install
cp .env.example .env     # set VITE_APARTMENT_API_URL and VITE_ADVISOR_API_URL
npm run dev              # http://localhost:5173
npm run build            # production build in dist/
```
Pages: Home, Browse, Apartment Details, Rental Advisor, Recommendations, Compare, Statistics, Add, Edit.
Vite reads `VITE_*` variables at **build time**, so after changing them on a host you must redeploy/rebuild.
`public/_redirects` (Netlify) and `vercel.json` make React Router deep links work after deployment.

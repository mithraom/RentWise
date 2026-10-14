import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getStatistics } from "../services/api.js";
import { CITIES, inr } from "../utils.js";

const features = [
  ["🎯", "Smart Recommendations", "Apartments ranked 0–100 with a clear explanation."],
  ["💰", "Budget Friendly", "See instantly whether a home fits your monthly budget."],
  ["📍", "Location Based", "Match your city, area and maximum commute distance."],
  ["⚖️", "Apartment Comparison", "Compare up to 3 apartments side by side."],
];
const steps = [
  ["1", "Tell us your needs", "Budget, city, bedrooms, amenities and commute."],
  ["2", "Advisor scores homes", "The Advisor microservice fetches listings from the Apartment microservice and scores each one."],
  ["3", "Pick with confidence", "See reasons, score breakdown and compare your shortlist."],
];

export default function Home() {
  const [stats, setStats] = useState(null);
  useEffect(() => { getStatistics().then(setStats).catch(() => {}); }, []);
  return (
    <>
      <section className="hero hero-split">
        <div className="hero-text">
          <h1>Find a Home That Fits Your Life</h1>
          <p>Smart rental recommendations based on your budget, location and lifestyle.</p>
          <div className="row">
            <Link className="btn big" to="/advisor">Find My Home</Link>
            <Link className="btn big outline light" to="/apartments">Browse Apartments</Link>
          </div>
        </div>
        <img className="hero-art" src="/images/hero-city.svg" alt="Illustration of apartment buildings in a city" />
      </section>

      {stats && (
        <section className="stat-strip">
          <div><b>{stats.totalApartments}</b><span>Listings</span></div>
          <div><b>{stats.availableApartments}</b><span>Available now</span></div>
          <div><b>{inr(stats.averageRent)}</b><span>Average rent</span></div>
          <div><b>{CITIES.length}</b><span>Cities</span></div>
        </section>
      )}

      <section className="grid4">
        {features.map(([icon, t, d]) => (
          <div className="card pad feature" key={t}><div className="icon">{icon}</div><h3>{t}</h3><p className="muted">{d}</p></div>
        ))}
      </section>

      <h2 className="section-title">How it works</h2>
      <section className="grid4 steps">
        {steps.map(([n, t, d]) => (
          <div className="card pad" key={n}><span className="step-no">{n}</span><h3>{t}</h3><p className="muted">{d}</p></div>
        ))}
      </section>

      <h2 className="section-title">Explore by city</h2>
      <section className="city-row">
        {CITIES.map((c) => <Link key={c} className="city-chip" to={`/apartments?city=${c}`}>🏙️ {c}</Link>)}
      </section>
    </>
  );
}

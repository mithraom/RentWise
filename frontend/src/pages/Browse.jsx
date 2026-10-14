import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getApartments, errMsg } from "../services/api.js";
import ApartmentCard from "../components/ApartmentCard.jsx";
import { Loading, ErrorBox, Empty } from "../components/State.jsx";
import { CITIES, FURNISHING } from "../utils.js";

const initial = { q: "", city: "", maxRent: "", bedrooms: "", furnishing: "", petFriendly: "", sort: "newest" };

export default function Browse() {
  const [params] = useSearchParams();
  const [filters, setFilters] = useState({ ...initial, city: params.get("city") || "" });
  const [apts, setApts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = () => {
    setLoading(true); setError("");
    getApartments(filters).then(setApts).catch((e) => setError(errMsg(e))).finally(() => setLoading(false));
  };
  useEffect(load, [filters]);
  const set = (k) => (e) => setFilters({ ...filters, [k]: e.target.value });

  return (
    <>
      <h1>Browse Apartments</h1>
      <div className="filters card pad">
        <input type="search" placeholder="Search title, area, amenity..." value={filters.q} onChange={set("q")} />
        <select value={filters.city} onChange={set("city")}><option value="">All cities</option>{CITIES.map((c) => <option key={c}>{c}</option>)}</select>
        <input type="number" placeholder="Max rent (₹)" value={filters.maxRent} onChange={set("maxRent")} min="0" />
        <select value={filters.bedrooms} onChange={set("bedrooms")}><option value="">Any bedrooms</option>{[1, 2, 3].map((n) => <option key={n} value={n}>{n} BHK</option>)}</select>
        <select value={filters.furnishing} onChange={set("furnishing")}><option value="">Any furnishing</option>{FURNISHING.map((c) => <option key={c}>{c}</option>)}</select>
        <select value={filters.petFriendly} onChange={set("petFriendly")}><option value="">Pets: any</option><option value="true">Pet friendly</option></select>
        <select value={filters.sort} onChange={set("sort")} aria-label="Sort">
          <option value="newest">Sort: Newest</option><option value="rentAsc">Rent: Low to High</option>
          <option value="rentDesc">Rent: High to Low</option><option value="areaDesc">Largest area</option>
          <option value="commuteAsc">Shortest commute</option></select>
        <button className="btn outline small" onClick={() => setFilters(initial)}>Reset</button>
      </div>
      {loading ? <Loading text="Loading apartments (the server may take a few seconds to wake up)..." /> :
        error ? <ErrorBox message={error} onRetry={load} /> :
        apts.length === 0 ? <Empty>No apartments match your filters.</Empty> :
        <><p className="muted">{apts.length} apartments found</p><div className="grid3">{apts.map((a) => <ApartmentCard key={a._id} apt={a} />)}</div></>}
    </>
  );
}

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { compareApartments, errMsg } from "../services/api.js";
import { useCompare } from "../CompareContext.jsx";
import { Loading, ErrorBox, Empty } from "../components/State.jsx";
import { inr } from "../utils.js";

const ROWS = [
  ["Monthly rent", "rent", (a) => inr(a.rent)],
  ["Security deposit", "securityDeposit", (a) => inr(a.securityDeposit)],
  ["Bedrooms", "bedrooms", (a) => a.bedrooms],
  ["Bathrooms", "bathrooms", (a) => a.bathrooms],
  ["Area", "areaSqFt", (a) => `${a.areaSqFt} sq.ft`],
  ["Furnishing", null, (a) => a.furnishing],
  ["Amenities", "amenities", (a) => `${a.amenityCount}: ${a.amenities.join(", ")}`],
  ["Commute", "commuteDistance", (a) => `${a.commuteDistance} km`],
];

export default function Compare() {
  const { ids, toggle, clear } = useCompare();
  const [res, setRes] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (ids.length < 2) { setRes(null); return; }
    setLoading(true); setError("");
    const prefs = JSON.parse(sessionStorage.getItem("rw_prefs") || "null") || undefined;
    compareApartments(ids, prefs).then(setRes).catch((e) => setError(errMsg(e))).finally(() => setLoading(false));
  }, [ids]);

  if (ids.length < 2)
    return <Empty>Select 2 or 3 apartments to compare ({ids.length} selected). <Link to="/apartments">Browse apartments</Link></Empty>;
  if (loading) return <Loading text="Comparing..." />;
  if (error) return <ErrorBox message={error} onRetry={() => clear()} />;
  if (!res) return null;
  const best = (key, id) => key && res.highlights[key] === id ? "best" : "";

  return (
    <>
      <h1>Compare Apartments</h1>
      <p className="muted">Best value in each row is highlighted. {res.scoreType === "match" ? "Score = match with your preferences." : "Score = overall value score (use the Rental Advisor to get a personalised match score)."}</p>
      <div className="table-wrap">
        <table className="compare">
          <thead><tr><th />{res.data.map((a) => (
            <th key={a._id}><Link to={`/apartments/${a._id}`}>{a.title}</Link><br /><small>{a.location}, {a.city}</small><br />
              <button className="link-btn" onClick={() => toggle(a._id)}>Remove</button></th>))}</tr></thead>
          <tbody>
            {ROWS.map(([label, key, fmt]) => (
              <tr key={label}><th>{label}</th>{res.data.map((a) => <td key={a._id} className={best(key, a._id)}>{fmt(a)}</td>)}</tr>))}
            <tr><th>{res.scoreType === "match" ? "Recommendation score" : "Value score"}</th>
              {res.data.map((a) => <td key={a._id} className={best("score", a._id) + " strong"}>{a.score}{a._id === res.bestValueId && " 🏆"}</td>)}</tr>
          </tbody>
        </table>
      </div>
      <button className="btn outline small" onClick={clear}>Clear selection</button>
    </>
  );
}

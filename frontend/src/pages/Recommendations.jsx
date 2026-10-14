import { useState } from "react";
import { Link } from "react-router-dom";
import { saveSearch, errMsg } from "../services/api.js";
import ScoreBadge from "../components/ScoreBadge.jsx";
import { useCompare } from "../CompareContext.jsx";
import { Empty } from "../components/State.jsx";
import { inr, FALLBACK_IMG, aptImage } from "../utils.js";

const NAMES = { budget: "Budget", location: "Location", bedrooms: "Bedrooms", amenities: "Amenities",
  furnishing: "Furnishing", commute: "Commute", petFriendly: "Pet friendly" };

export default function Recommendations() {
  const { has, toggle } = useCompare();
  const [msg, setMsg] = useState("");
  const saved = sessionStorage.getItem("rw_results");
  if (!saved) return <Empty>No recommendations yet. <Link to="/advisor">Use the Rental Advisor</Link> first.</Empty>;
  const res = JSON.parse(saved);

  const save = async () => {
    const name = window.prompt("Name this search:", `Search for ₹${res.preferences.budget}`);
    if (name === null) return;
    try { await saveSearch(name, res.preferences); setMsg("✓ Search saved"); } catch (e) { setMsg("⚠️ " + errMsg(e)); }
  };

  return (
    <>
      <h1>Your Top Rental Matches</h1>
      <p className="muted">{res.totalEvaluated} apartments evaluated · <Link to="/advisor">Change preferences</Link> · <button className="btn small outline" onClick={save}>💾 Save this search</button> {msg}</p>
      <div className="stack">
        {res.data.map((r, i) => {
          const a = r.apartment;
          return (
            <article className="card rec" key={a._id}>
              <img src={aptImage(a)} alt={a.title} onError={(e) => (e.target.src = FALLBACK_IMG)} />
              <div className="rec-main">
                <h3>#{i + 1} {a.title}</h3>
                <p className="muted">📍 {a.location}, {a.city} · {a.bedrooms} Bed · {a.bathrooms} Bath · {a.furnishing}</p>
                <p className="rent">{inr(a.rent)}<small>/month</small> <span className={"afford " + (r.affordabilityStatus.includes("over") || r.affordabilityStatus.includes("Over") ? "bad" : "ok")}>{r.affordabilityStatus}</span></p>
                <div className="tags">
                  {r.matchedAmenities.map((x) => <span key={x} className="tag good">✓ {x}</span>)}
                  {r.missingAmenities.map((x) => <span key={x} className="tag miss">✗ {x}</span>)}
                  {a.amenities.filter((x) => !r.matchedAmenities.includes(x)).slice(0, 3).map((x) => <span key={x} className="tag">{x}</span>)}
                </div>
                <p className="reason">💡 {r.reason}</p>
                <div className="breakdown">
                  {Object.entries(r.scoreBreakdown).map(([k, v]) => (
                    <div key={k} className="bar-row"><span>{NAMES[k]}</span>
                      <div className="bar"><i style={{ width: `${(v / r.maxScores[k]) * 100}%` }} /></div>
                      <span>{v}/{r.maxScores[k]}</span></div>))}
                </div>
                <div className="row">
                  <Link className="btn small" to={`/apartments/${a._id}`}>View Details</Link>
                  <button className="btn small outline" onClick={() => toggle(a._id)}>{has(a._id) ? "✓ Added to compare" : "Compare"}</button>
                </div>
              </div>
              <ScoreBadge score={r.recommendationScore} />
            </article>
          );
        })}
      </div>
    </>
  );
}

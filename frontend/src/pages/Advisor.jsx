import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getRecommendations, getSavedSearches, deleteSavedSearch, errMsg } from "../services/api.js";
import { AMENITIES, CITIES, FURNISHING } from "../utils.js";

export default function Advisor() {
  const nav = useNavigate();
  const [f, setF] = useState({ budget: 25000, preferredCity: "Coimbatore", bedrooms: 2, furnishing: "Semi-Furnished",
    requiredAmenities: ["Parking", "WiFi"], maxCommuteDistance: 8, petFriendly: false });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState([]);
  const [savedErr, setSavedErr] = useState("");
  useEffect(() => { getSavedSearches().then(setSaved).catch((e) => setSavedErr(errMsg(e))); }, []);
  const load = (p) => setF({ ...f, ...p, requiredAmenities: p.requiredAmenities || [], furnishing: p.furnishing || "" });
  const drop = async (id) => { await deleteSavedSearch(id); setSaved(saved.filter((x) => x._id !== id)); };
  const set = (k, v) => setF((p) => ({ ...p, [k]: v }));
  const toggle = (a) => set("requiredAmenities", f.requiredAmenities.includes(a) ? f.requiredAmenities.filter((x) => x !== a) : [...f.requiredAmenities, a]);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    const prefs = { ...f, budget: Number(f.budget), bedrooms: Number(f.bedrooms), maxCommuteDistance: Number(f.maxCommuteDistance) };
    try {
      const res = await getRecommendations(prefs);           // -> Rental Advisor Service
      sessionStorage.setItem("rw_prefs", JSON.stringify(prefs));
      sessionStorage.setItem("rw_results", JSON.stringify(res));
      nav("/recommendations");
    } catch (err) { setError(errMsg(err)); } finally { setLoading(false); }
  };

  return (
    <>
      <h1>Rental Advisor</h1>
      <p className="muted">Tell us what you need and we will rank the best apartments for you.</p>
      <form className="form card pad" onSubmit={submit}>
        <div className="grid2">
          <label>Monthly budget (₹)<input type="number" min="1" required value={f.budget} onChange={(e) => set("budget", e.target.value)} /></label>
          <label>Preferred city<select value={f.preferredCity} onChange={(e) => set("preferredCity", e.target.value)}>{CITIES.map((c) => <option key={c}>{c}</option>)}</select></label>
          <label>Bedrooms<select value={f.bedrooms} onChange={(e) => set("bedrooms", e.target.value)}>{[1, 2, 3].map((n) => <option key={n} value={n}>{n} BHK</option>)}</select></label>
          <label>Furnishing<select value={f.furnishing} onChange={(e) => set("furnishing", e.target.value)}><option value="">Any</option>{FURNISHING.map((c) => <option key={c}>{c}</option>)}</select></label>
          <label>Maximum commute (km)<input type="number" min="0" step="0.5" value={f.maxCommuteDistance} onChange={(e) => set("maxCommuteDistance", e.target.value)} /></label>
          <label className="check pad-top"><input type="checkbox" checked={f.petFriendly} onChange={(e) => set("petFriendly", e.target.checked)} /> I need a pet friendly home</label>
        </div>
        <fieldset><legend>Required amenities</legend>
          <div className="checks">{AMENITIES.map((a) => <label key={a} className="check"><input type="checkbox" checked={f.requiredAmenities.includes(a)} onChange={() => toggle(a)} /> {a}</label>)}</div>
        </fieldset>
        {error && <div className="state error">⚠️ {error}</div>}
        <button className="btn big" disabled={loading}>{loading ? "Finding your matches..." : "Find My Home"}</button>
      </form>
      <h2 className="section-title">Saved searches</h2>
      {savedErr ? <p className="muted">Saved searches unavailable: {savedErr}</p> :
        saved.length === 0 ? <p className="muted">No saved searches yet. Run a search and click “Save this search”.</p> :
        <div className="stack">{saved.map((s) => (
          <div className="card pad saved" key={s._id}>
            <div><b>{s.name}</b><p className="muted">₹{Number(s.preferences.budget).toLocaleString("en-IN")} · {s.preferences.preferredCity || "Any city"} · {s.preferences.bedrooms || "Any"} BHK</p></div>
            <div className="row"><button className="btn small outline" type="button" onClick={() => load(s.preferences)}>Load</button>
              <button className="link-btn" type="button" onClick={() => drop(s._id)}>Delete</button></div>
          </div>))}</div>}
    </>
  );
}

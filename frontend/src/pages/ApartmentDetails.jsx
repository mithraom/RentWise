import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { getApartment, deleteApartment, errMsg } from "../services/api.js";
import { useCompare } from "../CompareContext.jsx";
import { Loading, ErrorBox } from "../components/State.jsx";
import { inr, FALLBACK_IMG, aptImage } from "../utils.js";

export default function ApartmentDetails() {
  const { id } = useParams();
  const nav = useNavigate();
  const { has, toggle } = useCompare();
  const [apt, setApt] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { getApartment(id).then(setApt).catch((e) => setError(errMsg(e))); }, [id]);

  const remove = async () => {
    if (!window.confirm(`Delete "${apt.title}"? This cannot be undone.`)) return;
    try { await deleteApartment(id); nav("/apartments"); } catch (e) { alert(errMsg(e)); }
  };

  if (error) return <ErrorBox message={error} />;
  if (!apt) return <Loading />;
  const rows = [["Monthly rent", inr(apt.rent)], ["Security deposit", inr(apt.securityDeposit)], ["Bedrooms", apt.bedrooms],
    ["Bathrooms", apt.bathrooms], ["Area", `${apt.areaSqFt} sq.ft`], ["Furnishing", apt.furnishing],
    ["Available from", apt.availableFrom], ["Parking", apt.parking ? "Yes" : "No"], ["Pet friendly", apt.petFriendly ? "Yes" : "No"],
    ["Commute distance", `${apt.commuteDistance} km`], ["Owner", apt.ownerName || "—"]];
  return (
    <div className="details">
      <img className="hero-img" src={aptImage(apt)} alt={apt.title} onError={(e) => (e.target.src = FALLBACK_IMG)} />
      <div>
        <h1>{apt.title}</h1>
        <p className="muted">📍 {apt.location}, {apt.city}</p>
        <p className="rent big">{inr(apt.rent)}<small>/month</small></p>
        <p>{apt.description}</p>
        <table className="kv"><tbody>{rows.map(([k, v]) => <tr key={k}><th>{k}</th><td>{v}</td></tr>)}</tbody></table>
        <div className="tags">{apt.amenities.map((a) => <span key={a} className="tag">{a}</span>)}</div>
        <div className="row">
          <button className="btn" onClick={() => toggle(apt._id)}>{has(apt._id) ? "✓ In comparison" : "Add to compare"}</button>
          <Link className="btn outline" to={`/apartments/${id}/edit`}>Edit</Link>
          <button className="btn danger" onClick={remove}>Delete</button>
        </div>
      </div>
    </div>
  );
}

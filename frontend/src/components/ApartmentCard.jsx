import { Link } from "react-router-dom";
import { useCompare } from "../CompareContext.jsx";
import { inr, FALLBACK_IMG, aptImage } from "../utils.js";

export default function ApartmentCard({ apt }) {
  const { has, toggle } = useCompare();
  const picked = has(apt._id);
  return (
    <article className="card apt-card">
      <img src={aptImage(apt)} alt={apt.title} onError={(e) => (e.target.src = FALLBACK_IMG)} />
      <div className="card-body">
        <h3>{apt.title}</h3>
        <p className="muted">📍 {apt.location}, {apt.city}</p>
        <p className="rent">{inr(apt.rent)}<small>/month</small></p>
        <p className="facts">{apt.bedrooms} Bed · {apt.bathrooms} Bath · {apt.areaSqFt} sq.ft</p>
        <p className="muted">{apt.furnishing}</p>
        <div className="tags">{(apt.amenities || []).slice(0, 4).map((a) => <span key={a} className="tag">{a}</span>)}</div>
        <div className="row">
          <Link className="btn small" to={`/apartments/${apt._id}`}>View Details</Link>
          <button className={picked ? "btn small outline active" : "btn small outline"} onClick={() => toggle(apt._id)}>
            {picked ? "✓ Added" : "Compare"}
          </button>
        </div>
      </div>
    </article>
  );
}

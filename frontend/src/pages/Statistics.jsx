import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getStatistics, getBestValue, errMsg } from "../services/api.js";
import { Loading, ErrorBox } from "../components/State.jsx";
import { inr } from "../utils.js";

export default function Statistics() {
  const [s, setS] = useState(null);
  const [best, setBest] = useState(null);
  const [error, setError] = useState("");
  const load = () => {
    setError("");
    Promise.all([getStatistics(), getBestValue()]).then(([a, b]) => { setS(a); setBest(b); }).catch((e) => setError(errMsg(e)));
  };
  useEffect(load, []);

  if (error) return <ErrorBox message={error} onRetry={load} />;
  if (!s) return <Loading text="Loading statistics (the server may take a few seconds to wake up)..." />;
  const maxRent = Math.max(...s.averageRentByBedrooms.map((r) => r.averageRent));
  const maxAm = Math.max(...s.mostCommonAmenities.map((r) => r.count));
  const cards = [["Average rent", inr(s.averageRent)], ["Minimum rent", inr(s.minimumRent)], ["Maximum rent", inr(s.maximumRent)],
    ["Average area", `${s.averageArea} sq.ft`], ["Total apartments", s.totalApartments], ["Available now", s.availableApartments]];
  return (
    <>
      <h1>Rental Statistics</h1>
      <div className="grid3">{cards.map(([k, v]) => <div key={k} className="card pad stat"><span className="muted">{k}</span><b>{v}</b></div>)}</div>
      <div className="grid2 gap">
        <div className="card pad"><h3>Average rent by bedrooms</h3>
          {s.averageRentByBedrooms.map((r) => (
            <div className="bar-row" key={r.bedrooms}><span>{r.bedrooms} BHK</span>
              <div className="bar"><i style={{ width: `${(r.averageRent / maxRent) * 100}%` }} /></div><span>{inr(r.averageRent)}</span></div>))}
        </div>
        <div className="card pad"><h3>Most common amenities</h3>
          {s.mostCommonAmenities.map((r) => (
            <div className="bar-row" key={r.amenity}><span>{r.amenity}</span>
              <div className="bar"><i style={{ width: `${(r.count / maxAm) * 100}%` }} /></div><span>{r.count}</span></div>))}
        </div>
      </div>
      {s.averageRentByCity && (
        <div className="card pad gap"><h3>Average rent by city</h3>
          {s.averageRentByCity.map((r) => (
            <div className="bar-row" key={r.city}><span>{r.city}</span>
              <div className="bar"><i style={{ width: `${(r.averageRent / Math.max(...s.averageRentByCity.map((x) => x.averageRent))) * 100}%` }} /></div><span>{inr(r.averageRent)}</span></div>))}
        </div>)}
      {best && <div className="card pad best-value"><h3>🏆 Best value apartment</h3>
        <p><Link to={`/apartments/${best.apartment._id}`}><b>{best.apartment.title}</b></Link> – {best.apartment.location}, {best.apartment.city} · {inr(best.apartment.rent)}/month · value score {best.valueScore}</p>
        <p className="muted">{best.reason}</p></div>}
    </>
  );
}

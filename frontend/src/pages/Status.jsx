import { useEffect, useState } from "react";
import { getApartmentHealth, getAdvisorStatus, API_URLS, errMsg } from "../services/api.js";
import { Loading } from "../components/State.jsx";

const Dot = ({ ok }) => <span className={"dot " + (ok ? "ok" : "bad")} />;

export default function Status() {
  const [apt, setApt] = useState(null);
  const [adv, setAdv] = useState(null);
  const [loading, setLoading] = useState(true);

  const check = async () => {
    setLoading(true);
    const t0 = performance.now();
    const a = await getApartmentHealth().then((d) => ({ ok: true, d, ms: Math.round(performance.now() - t0) })).catch((e) => ({ ok: false, err: errMsg(e) }));
    const t1 = performance.now();
    const b = await getAdvisorStatus().then((d) => ({ ok: true, d, ms: Math.round(performance.now() - t1) })).catch((e) => ({ ok: false, err: errMsg(e) }));
    setApt(a); setAdv(b); setLoading(false);
  };
  useEffect(() => { check(); }, []);

  return (
    <>
      <h1>System Status</h1>
      <p className="muted">Live health of both microservices and the REST link between them (useful for demonstration).</p>
      {loading ? <Loading text="Checking services (a sleeping free-tier server can take up to a minute)..." /> : (
        <div className="stack">
          <div className="card pad"><h3><Dot ok={apt.ok} /> Apartment Service (Microservice 1)</h3>
            <p className="muted">{API_URLS.apartment}</p>
            {apt.ok ? <p>Status: <b>{apt.d.status}</b> · Database: <b>{apt.d.database}</b> · Response: {apt.ms} ms</p> : <p className="err-text">{apt.err}</p>}</div>
          <div className="card pad"><h3><Dot ok={adv.ok} /> Rental Advisor Service (Microservice 2)</h3>
            <p className="muted">{API_URLS.advisor}</p>
            {adv.ok ? <p>Status: <b>{adv.d.status}</b> · Response: {adv.ms} ms · Saved searches DB: <b>{adv.d.savedSearchesEnabled ? "enabled" : "not configured"}</b></p> : <p className="err-text">{adv.err}</p>}</div>
          <div className="card pad"><h3><Dot ok={!!adv.d?.apartmentService?.reachable} /> Advisor → Apartment Service (inter-service REST call)</h3>
            {adv.ok ? (adv.d.apartmentService.reachable
              ? <p>Reachable · database: <b>{adv.d.apartmentService.database}</b> · round trip: {adv.d.apartmentService.latencyMs} ms</p>
              : <p className="err-text">{adv.d.apartmentService.error}</p>) : <p className="err-text">Advisor not reachable, so the link cannot be tested.</p>}</div>
          <div><button className="btn" onClick={check}>Re-check</button></div>
        </div>)}
    </>
  );
}

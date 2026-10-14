import { useState } from "react";
import { NavLink, Link } from "react-router-dom";
import { useCompare } from "../CompareContext.jsx";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { ids } = useCompare();
  const close = () => setOpen(false);
  return (
    <header className="nav">
      <div className="nav-inner">
        <Link to="/" className="brand" onClick={close}>🏠 RentWise</Link>
        <button className="burger" onClick={() => setOpen(!open)} aria-label="Menu">☰</button>
        <nav className={open ? "links open" : "links"} onClick={close}>
          <NavLink to="/apartments">Browse</NavLink>
          <NavLink to="/advisor">Rental Advisor</NavLink>
          <NavLink to="/compare">Compare{ids.length > 0 && <span className="pill">{ids.length}</span>}</NavLink>
          <NavLink to="/statistics">Statistics</NavLink>
          <NavLink to="/status">Status</NavLink>
          <NavLink to="/add" className="btn small">+ Add Apartment</NavLink>
        </nav>
      </div>
    </header>
  );
}

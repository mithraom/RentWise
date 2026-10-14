import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import Browse from "./pages/Browse.jsx";
import ApartmentDetails from "./pages/ApartmentDetails.jsx";
import Advisor from "./pages/Advisor.jsx";
import Recommendations from "./pages/Recommendations.jsx";
import Compare from "./pages/Compare.jsx";
import Statistics from "./pages/Statistics.jsx";
import Status from "./pages/Status.jsx";
import AddApartment from "./pages/AddApartment.jsx";
import EditApartment from "./pages/EditApartment.jsx";

export default function App() {
  return (
    <>
      <Navbar />
      <main className="container">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/apartments" element={<Browse />} />
          <Route path="/apartments/:id" element={<ApartmentDetails />} />
          <Route path="/apartments/:id/edit" element={<EditApartment />} />
          <Route path="/add" element={<AddApartment />} />
          <Route path="/advisor" element={<Advisor />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/statistics" element={<Statistics />} />
          <Route path="/status" element={<Status />} />
          <Route path="*" element={<div className="empty">Page not found.</div>} />
        </Routes>
      </main>
      <footer className="footer">RentWise – Full Stack Lab Mini Project</footer>
    </>
  );
}

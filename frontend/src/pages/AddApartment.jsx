import { useNavigate } from "react-router-dom";
import ApartmentForm from "../components/ApartmentForm.jsx";
import { createApartment, errMsg } from "../services/api.js";

export default function AddApartment() {
  const nav = useNavigate();
  const save = async (data) => {
    try { const a = await createApartment(data); nav(`/apartments/${a._id}`); } catch (e) { alert(errMsg(e)); }
  };
  return (<><h1>Add Apartment</h1><ApartmentForm onSubmit={save} submitText="Add Apartment" /></>);
}

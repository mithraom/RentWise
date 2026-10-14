import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import ApartmentForm from "../components/ApartmentForm.jsx";
import { Loading, ErrorBox } from "../components/State.jsx";
import { getApartment, updateApartment, errMsg } from "../services/api.js";

export default function EditApartment() {
  const { id } = useParams();
  const nav = useNavigate();
  const [apt, setApt] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { getApartment(id).then(setApt).catch((e) => setError(errMsg(e))); }, [id]);

  const save = async (data) => {
    const { _id, createdAt, ...body } = data;
    try { await updateApartment(id, body); nav(`/apartments/${id}`); } catch (e) { alert(errMsg(e)); }
  };
  if (error) return <ErrorBox message={error} />;
  if (!apt) return <Loading />;
  return (<><h1>Edit Apartment</h1><ApartmentForm initial={apt} onSubmit={save} submitText="Save Changes" /></>);
}

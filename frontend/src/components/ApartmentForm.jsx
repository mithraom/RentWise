import { useState } from "react";
import { AMENITIES, CITIES, FURNISHING, IMAGE_CHOICES } from "../utils.js";

const blank = { title: "", description: "", ownerName: "", location: "", city: "Coimbatore", rent: "", securityDeposit: "",
  bedrooms: 1, bathrooms: 1, areaSqFt: "", furnishing: "Semi-Furnished", availableFrom: new Date().toISOString().slice(0, 10),
  amenities: [], parking: false, petFriendly: false, commuteDistance: "", imageUrl: "" };

export default function ApartmentForm({ initial, onSubmit, submitText }) {
  const [f, setF] = useState({ ...blank, ...initial });
  const [saving, setSaving] = useState(false);
  const set = (k, v) => setF((p) => ({ ...p, [k]: v }));
  const toggleAm = (a) => set("amenities", f.amenities.includes(a) ? f.amenities.filter((x) => x !== a) : [...f.amenities, a]);

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    const num = (v) => (v === "" ? undefined : Number(v));
    await onSubmit({ ...f, rent: num(f.rent), securityDeposit: num(f.securityDeposit), areaSqFt: num(f.areaSqFt),
      commuteDistance: num(f.commuteDistance), bedrooms: Number(f.bedrooms), bathrooms: Number(f.bathrooms) });
    setSaving(false);
  };
  const input = (label, key, type = "text", extra = {}) => (
    <label>{label}<input type={type} value={f[key] ?? ""} onChange={(e) => set(key, e.target.value)} {...extra} /></label>
  );

  return (
    <form className="form card pad" onSubmit={submit}>
      <div className="grid2">
        {input("Title *", "title", "text", { required: true })}
        {input("Owner name", "ownerName")}
        {input("Location / Area *", "location", "text", { required: true })}
        <label>City *<select value={f.city} onChange={(e) => set("city", e.target.value)}>{CITIES.map((c) => <option key={c}>{c}</option>)}</select></label>
        {input("Monthly rent (₹) *", "rent", "number", { required: true, min: 1 })}
        {input("Security deposit (₹)", "securityDeposit", "number", { min: 0 })}
        {input("Bedrooms *", "bedrooms", "number", { required: true, min: 0 })}
        {input("Bathrooms *", "bathrooms", "number", { required: true, min: 0 })}
        {input("Area (sq.ft) *", "areaSqFt", "number", { required: true, min: 1 })}
        <label>Furnishing *<select value={f.furnishing} onChange={(e) => set("furnishing", e.target.value)}>{FURNISHING.map((c) => <option key={c}>{c}</option>)}</select></label>
        {input("Available from", "availableFrom", "date")}
        {input("Commute distance (km)", "commuteDistance", "number", { min: 0, step: "0.5" })}
      </div>
      <label>Apartment picture
        <select value={IMAGE_CHOICES.some((c) => c.value === f.imageUrl) ? f.imageUrl : (f.imageUrl ? "custom" : "")} onChange={(e) => set("imageUrl", e.target.value === "custom" ? "https://" : e.target.value)}>
          <option value="">Auto (match to size)</option>
          {IMAGE_CHOICES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
          <option value="custom">Custom image URL...</option>
        </select>
      </label>
      {f.imageUrl && !IMAGE_CHOICES.some((c) => c.value === f.imageUrl) && input("Image URL", "imageUrl", "url")}
      {f.imageUrl && <img className="form-preview" src={f.imageUrl} alt="Preview" onError={(e) => (e.target.style.display = "none")} onLoad={(e) => (e.target.style.display = "block")} />}
      <label>Description<textarea rows="3" value={f.description} onChange={(e) => set("description", e.target.value)} /></label>
      <fieldset><legend>Amenities</legend>
        <div className="checks">{AMENITIES.map((a) => (
          <label key={a} className="check"><input type="checkbox" checked={f.amenities.includes(a)} onChange={() => toggleAm(a)} /> {a}</label>))}</div>
      </fieldset>
      <div className="checks">
        <label className="check"><input type="checkbox" checked={f.parking} onChange={(e) => set("parking", e.target.checked)} /> Parking available</label>
        <label className="check"><input type="checkbox" checked={f.petFriendly} onChange={(e) => set("petFriendly", e.target.checked)} /> Pet friendly</label>
      </div>
      <button className="btn" disabled={saving}>{saving ? "Saving..." : submitText}</button>
    </form>
  );
}

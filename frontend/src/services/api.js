import axios from "axios";

// Microservice 1 – Apartment Service
const apartmentApi = axios.create({ baseURL: import.meta.env.VITE_APARTMENT_API_URL || "http://localhost:5001" });
// Microservice 2 – Rental Advisor Service
const advisorApi = axios.create({ baseURL: import.meta.env.VITE_ADVISOR_API_URL || "http://localhost:5002" });

export const errMsg = (e) =>
  e.response?.data?.details?.join(", ") || e.response?.data?.error ||
  (e.request ? "Cannot reach the server. Please try again in a moment." : e.message);

export const getApartments = (params = {}) => {
  const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== "" && v !== null));
  return apartmentApi.get("/api/apartments/search", { params: clean }).then((r) => r.data.data);
};
export const getApartment = (id) => apartmentApi.get(`/api/apartments/${id}`).then((r) => r.data.data);
export const createApartment = (b) => apartmentApi.post("/api/apartments", b).then((r) => r.data.data);
export const updateApartment = (id, b) => apartmentApi.put(`/api/apartments/${id}`, b).then((r) => r.data.data);
export const deleteApartment = (id) => apartmentApi.delete(`/api/apartments/${id}`);

export const getRecommendations = (prefs) => advisorApi.post("/api/recommendations", prefs).then((r) => r.data);
export const compareApartments = (apartmentIds, preferences) =>
  advisorApi.post("/api/compare", { apartmentIds, preferences }).then((r) => r.data);
export const getBestValue = () => advisorApi.get("/api/recommendations/best-value").then((r) => r.data.data);
export const getStatistics = () => advisorApi.get("/api/recommendations/statistics").then((r) => r.data.data);

// Saved searches live in the Rental Advisor Service's own database
export const getSavedSearches = () => advisorApi.get("/api/saved-searches").then((r) => r.data.data);
export const saveSearch = (name, preferences) => advisorApi.post("/api/saved-searches", { name, preferences }).then((r) => r.data.data);
export const deleteSavedSearch = (id) => advisorApi.delete(`/api/saved-searches/${id}`);

// System status: pings both services and the link between them
export const API_URLS = { apartment: apartmentApi.defaults.baseURL, advisor: advisorApi.defaults.baseURL };
export const getApartmentHealth = () => apartmentApi.get("/health").then((r) => r.data);
export const getAdvisorStatus = () => advisorApi.get("/api/status").then((r) => r.data);

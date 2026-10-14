export const inr = (n) => "₹" + Number(n || 0).toLocaleString("en-IN");
export const CITIES = ["Coimbatore", "Chennai", "Bangalore", "Kochi", "Hyderabad"];
export const FURNISHING = ["Unfurnished", "Semi-Furnished", "Fully-Furnished"];
export const AMENITIES = ["WiFi", "Parking", "Gym", "Security", "Power Backup", "Lift",
  "Swimming Pool", "Play Area", "Air Conditioning", "Water Supply"];
const LOCAL_IMGS = ["apt-1bhk-compact", "apt-1bhk-modern", "apt-2bhk-family", "apt-2bhk-garden", "apt-3bhk-premium", "apt-3bhk-luxury", "apt-tower"];
// Picks the illustration that fits the apartment. Old picsum/random photo URLs are ignored.
export const aptImage = (apt) => {
  const u = apt?.imageUrl || "";
  if (u && !u.includes("picsum.photos")) return u;
  const bed = apt?.bedrooms || 1;
  if (bed >= 3) return apt.rent >= 30000 ? "/images/apt-3bhk-luxury.svg" : "/images/apt-3bhk-premium.svg";
  if (bed === 2) return apt.furnishing === "Unfurnished" ? "/images/apt-2bhk-garden.svg" : "/images/apt-2bhk-family.svg";
  return apt?.furnishing === "Fully-Furnished" ? "/images/apt-1bhk-modern.svg" : "/images/apt-1bhk-compact.svg";
};
export const IMAGE_CHOICES = LOCAL_IMGS.map((n) => ({ label: n.replace("apt-", "").replace(/-/g, " "), value: `/images/${n}.svg` }));
export const FALLBACK_IMG = "/images/apt-default.svg";
export const FALLBACK_IMG_OLD = "data:image/svg+xml;utf8," + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420"><rect width="100%" height="100%" fill="#e2e8f0"/><text x="50%" y="50%" text-anchor="middle" fill="#64748b" font-family="sans-serif" font-size="28">No image</text></svg>');

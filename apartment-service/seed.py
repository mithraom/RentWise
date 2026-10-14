"""Load 20 sample apartments into rentwise_db.apartments.
Usage:  python seed.py          (adds data only if the collection is empty)
        python seed.py --reset  (clears the collection first)"""
import sys
from datetime import datetime, timedelta, timezone
from env_loader import load_env

load_env()
from models.apartment import get_collection  # noqa: E402

U, S, F = "Unfurnished", "Semi-Furnished", "Fully-Furnished"
# (title, owner, location, city, rent, deposit, bed, bath, area, furnishing, amenities, parking, pet, commute)
ROWS = [
    ("Green Valley 2BHK", "Ravi Kumar", "RS Puram", "Coimbatore", 18000, 54000, 2, 2, 1100, S, ["WiFi", "Parking", "Security", "Power Backup"], True, True, 5),
    ("Sunrise Residency 2BHK", "Meena Iyer", "Saravanampatty", "Coimbatore", 15500, 46500, 2, 2, 1000, S, ["Parking", "WiFi", "Gym", "Lift"], True, True, 7),
    ("Peelamedu Compact 1BHK", "S. Arun", "Peelamedu", "Coimbatore", 9500, 28500, 1, 1, 600, F, ["WiFi", "Security"], False, False, 3),
    ("Gandhipuram Family 3BHK", "K. Lakshmi", "Gandhipuram", "Coimbatore", 24000, 72000, 3, 3, 1500, S, ["Parking", "Lift", "Security", "Power Backup", "Play Area"], True, True, 4),
    ("Race Course Luxury 3BHK", "Dr. Prakash", "Race Course", "Coimbatore", 32000, 128000, 3, 3, 1800, F, ["WiFi", "Parking", "Gym", "Swimming Pool", "Air Conditioning", "Lift"], True, False, 2),
    ("Singanallur Budget 2BHK", "P. Murugan", "Singanallur", "Coimbatore", 14000, 42000, 2, 1, 900, U, ["Parking", "Water Supply"], True, True, 9),
    ("Adyar Heritage 2BHK", "Nirmala Devi", "Adyar", "Chennai", 28000, 112000, 2, 2, 1050, F, ["WiFi", "Parking", "Lift", "Security", "Power Backup"], True, False, 6),
    ("Velachery Metro 2BHK", "R. Sundar", "Velachery", "Chennai", 22000, 88000, 2, 2, 980, S, ["WiFi", "Parking", "Gym", "Security"], True, True, 4),
    ("OMR Tech Park 3BHK", "Anand Rao", "Sholinganallur", "Chennai", 35000, 140000, 3, 3, 1650, F, ["WiFi", "Parking", "Gym", "Swimming Pool", "Air Conditioning", "Play Area"], True, True, 3),
    ("Anna Nagar Studio 1BHK", "Fathima B.", "Anna Nagar", "Chennai", 15000, 60000, 1, 1, 650, S, ["WiFi", "Security", "Lift"], False, False, 5),
    ("Whitefield Garden 2BHK", "Vikram Shetty", "Whitefield", "Bangalore", 32000, 160000, 2, 2, 1200, S, ["WiFi", "Parking", "Gym", "Swimming Pool", "Security"], True, True, 8),
    ("Koramangala Nest 1BHK", "Priya Nair", "Koramangala", "Bangalore", 26000, 130000, 1, 1, 700, F, ["WiFi", "Air Conditioning", "Security", "Power Backup"], False, False, 3),
    ("HSR Layout Premium 3BHK", "Suresh Gowda", "HSR Layout", "Bangalore", 48000, 240000, 3, 3, 1700, F, ["WiFi", "Parking", "Gym", "Swimming Pool", "Lift", "Air Conditioning"], True, True, 5),
    ("Electronic City Value 1BHK", "M. Harish", "Electronic City", "Bangalore", 14000, 70000, 1, 1, 580, U, ["Parking", "Security", "Water Supply"], True, False, 10),
    ("Kakkanad Infopark 2BHK", "Joseph Mathew", "Kakkanad", "Kochi", 20000, 80000, 2, 2, 1050, S, ["WiFi", "Parking", "Gym", "Lift", "Power Backup"], True, True, 4),
    ("Edappally Comfort 2BHK", "Anitha Menon", "Edappally", "Kochi", 18500, 74000, 2, 2, 1000, S, ["Parking", "WiFi", "Security"], True, False, 6),
    ("Marine Drive Sea View 3BHK", "Thomas Varghese", "Marine Drive", "Kochi", 38000, 190000, 3, 3, 1600, F, ["WiFi", "Parking", "Lift", "Air Conditioning", "Security", "Swimming Pool"], True, False, 2),
    ("Gachibowli Skyline 2BHK", "Srinivas Reddy", "Gachibowli", "Hyderabad", 30000, 150000, 2, 2, 1150, F, ["WiFi", "Parking", "Gym", "Swimming Pool", "Security", "Lift"], True, True, 5),
    ("Madhapur Urban 1BHK", "Kavitha R.", "Madhapur", "Hyderabad", 22000, 110000, 1, 1, 680, F, ["WiFi", "Air Conditioning", "Security"], False, True, 3),
    ("Kondapur Family 3BHK", "Ramesh Babu", "Kondapur", "Hyderabad", 42000, 210000, 3, 3, 1750, S, ["WiFi", "Parking", "Gym", "Play Area", "Lift", "Power Backup"], True, True, 7),
]

AMENITY_DESC = "Amenities include {}."


def image_for(bed, furn, rent, n_amenities):
    """Pick a matching illustration shipped with the frontend (frontend/public/images)."""
    if bed >= 3:
        return "/images/apt-3bhk-luxury.svg" if rent >= 30000 or n_amenities >= 6 else "/images/apt-3bhk-premium.svg"
    if bed == 2:
        return "/images/apt-2bhk-garden.svg" if furn == "Unfurnished" or rent < 16000 else "/images/apt-2bhk-family.svg"
    return "/images/apt-1bhk-modern.svg" if furn == "Fully-Furnished" else "/images/apt-1bhk-compact.svg"


def build_docs():
    now = datetime.now(timezone.utc)
    docs = []
    for i, r in enumerate(ROWS):
        title, owner, loc, city, rent, dep, bed, bath, area, furn, am, park, pet, commute = r
        docs.append({
            "title": title,
            "description": f"{bed}BHK {furn.lower()} apartment in {loc}, {city}. {AMENITY_DESC.format(', '.join(am))}",
            "ownerName": owner, "location": loc, "city": city, "rent": rent,
            "securityDeposit": dep, "bedrooms": bed, "bathrooms": bath, "areaSqFt": area,
            "furnishing": furn, "availableFrom": (now + timedelta(days=(i * 11) % 35 - 22)).strftime("%Y-%m-%d"),
            "amenities": am, "parking": park, "petFriendly": pet, "commuteDistance": commute,
            "imageUrl": image_for(bed, furn, rent, len(am)),
            "createdAt": (now - timedelta(hours=i)).isoformat(),
        })
    return docs


if __name__ == "__main__":
    col = get_collection()
    if "--reset" in sys.argv:
        col.delete_many({})
    if col.count_documents({}) == 0:
        col.insert_many(build_docs())
        print(f"Inserted {len(ROWS)} sample apartments")
    else:
        print("Collection already has data. Use --reset to reseed.")

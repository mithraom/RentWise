"""Rental Advisor tests: the Apartment Service is replaced by a fake HTTP client. Run: pytest"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import mongomock, pytest
import services.apartment_client as ac
import routes.recommendations as rec

APTS = [
    {"_id": "1", "title": "A", "city": "Coimbatore", "location": "RS Puram", "rent": 18000, "securityDeposit": 54000, "bedrooms": 2,
     "bathrooms": 2, "areaSqFt": 1000, "furnishing": "Semi-Furnished", "amenities": ["WiFi", "Parking"], "parking": True,
     "petFriendly": True, "commuteDistance": 4, "availableFrom": "2026-01-01"},
    {"_id": "2", "title": "B", "city": "Chennai", "location": "Adyar", "rent": 40000, "securityDeposit": 80000, "bedrooms": 3,
     "bathrooms": 3, "areaSqFt": 1500, "furnishing": "Fully-Furnished", "amenities": ["Gym"], "parking": False,
     "petFriendly": False, "commuteDistance": 12, "availableFrom": "2026-01-01"},
]

@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(rec.client, "fetch_all_apartments", lambda params=None: APTS)
    monkeypatch.setattr(rec.client, "fetch_apartment", lambda i: next(a for a in APTS if a["_id"] == i))
    import models.saved_search as ss, routes.saved_searches as rs, app as appmod
    col = mongomock.MongoClient()["t"]["s"]
    monkeypatch.setattr(rs, "get_collection", lambda: col)
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client()

PREFS = {"budget": 20000, "preferredCity": "Coimbatore", "bedrooms": 2, "requiredAmenities": ["WiFi"]}

def test_recommend_ranks_best_first(client):
    r = client.post("/api/recommendations", json=PREFS).get_json()
    assert r["data"][0]["apartment"]["_id"] == "1"
    assert r["data"][0]["recommendationScore"] > r["data"][1]["recommendationScore"]

def test_recommend_needs_budget(client):
    assert client.post("/api/recommendations", json={}).status_code == 400

def test_compare_and_validation(client):
    assert client.post("/api/compare", json={"apartmentIds": ["1", "2"]}).status_code == 200
    assert client.post("/api/compare", json={"apartmentIds": ["1"]}).status_code == 400

def test_statistics_and_best_value(client):
    s = client.get("/api/recommendations/statistics").get_json()["data"]
    assert s["totalApartments"] == 2 and len(s["averageRentByCity"]) == 2
    assert client.get("/api/recommendations/best-value").status_code == 200

def test_apartment_service_down_returns_503(client, monkeypatch):
    def boom(params=None):
        raise ac.ApartmentServiceError("Apartment Service is unavailable. Please try again later.")
    monkeypatch.setattr(rec.client, "fetch_all_apartments", boom)
    r = client.post("/api/recommendations", json=PREFS)
    assert r.status_code == 503 and r.get_json()["success"] is False

def test_saved_searches_crud(client):
    sid = client.post("/api/saved-searches", json={"name": "Mine", "preferences": PREFS}).get_json()["data"]["_id"]
    assert client.get("/api/saved-searches").get_json()["count"] == 1
    assert client.put(f"/api/saved-searches/{sid}", json={"name": "Renamed"}).get_json()["data"]["name"] == "Renamed"
    assert client.delete(f"/api/saved-searches/{sid}").status_code == 200
    assert client.delete(f"/api/saved-searches/{sid}").status_code == 404

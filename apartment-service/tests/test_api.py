"""Apartment Service API tests (in-memory MongoDB via mongomock). Run: pytest"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import mongomock, pytest
import models.apartment as m

@pytest.fixture()
def client(monkeypatch):
    col = mongomock.MongoClient()["t"]["apartments"]
    monkeypatch.setattr(m, "get_collection", lambda: col)
    import routes.apartments as r, app as appmod
    monkeypatch.setattr(r, "get_collection", lambda: col)
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client()

GOOD = {"title": "Test 2BHK", "location": "RS Puram", "city": "Coimbatore", "rent": 18000, "bedrooms": 2,
        "bathrooms": 2, "areaSqFt": 1000, "furnishing": "Semi-Furnished", "amenities": ["WiFi"], "petFriendly": True}

def test_health(client):
    assert client.get("/").get_json()["status"] == "running"

def test_create_and_get(client):
    r = client.post("/api/apartments", json=GOOD)
    assert r.status_code == 201
    _id = r.get_json()["data"]["_id"]
    assert client.get(f"/api/apartments/{_id}").get_json()["data"]["title"] == "Test 2BHK"

def test_create_validation(client):
    r = client.post("/api/apartments", json={"title": "x"})
    assert r.status_code == 400 and r.get_json()["details"]

def test_update_delete_404(client):
    _id = client.post("/api/apartments", json=GOOD).get_json()["data"]["_id"]
    assert client.put(f"/api/apartments/{_id}", json={"rent": 20000}).get_json()["data"]["rent"] == 20000
    assert client.delete(f"/api/apartments/{_id}").status_code == 200
    assert client.get(f"/api/apartments/{_id}").status_code == 404

def test_invalid_id(client):
    assert client.get("/api/apartments/abc").status_code == 400

def test_search_sort_text(client):
    client.post("/api/apartments", json=GOOD)
    client.post("/api/apartments", json={**GOOD, "title": "Cheap 1BHK", "rent": 8000, "bedrooms": 1, "city": "Chennai", "location": "Adyar"})
    assert client.get("/api/apartments/search?city=chennai").get_json()["count"] == 1
    assert client.get("/api/apartments/search?maxRent=10000").get_json()["count"] == 1
    assert client.get("/api/apartments/search?q=adyar").get_json()["count"] == 1
    rents = [a["rent"] for a in client.get("/api/apartments?sort=rentAsc").get_json()["data"]]
    assert rents == sorted(rents)
    assert client.get("/api/apartments?sort=bogus").status_code == 400

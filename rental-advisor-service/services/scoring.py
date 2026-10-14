"""Rule-based, explainable scoring.

recommendationScore (0-100) = budget 30 + location 20 + bedrooms 15 + amenities 15
                              + furnishing 10 + commute 5 + pet-friendly 5
"""
from datetime import datetime, timedelta

WEIGHTS = {"budget": 30, "location": 20, "bedrooms": 15, "amenities": 15,
           "furnishing": 10, "commute": 5, "petFriendly": 5}


def _n(x):
    return str(x).strip().lower()


def amenity_set(apt):
    """Lower-cased amenities; the 'parking' flag also counts as the Parking amenity."""
    s = {_n(a) for a in apt.get("amenities", [])}
    if apt.get("parking"):
        s.add("parking")
    return s


def label_for(score):
    if score >= 85:
        return "Excellent Match"
    if score >= 70:
        return "Good Match"
    if score >= 50:
        return "Fair Match"
    return "Low Match"


def score_apartment(apt, prefs):
    rent = apt.get("rent", 0)
    b, good, warn = {}, [], []

    # 1. Budget (30): full marks within budget, linearly down to 0 at 120% of budget
    budget = prefs.get("budget")
    if not budget:
        b["budget"], afford = 30, "No budget given"
    elif rent <= budget:
        b["budget"] = 30
        afford = "Well within budget" if rent <= 0.85 * budget else "Within budget"
        good.append("fits your budget")
    elif rent <= budget * 1.2:
        b["budget"] = round(30 * (1 - (rent - budget) / (budget * 0.2)), 1)
        afford = "Slightly over budget"
        warn.append("rent is slightly above your budget")
    else:
        b["budget"], afford = 0, "Over budget"
        warn.append("rent is above your budget")

    # 2. Location (20): city = 12 points, area/locality match = 8 more
    city, area = prefs.get("preferredCity"), prefs.get("preferredLocation")
    city_ok = (not city) or _n(apt.get("city", "")) == _n(city)
    area_ok = (not area) or _n(area) in _n(apt.get("location", ""))
    if not area:
        b["location"] = 20 if city_ok else 0
    else:
        b["location"] = (12 if city_ok else 0) + (8 if area_ok else 0)
    location_match = city_ok and area_ok
    (good if location_match else warn).append(
        "is in your preferred location" if location_match else "is outside your preferred location")

    # 3. Bedrooms (15): exact 15, bigger 10, one fewer 5
    req = prefs.get("bedrooms")
    have = apt.get("bedrooms", 0)
    if not req or have == req:
        b["bedrooms"] = 15
        if req:
            good.append("matches your bedroom requirement")
    elif have > req:
        b["bedrooms"] = 10
        good.append("has more bedrooms than required")
    elif have == req - 1:
        b["bedrooms"] = 5
        warn.append("has one bedroom fewer than required")
    else:
        b["bedrooms"] = 0
        warn.append("has too few bedrooms")

    # 4. Amenities (15): proportional to the share of requested amenities provided
    have_am = amenity_set(apt)
    required = prefs.get("requiredAmenities") or []
    matched = [a for a in required if _n(a) in have_am]
    missing = [a for a in required if _n(a) not in have_am]
    b["amenities"] = round(15 * len(matched) / len(required), 1) if required else 15
    if required:
        (good if not missing else warn).append(
            "provides all requested amenities" if not missing else f"is missing {', '.join(missing)}")

    # 5. Furnishing (10): exact 10, Semi vs other 5
    want = prefs.get("furnishing")
    if not want or _n(want) == "any" or _n(want) == _n(apt.get("furnishing", "")):
        b["furnishing"] = 10
    elif "semi" in (_n(want), _n(apt.get("furnishing", ""))):
        b["furnishing"] = 5
    else:
        b["furnishing"] = 0

    # 6. Commute (5): within limit 5, linearly to 0 at twice the limit
    limit, dist = prefs.get("maxCommuteDistance"), apt.get("commuteDistance", 0)
    if not limit or dist <= limit:
        b["commute"] = 5
        if limit:
            good.append(f"has a short commute ({dist} km)")
    elif dist < limit * 2:
        b["commute"] = round(5 * (1 - (dist - limit) / limit), 1)
        warn.append("commute is longer than preferred")
    else:
        b["commute"] = 0
        warn.append("commute is much longer than preferred")

    # 7. Pet friendly (5)
    if prefs.get("petFriendly") and not apt.get("petFriendly"):
        b["petFriendly"] = 0
        warn.append("is not pet friendly")
    else:
        b["petFriendly"] = 5

    total = int(round(sum(b.values())))
    reason = "This apartment " + (", ".join(good) if good else "partly matches your needs")
    if warn:
        reason += ", but " + " and ".join(warn)
    reason += "."
    return {
        "apartment": apt,
        "recommendationScore": total,
        "matchLabel": label_for(total),
        "scoreBreakdown": b,
        "maxScores": WEIGHTS,
        "matchedAmenities": matched,
        "missingAmenities": missing,
        "affordabilityStatus": afford,
        "locationMatch": location_match,
        "reason": reason,
    }


def validate_preferences(data):
    """Return (clean_prefs, errors) for the POST /api/recommendations body."""
    if not isinstance(data, dict):
        return None, ["Request body must be a JSON object"]
    errors, p = [], {}

    def num(key, required=False, integer=False):
        v = data.get(key)
        if v in (None, ""):
            if required:
                errors.append(f"{key} is required")
            return
        try:
            f = float(v)
            if f <= 0 and key != "maxCommuteDistance" or f < 0:
                raise ValueError
            p[key] = int(f) if integer or f.is_integer() else f
        except (TypeError, ValueError):
            errors.append(f"{key} must be a positive number")

    num("budget", required=True)
    num("bedrooms", integer=True)
    num("maxCommuteDistance")
    for k in ("preferredCity", "preferredLocation", "furnishing"):
        if data.get(k):
            p[k] = str(data[k]).strip()
    am = data.get("requiredAmenities", [])
    if isinstance(am, list) and all(isinstance(a, str) for a in am):
        p["requiredAmenities"] = am
    else:
        errors.append("requiredAmenities must be a list of strings")
    if "petFriendly" in data:
        if isinstance(data["petFriendly"], bool):
            p["petFriendly"] = data["petFriendly"]
        else:
            errors.append("petFriendly must be true or false")
    return p, errors


def value_scores(apartments):
    """'Best value' score (0-100) for each apartment, relative to the whole list:
    price per sq.ft 40 + facilities 25 + short commute 20 + space 15."""
    if not apartments:
        return {}
    ppsf = {a["_id"]: a["rent"] / max(a.get("areaSqFt") or 1, 1) for a in apartments}
    lo, hi = min(ppsf.values()), max(ppsf.values())
    max_area = max((a.get("areaSqFt") or 0) for a in apartments) or 1
    out = {}
    for a in apartments:
        price = 40 if hi == lo else 40 * (hi - ppsf[a["_id"]]) / (hi - lo)
        facilities = 25 * min(len(amenity_set(a)), 8) / 8
        commute = 20 * max(0, 1 - (a.get("commuteDistance") or 0) / 20)
        space = 15 * (a.get("areaSqFt") or 0) / max_area
        out[a["_id"]] = round(price + facilities + commute + space, 1)
    return out


def available_now(apt):
    try:
        return datetime.strptime(apt.get("availableFrom", ""), "%Y-%m-%d") <= datetime.now()
    except ValueError:
        return True

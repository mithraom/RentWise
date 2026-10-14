"""Input validation for apartment payloads."""
from datetime import datetime

FURNISHING = ["Unfurnished", "Semi-Furnished", "Fully-Furnished"]
REQUIRED = ["title", "location", "city", "rent", "bedrooms", "bathrooms", "areaSqFt", "furnishing"]
TEXT = ["title", "description", "ownerName", "location", "city", "imageUrl"]
# field: (must_be_integer, minimum)
NUMERIC = {
    "rent": (False, 1), "securityDeposit": (False, 0), "bedrooms": (True, 0),
    "bathrooms": (True, 0), "areaSqFt": (False, 1), "commuteDistance": (False, 0),
}
BOOLEAN = ["parking", "petFriendly"]


def validate_apartment(data, partial=False):
    """Return (clean_data, errors). partial=True is used for updates."""
    if not isinstance(data, dict):
        return None, ["Request body must be a JSON object"]
    errors, clean = [], {}

    if not partial:
        errors += [f"{f} is required" for f in REQUIRED if data.get(f) in (None, "")]

    for f in TEXT:
        if f in data:
            if not isinstance(data[f], str):
                errors.append(f"{f} must be a string")
            else:
                clean[f] = data[f].strip()

    for f, (is_int, minimum) in NUMERIC.items():
        if f in data and data[f] not in (None, ""):
            v = data[f]
            if isinstance(v, bool) or not isinstance(v, (int, float, str)):
                errors.append(f"{f} must be a number")
                continue
            try:
                v = float(v)
            except ValueError:
                errors.append(f"{f} must be a number")
                continue
            if v < minimum:
                errors.append(f"{f} must be at least {minimum}")
            elif is_int and not v.is_integer():
                errors.append(f"{f} must be a whole number")
            else:
                clean[f] = int(v) if v.is_integer() else v

    for f in BOOLEAN:
        if f in data:
            if isinstance(data[f], bool):
                clean[f] = data[f]
            else:
                errors.append(f"{f} must be true or false")

    if "furnishing" in data and data["furnishing"] not in (None, ""):
        if data["furnishing"] in FURNISHING:
            clean["furnishing"] = data["furnishing"]
        else:
            errors.append(f"furnishing must be one of {FURNISHING}")

    if "amenities" in data:
        a = data["amenities"]
        if isinstance(a, list) and all(isinstance(x, str) for x in a):
            clean["amenities"] = [x.strip() for x in a if x.strip()]
        else:
            errors.append("amenities must be a list of strings")

    if "availableFrom" in data and data["availableFrom"]:
        try:
            datetime.strptime(data["availableFrom"], "%Y-%m-%d")
            clean["availableFrom"] = data["availableFrom"]
        except (ValueError, TypeError):
            errors.append("availableFrom must be a date in YYYY-MM-DD format")

    return clean, errors

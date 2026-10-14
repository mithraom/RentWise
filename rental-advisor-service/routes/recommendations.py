"""REST API routes of the Rental Advisor Service."""
from collections import Counter
from flask import Blueprint, jsonify, request
from services import apartment_client as client
from services.scoring import (score_apartment, validate_preferences, value_scores,
                              available_now, amenity_set)

bp = Blueprint("advisor", __name__)


def error(message, status, details=None):
    body = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


@bp.route("/api/recommendations", methods=["POST"])
def recommend():
    prefs, errors = validate_preferences(request.get_json(silent=True))
    if errors:
        return error("Invalid request", 400, errors)
    apartments = client.fetch_all_apartments()          # REST call to Apartment Service
    results = [score_apartment(a, prefs) for a in apartments]
    results.sort(key=lambda r: r["recommendationScore"], reverse=True)
    try:
        limit = max(1, int(request.args.get("limit", 6)))
    except ValueError:
        limit = 6
    return jsonify({"success": True, "count": len(results[:limit]),
                    "totalEvaluated": len(results), "preferences": prefs,
                    "data": results[:limit]}), 200


@bp.route("/api/recommendations/best-value", methods=["GET"])
def best_value():
    params = {"city": request.args["city"]} if request.args.get("city") else None
    apartments = client.fetch_all_apartments(params)
    if not apartments:
        return error("No apartments available", 404)
    scores = value_scores(apartments)
    ranked = sorted(apartments, key=lambda a: scores[a["_id"]], reverse=True)
    best = ranked[0]
    reason = (f"Rs.{best['rent']:,} for {best['areaSqFt']} sq.ft "
              f"(about Rs.{best['rent'] / best['areaSqFt']:.1f} per sq.ft) with "
              f"{len(amenity_set(best))} amenities and a {best['commuteDistance']} km commute.")
    return jsonify({"success": True, "data": {
        "apartment": best, "valueScore": scores[best["_id"]], "reason": reason,
        "runnersUp": [{"apartment": a, "valueScore": scores[a["_id"]]} for a in ranked[1:4]],
    }}), 200


@bp.route("/api/recommendations/statistics", methods=["GET"])
def statistics():
    apts = client.fetch_all_apartments()
    if not apts:
        return jsonify({"success": True, "data": {"totalApartments": 0}}), 200
    rents = [a["rent"] for a in apts]
    areas = [a["areaSqFt"] for a in apts]
    by_bed = {}
    for a in apts:
        by_bed.setdefault(a["bedrooms"], []).append(a["rent"])
    by_city = {}
    for a in apts:
        by_city.setdefault(a["city"], []).append(a["rent"])
    common = Counter(am for a in apts for am in amenity_set(a))
    names = {am.lower(): am for a in apts for am in a.get("amenities", [])}   # keep original spelling (e.g. WiFi)
    return jsonify({"success": True, "data": {
        "totalApartments": len(apts),
        "availableApartments": sum(1 for a in apts if available_now(a)),
        "averageRent": round(sum(rents) / len(rents)),
        "minimumRent": min(rents),
        "maximumRent": max(rents),
        "averageArea": round(sum(areas) / len(areas)),
        "averageRentByBedrooms": [
            {"bedrooms": k, "averageRent": round(sum(v) / len(v)), "count": len(v)}
            for k, v in sorted(by_bed.items())],
        "averageRentByCity": [
            {"city": k, "averageRent": round(sum(v) / len(v)), "count": len(v)}
            for k, v in sorted(by_city.items())],
        "mostCommonAmenities": [{"amenity": names.get(k, k.title()), "count": v} for k, v in common.most_common(6)],
    }}), 200


@bp.route("/api/compare", methods=["POST"])
def compare():
    body = request.get_json(silent=True) or {}
    ids = body.get("apartmentIds")
    if not isinstance(ids, list) or not 2 <= len(ids) <= 3 or len(set(ids)) != len(ids):
        return error("Provide 2 or 3 different apartment ids in 'apartmentIds'", 400)
    prefs = None
    if body.get("preferences"):
        prefs, errors = validate_preferences(body["preferences"])
        if errors:
            return error("Invalid preferences", 400, errors)

    apartments = [client.fetch_apartment(i) for i in ids]       # REST call per apartment
    if prefs:
        scored = {a["_id"]: score_apartment(a, prefs)["recommendationScore"] for a in apartments}
        score_type = "match"
    else:                                                       # no preferences -> value score
        everything = client.fetch_all_apartments()
        vs = value_scores(everything)
        scored = {a["_id"]: vs.get(a["_id"], 0) for a in apartments}
        score_type = "value"

    def best(key, lowest=False):
        pick = min if lowest else max
        return pick(apartments, key=key)["_id"]

    highlights = {
        "rent": best(lambda a: a["rent"], True),
        "securityDeposit": best(lambda a: a["securityDeposit"], True),
        "bedrooms": best(lambda a: a["bedrooms"]),
        "bathrooms": best(lambda a: a["bathrooms"]),
        "areaSqFt": best(lambda a: a["areaSqFt"]),
        "amenities": best(lambda a: len(a.get("amenities", []))),
        "commuteDistance": best(lambda a: a["commuteDistance"], True),
        "score": best(lambda a: scored[a["_id"]]),
    }
    rows = [{**a, "score": scored[a["_id"]], "amenityCount": len(a.get("amenities", []))} for a in apartments]
    return jsonify({"success": True, "scoreType": score_type, "data": rows,
                    "highlights": highlights, "bestValueId": highlights["score"]}), 200

"""REST API routes of the Apartment Management Service (CRUD + search)."""
import re
from datetime import datetime, timezone
from bson import ObjectId
from flask import Blueprint, jsonify, request
from models.apartment import get_collection, serialize
from services.validation import validate_apartment

bp = Blueprint("apartments", __name__)

DEFAULTS = {
    "description": "", "ownerName": "", "securityDeposit": 0, "amenities": [],
    "parking": False, "petFriendly": False, "commuteDistance": 0, "imageUrl": "",
}


def error(message, status, details=None):
    body = {"success": False, "error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


def to_bool(v):
    return str(v).lower() in ("true", "1", "yes")


def build_query(args):
    """Translate query-string filters into a MongoDB query."""
    q = {}
    if args.get("city"):
        q["city"] = {"$regex": f"^{re.escape(args['city'])}$", "$options": "i"}
    if args.get("location"):
        q["location"] = {"$regex": re.escape(args["location"]), "$options": "i"}
    rent = {}
    for key, op in (("minRent", "$gte"), ("maxRent", "$lte")):
        if args.get(key):
            try:
                rent[op] = float(args[key])
            except ValueError:
                raise ValueError(f"{key} must be a number")
    if rent:
        q["rent"] = rent
    if args.get("bedrooms"):
        try:
            q["bedrooms"] = int(args["bedrooms"])
        except ValueError:
            raise ValueError("bedrooms must be a whole number")
    if args.get("furnishing"):
        q["furnishing"] = args["furnishing"]
    if args.get("petFriendly") not in (None, ""):
        q["petFriendly"] = to_bool(args["petFriendly"])
    if args.get("parking") not in (None, ""):
        q["parking"] = to_bool(args["parking"])
    if args.get("maxCommute"):
        try:
            q["commuteDistance"] = {"$lte": float(args["maxCommute"])}
        except ValueError:
            raise ValueError("maxCommute must be a number")
    if args.get("q"):                      # free-text search over title / location / description
        rx = {"$regex": re.escape(args["q"].strip()), "$options": "i"}
        q["$or"] = [{"title": rx}, {"location": rx}, {"description": rx}, {"amenities": rx}]
    return q


SORTS = {
    "newest": [("createdAt", -1)], "rentAsc": [("rent", 1)], "rentDesc": [("rent", -1)],
    "areaDesc": [("areaSqFt", -1)], "commuteAsc": [("commuteDistance", 1)],
}


def oid_or_none(id_):
    return ObjectId(id_) if ObjectId.is_valid(id_) else None


@bp.route("/api/apartments", methods=["POST"])
def create_apartment():
    clean, errors = validate_apartment(request.get_json(silent=True))
    if errors:
        return error("Invalid request", 400, errors)
    now = datetime.now(timezone.utc)
    doc = {**DEFAULTS, "availableFrom": now.strftime("%Y-%m-%d"), **clean, "createdAt": now.isoformat()}
    result = get_collection().insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return jsonify({"success": True, "message": "Apartment created", "data": doc}), 201


def _list(args):
    try:
        query = build_query(args)
    except ValueError as e:
        return error(str(e), 400)
    sort = SORTS.get(args.get("sort", "newest"))
    if sort is None:
        return error(f"sort must be one of {list(SORTS)}", 400)
    docs = get_collection().find(query).sort(sort)
    data = [serialize(d) for d in docs]
    return jsonify({"success": True, "count": len(data), "data": data}), 200


@bp.route("/api/apartments", methods=["GET"])
def list_apartments():
    return _list(request.args)


@bp.route("/api/apartments/search", methods=["GET"])
def search_apartments():
    return _list(request.args)


@bp.route("/api/apartments/<id>", methods=["GET"])
def get_apartment(id):
    oid = oid_or_none(id)
    if not oid:
        return error("Invalid apartment id", 400)
    doc = get_collection().find_one({"_id": oid})
    if not doc:
        return error("Apartment not found", 404)
    return jsonify({"success": True, "data": serialize(doc)}), 200


@bp.route("/api/apartments/<id>", methods=["PUT"])
def update_apartment(id):
    oid = oid_or_none(id)
    if not oid:
        return error("Invalid apartment id", 400)
    clean, errors = validate_apartment(request.get_json(silent=True), partial=True)
    if errors:
        return error("Invalid request", 400, errors)
    if not clean:
        return error("No valid fields to update", 400)
    result = get_collection().find_one_and_update({"_id": oid}, {"$set": clean}, return_document=True)
    if not result:
        return error("Apartment not found", 404)
    return jsonify({"success": True, "message": "Apartment updated", "data": serialize(result)}), 200


@bp.route("/api/apartments/<id>", methods=["DELETE"])
def delete_apartment(id):
    oid = oid_or_none(id)
    if not oid:
        return error("Invalid apartment id", 400)
    if get_collection().delete_one({"_id": oid}).deleted_count == 0:
        return error("Apartment not found", 404)
    return jsonify({"success": True, "message": "Apartment deleted"}), 200

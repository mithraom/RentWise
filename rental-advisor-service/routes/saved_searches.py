"""CRUD for saved searches (the Advisor's own data, stored in its own MongoDB database)."""
from datetime import datetime, timezone
from bson import ObjectId
from flask import Blueprint, jsonify, request
from models.saved_search import get_collection, serialize
from services.scoring import validate_preferences

bp = Blueprint("saved_searches", __name__)


def _err(msg, status, details=None):
    body = {"success": False, "error": msg}
    if details:
        body["details"] = details
    return jsonify(body), status


@bp.route("/api/saved-searches", methods=["POST"])
def create():
    body = request.get_json(silent=True) or {}
    prefs, errors = validate_preferences(body.get("preferences"))
    if errors:
        return _err("Invalid request", 400, errors)
    name = str(body.get("name") or "").strip() or f"Search for Rs.{prefs.get('budget'):,.0f}"
    doc = {"name": name[:80], "preferences": prefs, "createdAt": datetime.now(timezone.utc).isoformat()}
    doc["_id"] = get_collection().insert_one(doc).inserted_id
    return jsonify({"success": True, "message": "Search saved", "data": serialize(doc)}), 201


@bp.route("/api/saved-searches", methods=["GET"])
def list_all():
    docs = [serialize(d) for d in get_collection().find().sort("createdAt", -1).limit(50)]
    return jsonify({"success": True, "count": len(docs), "data": docs}), 200


@bp.route("/api/saved-searches/<id>", methods=["PUT"])
def rename(id):
    if not ObjectId.is_valid(id):
        return _err("Invalid saved search id", 400)
    name = str((request.get_json(silent=True) or {}).get("name") or "").strip()
    if not name:
        return _err("name is required", 400)
    doc = get_collection().find_one_and_update({"_id": ObjectId(id)}, {"$set": {"name": name[:80]}}, return_document=True)
    if not doc:
        return _err("Saved search not found", 404)
    return jsonify({"success": True, "data": serialize(doc)}), 200


@bp.route("/api/saved-searches/<id>", methods=["DELETE"])
def remove(id):
    if not ObjectId.is_valid(id):
        return _err("Invalid saved search id", 400)
    if get_collection().delete_one({"_id": ObjectId(id)}).deleted_count == 0:
        return _err("Saved search not found", 404)
    return jsonify({"success": True, "message": "Saved search deleted"}), 200

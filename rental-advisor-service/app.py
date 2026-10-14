"""Rental Advisor Service - Microservice 2 of RentWise.
It never connects to MongoDB; all apartment data comes from the Apartment Service over HTTP."""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from env_loader import load_env

load_env()

import time  # noqa: E402
from pymongo.errors import PyMongoError  # noqa: E402
from routes.recommendations import bp, error  # noqa: E402
from routes.saved_searches import bp as saved_bp  # noqa: E402
from models.saved_search import StorageNotConfigured  # noqa: E402
from services.apartment_client import ApartmentServiceError, ApartmentNotFound  # noqa: E402

app = Flask(__name__)
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
CORS(app, origins=origins)
app.register_blueprint(bp)
app.register_blueprint(saved_bp)


@app.route("/")
def health():
    return jsonify({"service": "Rental Advisor Service", "status": "running"})


@app.route("/health")
def health_check():
    """Open http://localhost:5002/health to check the link to the Apartment Service."""
    from services.apartment_client import _get
    _get("/health")
    return jsonify({"service": "Rental Advisor Service", "status": "running", "apartmentService": "reachable"})


@app.route("/api/status")
def status():
    """Used by the frontend 'System Status' page: shows the inter-service link and its latency."""
    from services.apartment_client import _get
    started, link = time.perf_counter(), {"reachable": True, "error": None}
    try:
        info = _get("/health")
        link["database"] = info.get("database")
    except (ApartmentServiceError, ApartmentNotFound) as e:
        link.update(reachable=False, error=str(e))
    link["latencyMs"] = round((time.perf_counter() - started) * 1000)
    return jsonify({"service": "Rental Advisor Service", "status": "running",
                    "apartmentService": link,
                    "savedSearchesEnabled": bool(os.getenv("MONGO_URI"))})


@app.errorhandler(StorageNotConfigured)
def no_storage(e):
    return error(str(e), 503)


@app.errorhandler(PyMongoError)
def db_error(e):
    app.logger.error("Database error: %s", e)
    return error("Advisor database unavailable.", 503)


@app.errorhandler(ApartmentServiceError)
def unavailable(e):
    return error(str(e), 503)


@app.errorhandler(ApartmentNotFound)
def missing(e):
    return error(str(e), 404)


@app.errorhandler(404)
def not_found(e):
    return error("Route not found", 404)


@app.errorhandler(405)
def bad_method(e):
    return error("Method not allowed", 405)


@app.errorhandler(Exception)
def server_error(e):
    app.logger.exception(e)
    return error("Internal server error", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5002)), debug=os.getenv("FLASK_DEBUG") == "1")

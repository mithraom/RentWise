"""Apartment Management Service - Microservice 1 of RentWise."""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from pymongo.errors import PyMongoError

from env_loader import load_env

load_env()

from models.apartment import get_collection  # noqa: E402
from routes.apartments import bp, error  # noqa: E402

app = Flask(__name__)
origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
CORS(app, origins=origins)
app.register_blueprint(bp)


@app.route("/")
def health():
    return jsonify({"service": "Apartment Management Service", "status": "running"})


@app.route("/health")
def health_check():
    """Open http://localhost:5001/health to check the database connection."""
    get_collection().database.client.admin.command("ping")
    return jsonify({"service": "Apartment Management Service", "status": "running", "database": "connected"})


@app.errorhandler(PyMongoError)
def db_error(e):
    app.logger.error("Database error: %s", e)
    return error("Database unavailable. Check MONGO_URI and make sure MongoDB is running.", 503)


@app.errorhandler(RuntimeError)
def config_error(e):
    app.logger.error("Configuration error: %s", e)
    return error(f"Server configuration error: {e}", 500)


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
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)), debug=os.getenv("FLASK_DEBUG") == "1")

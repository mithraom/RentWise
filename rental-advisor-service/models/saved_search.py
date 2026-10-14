"""Own database of the Rental Advisor Service: rentwise_advisor_db.saved_searches.
This is separate from the Apartment Service database (database-per-service pattern)."""
import os
from pymongo import MongoClient

_client = None


class StorageNotConfigured(Exception):
    """MONGO_URI is not set -> saved searches are disabled (-> HTTP 503)."""


def get_collection():
    global _client
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise StorageNotConfigured("Saved searches are disabled: set MONGO_URI for the Rental Advisor Service.")
    if _client is None:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client[os.getenv("DB_NAME", "rentwise_advisor_db")]["saved_searches"]


def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

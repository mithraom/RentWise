"""Database access for the apartments collection (rentwise_db.apartments)."""
import os
from pymongo import MongoClient

_client = None


def get_collection():
    """Create the Mongo client lazily and return the apartments collection."""
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")   # local-dev default
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client[os.getenv("DB_NAME", "rentwise_db")]["apartments"]


def serialize(doc):
    """Convert ObjectId to string so the document can be returned as JSON."""
    doc["_id"] = str(doc["_id"])
    return doc

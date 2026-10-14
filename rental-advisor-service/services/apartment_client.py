"""HTTP client used to talk to the Apartment Service.
This is the ONLY place where the Rental Advisor touches apartment data - via REST, never via MongoDB."""
import os
import requests


class ApartmentServiceError(Exception):
    """Apartment Service unreachable or returned a server error (-> HTTP 503)."""


class ApartmentNotFound(Exception):
    """Apartment Service answered 404 (-> HTTP 404)."""


def _get(path, params=None):
    base = os.getenv("APARTMENT_SERVICE_URL", "http://localhost:5001")   # local-dev default
    timeout = float(os.getenv("REQUEST_TIMEOUT", 25))
    try:
        resp = requests.get(base.rstrip("/") + path, params=params, timeout=timeout)
    except requests.exceptions.RequestException:
        raise ApartmentServiceError("Apartment Service is unavailable. Please try again later.")
    if resp.status_code == 404:
        raise ApartmentNotFound("Apartment not found")
    if resp.status_code == 400:
        raise ApartmentNotFound("Invalid apartment id")
    if resp.status_code >= 500:
        try:
            detail = resp.json().get("error", "")
        except ValueError:
            detail = ""
        raise ApartmentServiceError(f"Apartment Service returned an error. {detail}".strip())
    return resp.json()


def fetch_all_apartments(params=None):
    return _get("/api/apartments", params)["data"]


def fetch_apartment(apartment_id):
    return _get(f"/api/apartments/{apartment_id}")["data"]

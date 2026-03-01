from __future__ import annotations

from typing import Any

import requests

BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"
REQUEST_TIMEOUT_SECONDS = 10


class VpicServiceError(Exception):
    pass


def _get(url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise VpicServiceError("Could not fetch data from vPIC API") from exc


def decode_vin(vin: str) -> list[dict[str, Any]]:
    url = f"{BASE_URL}/DecodeVinValues/{vin}"
    data = _get(url, params={"format": "json"})
    return data.get("Results", [])


def get_all_makes() -> list[dict[str, Any]]:
    url = f"{BASE_URL}/GetAllMakes"
    data = _get(url, params={"format": "json"})
    return data.get("Results", [])


def get_models_for_make_year(make: str, year: int) -> list[dict[str, Any]]:
    url = f"{BASE_URL}/GetModelsForMakeYear/make/{make}/modelyear/{year}"
    data = _get(url, params={"format": "json"})
    return data.get("Results", [])

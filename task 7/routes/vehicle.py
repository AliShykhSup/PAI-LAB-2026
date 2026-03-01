from __future__ import annotations

from flask import Blueprint, jsonify, request

from services.vpic_service import (
    VpicServiceError,
    decode_vin,
    get_all_makes,
    get_models_for_make_year,
)

vehicle_bp = Blueprint("vehicle", __name__)


@vehicle_bp.get("/vin/<vin>")
def vin_lookup(vin: str):
    vin = vin.strip().upper()

    if len(vin) != 17:
        return jsonify({"error": "VIN must be exactly 17 characters"}), 400

    try:
        result = decode_vin(vin)
        if not result:
            return jsonify({"error": "No vehicle information found"}), 404

        record = result[0]
        vehicle_info = {
            "vin": record.get("VIN"),
            "make": record.get("Make"),
            "model": record.get("Model"),
            "model_year": record.get("ModelYear"),
            "body_class": record.get("BodyClass"),
            "vehicle_type": record.get("VehicleType"),
            "engine_cylinders": record.get("EngineCylinders"),
            "fuel_type_primary": record.get("FuelTypePrimary"),
            "plant_country": record.get("PlantCountry"),
            "manufacturer": record.get("Manufacturer"),
        }
        return jsonify({"data": vehicle_info})
    except VpicServiceError as exc:
        return jsonify({"error": str(exc)}), 502


@vehicle_bp.get("/makes")
def list_makes():
    try:
        makes = get_all_makes()
        return jsonify({"count": len(makes), "data": makes})
    except VpicServiceError as exc:
        return jsonify({"error": str(exc)}), 502


@vehicle_bp.get("/models")
def list_models_for_make_year():
    make = request.args.get("make", "").strip()
    year = request.args.get("year", "").strip()

    if not make:
        return jsonify({"error": "Query parameter 'make' is required"}), 400

    if not year.isdigit():
        return jsonify({"error": "Query parameter 'year' must be a valid number"}), 400

    year_number = int(year)
    if year_number < 1886:
        return jsonify({"error": "Year must be 1886 or later"}), 400

    try:
        models = get_models_for_make_year(make=make, year=year_number)
        return jsonify({"count": len(models), "data": models})
    except VpicServiceError as exc:
        return jsonify({"error": str(exc)}), 502

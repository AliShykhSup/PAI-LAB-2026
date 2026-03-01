import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from routes.vehicle import vehicle_bp

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(vehicle_bp, url_prefix="/api/vehicle")

    app.config["JSON_SORT_KEYS"] = False

    if _env_bool("TRUST_PROXY", default=True):
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    @app.get("/")
    def root():
        return jsonify(
            {
                "message": "Vehicle Info API is running",
                "endpoints": {
                    "decode_vin": "/api/vehicle/vin/<vin>",
                    "models_for_make_and_year": "/api/vehicle/models?make=toyota&year=2020",
                    "makes": "/api/vehicle/makes",
                },
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    app = create_app()
    debug_mode = _env_bool("FLASK_DEBUG", default=False)
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = _env_int("FLASK_PORT", 5000)
    app.run(host=host, port=port, debug=debug_mode)

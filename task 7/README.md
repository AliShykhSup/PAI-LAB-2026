# Vehicle Info App (Flask Backend)

A Flask-based backend that provides vehicle information using the free **NHTSA vPIC API**.

## Features

- Decode vehicle details from VIN
- List all vehicle makes
- List models by make and model year
- Health check endpoint

## Tech Stack

- Flask
- Requests
- NHTSA vPIC API (free, no API key required)

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

App runs at: `http://127.0.0.1:5000`

## Environment Variables

- `FLASK_HOST` (default: `0.0.0.0`)
- `FLASK_PORT` (default: `5000`)
- `FLASK_DEBUG` (default: `false`)
- `TRUST_PROXY` (default: `true`)

Example (PowerShell):

```powershell
$env:FLASK_HOST="0.0.0.0"
$env:FLASK_PORT="5000"
$env:FLASK_DEBUG="false"
```

## Deployment (Production)

Use `wsgi:app` as the deployment entrypoint with your host/platform WSGI runner.

The app is production-safe by code defaults:

Notes:

- Debug is off unless `FLASK_DEBUG=true`.
- Host/port are environment-driven.
- Proxy headers are handled via `ProxyFix`.
- Put this service behind a reverse proxy (TLS, routing, and rate limiting).

## API Endpoints

### 1) Root

- `GET /`
- Returns service message and endpoint map.

### 2) Health Check

- `GET /health`

### 3) VIN Decode

- `GET /api/vehicle/vin/<vin>`
- Example:

```http
GET /api/vehicle/vin/1HGCM82633A004352
```

### 4) All Makes

- `GET /api/vehicle/makes`

### 5) Models by Make + Year

- `GET /api/vehicle/models?make=toyota&year=2020`

## Notes

- VIN must be exactly 17 characters.
- Year must be a valid number and 1886 or later.
- External API failures return `502`.

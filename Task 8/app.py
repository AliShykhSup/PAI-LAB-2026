from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass
from pathlib import Path

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)


def load_local_env() -> None:
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_local_env()


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    open_price: float | None
    high: float | None
    low: float | None
    volume: int | None
    source: str


def quote_to_text(quote: Quote) -> str:
    parts = [f"Symbol: {quote.symbol}", f"Price: {quote.price}"]
    if quote.open_price is not None:
        parts.append(f"Open: {quote.open_price}")
    if quote.high is not None:
        parts.append(f"High: {quote.high}")
    if quote.low is not None:
        parts.append(f"Low: {quote.low}")
    if quote.volume is not None:
        parts.append(f"Volume: {quote.volume}")
    return ", ".join(parts)


def fetch_stock_quote(symbol: str) -> Quote:
    normalized = symbol.strip().lower()
    if not normalized:
        raise ValueError("Please enter a stock symbol.")

    url = f"https://stooq.com/q/l/?s={normalized}&i=d"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    reader = csv.DictReader(io.StringIO(response.text))
    row = next(reader, None)
    if not row or row.get("Close", "") in {"", "N/A"}:
        raise ValueError(f"No quote found for '{symbol.upper()}'.")

    return Quote(
        symbol=row.get("Symbol", symbol).upper(),
        price=float(row["Close"]),
        open_price=float(row["Open"]) if row.get("Open") not in {"", "N/A"} else None,
        high=float(row["High"]) if row.get("High") not in {"", "N/A"} else None,
        low=float(row["Low"]) if row.get("Low") not in {"", "N/A"} else None,
        volume=int(float(row["Volume"])) if row.get("Volume") not in {"", "N/A"} else None,
        source="Stooq",
    )


def fetch_gemini_insight(quote: Quote) -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "Set GEMINI_API_KEY in .env to enable AI insights."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Give one short, student-friendly sentence about this stock quote. "
                            "Do not add a disclaimer. Keep it under 25 words. "
                            f"{quote_to_text(quote)}"
                        )
                    }
                ]
            }
        ],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 60},
    }

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return "No AI insight was returned."

    parts = candidates[0].get("content", {}).get("parts", [])
    text = " ".join(part.get("text", "") for part in parts).strip()
    return text or "No AI insight was returned."


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/quote")
def api_quote():
    symbol = request.args.get("symbol", "").strip()
    try:
        quote = fetch_stock_quote(symbol)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except requests.RequestException:
        return jsonify({"error": "Unable to reach the stock data service right now."}), 502

    return jsonify(
        {
            "symbol": quote.symbol,
            "price": quote.price,
            "open": quote.open_price,
            "high": quote.high,
            "low": quote.low,
            "volume": quote.volume,
            "source": quote.source,
        }
    )


@app.route("/api/stock-story")
def api_stock_story():
    symbol = request.args.get("symbol", "").strip()
    try:
        quote = fetch_stock_quote(symbol)
        insight = fetch_gemini_insight(quote)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except requests.RequestException:
        return jsonify({"error": "Unable to reach a remote service right now."}), 502

    return jsonify({"symbol": quote.symbol, "story": insight})


if __name__ == "__main__":
    app.run(debug=True)
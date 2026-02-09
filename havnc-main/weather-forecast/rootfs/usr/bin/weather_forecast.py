#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

OPTIONS_PATH = "/data/options.json"
DEFAULT_MUNICIPALITY = "Barcelona"
DEFAULT_BASE_URL = "https://api.meteo.cat/recursos/v1"
PORT = 8099


class ForecastError(Exception):
    pass


def load_options():
    options = {}
    if os.path.exists(OPTIONS_PATH):
        with open(OPTIONS_PATH, "r", encoding="utf-8") as handle:
            options = json.load(handle)
    municipality = options.get("municipality") or DEFAULT_MUNICIPALITY
    municipality_code = options.get("municipality_code")
    api_key = options.get("api_key")
    base_url = options.get("base_url") or DEFAULT_BASE_URL
    return municipality, municipality_code, api_key, base_url


def fetch_json(url, api_key):
    request = urllib.request.Request(url)
    request.add_header("X-API-Key", api_key)
    request.add_header("Accept", "application/json")
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_municipalities(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get("municipis") or data.get("municipalities") or data.get("results") or []
    return []


def resolve_municipality_code(municipality, base_url, api_key):
    url = f"{base_url}/municipis"
    data = fetch_json(url, api_key)
    municipalities = extract_municipalities(data)
    if not municipalities:
        raise ForecastError("No municipality data returned from Meteocat.")
    municipality_lower = municipality.strip().lower()
    for entry in municipalities:
        name = str(entry.get("nom", "")).strip().lower()
        if name == municipality_lower:
            return entry.get("codi")
    raise ForecastError(f"No municipality code found for '{municipality}'.")


def fetch_forecast(municipality_code, base_url, api_key):
    url = f"{base_url}/prediccio/municipi/{urllib.parse.quote(str(municipality_code))}"
    return fetch_json(url, api_key)


def build_payload():
    municipality, municipality_code, api_key, base_url = load_options()
    if not api_key:
        raise ForecastError("Missing Meteocat API key (api_key).")
    if not municipality_code:
        municipality_code = resolve_municipality_code(municipality, base_url, api_key)

    forecast = fetch_forecast(municipality_code, base_url, api_key)

    return {
        "municipality": {
            "name": municipality,
            "code": municipality_code,
        },
        "forecast": forecast,
    }


class ForecastHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/health"):
            self._send_json(200, {"status": "ok"})
            return
        if self.path != "/forecast":
            self._send_json(404, {"error": "Not found"})
            return
        try:
            payload = build_payload()
        except ForecastError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except Exception as exc:  # noqa: BLE001
            self._send_json(500, {"error": f"Unexpected error: {exc}"})
            return
        self._send_json(200, payload)

    def log_message(self, format, *args):
        return

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = HTTPServer(("0.0.0.0", PORT), ForecastHandler)
    print(f"Weather Forecast add-on listening on port {PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Dashboard server: serves the web UI and live health data.

Usage: python3 server.py [port] [config.json]
Then open http://127.0.0.1:8000
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from monitor import check

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config" / "endpoints.json"


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            page = (ROOT / "web" / "index.html").read_bytes()
            self._send(200, page, "text/html; charset=utf-8")
        elif self.path == "/api/status":
            endpoints = json.loads(CONFIG.read_text())["endpoints"]
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(check, endpoints))
            payload = {
                "checked_at": datetime.now(timezone.utc).isoformat(),
                "results": results,
            }
            self._send(200, json.dumps(payload).encode(), "application/json")
        else:
            self._send(404, b"Not found", "text/plain")


def main():
    global CONFIG
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    if len(sys.argv) > 2:
        CONFIG = Path(sys.argv[2]).resolve()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Dashboard running at http://127.0.0.1:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

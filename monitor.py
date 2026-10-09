#!/usr/bin/env python3
"""Service Health Monitor: checks endpoints and writes a status report.

Usage: python3 monitor.py [config.json]
Exit code is 1 if any endpoint is DOWN, so CI pipelines can fail on it.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def classify(status, ms, expected=200, slow_ms=1000):
    """Return UP, SLOW or DOWN for a response."""
    if status != expected:
        return "DOWN"
    if ms > slow_ms:
        return "SLOW"
    return "UP"


def check(endpoint, timeout=5):
    """Check one endpoint and return a result dictionary."""
    name, url = endpoint["name"], endpoint["url"]
    expected = endpoint.get("expected_status", 200)
    slow_ms = endpoint.get("slow_ms", 1000)
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            status = resp.status
    except urllib.error.HTTPError as err:
        status = err.code
    except Exception as err:
        return {"name": name, "url": url, "state": "DOWN",
                "status": None, "ms": None, "error": str(err)}
    ms = round((time.time() - start) * 1000)
    return {"name": name, "url": url, "status": status, "ms": ms,
            "state": classify(status, ms, expected, slow_ms), "error": None}


def write_report(results, path="reports/latest.md"):
    """Write a Markdown status report."""
    Path(path).parent.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Service Health Report - {now}", "",
             "| Service | State | HTTP | Time (ms) | Notes |",
             "|---------|-------|------|-----------|-------|"]
    for r in results:
        lines.append(f"| {r['name']} | {r['state']} | {r['status'] or '-'} "
                     f"| {r['ms'] or '-'} | {r['error'] or ''} |")
    down = [r["name"] for r in results if r["state"] == "DOWN"]
    lines += ["", f"**Incidents:** {', '.join(down) if down else 'none'}"]
    Path(path).write_text("\n".join(lines) + "\n")


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/endpoints.json"
    endpoints = json.loads(Path(config_path).read_text())["endpoints"]
    results = [check(e) for e in endpoints]
    for r in results:
        print(f"[{r['state']:<4}] {r['name']:<14} "
              f"HTTP {r['status'] or '-'}  {r['ms'] or '-'} ms")
    write_report(results)
    return 1 if any(r["state"] == "DOWN" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())

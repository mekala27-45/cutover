"""Read-only source/account probes with bounded timeouts and redacted failures."""

import json
import os
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

URLS = {
    "nhtsa_layout": "https://static.nhtsa.gov/odi/ffdd/cmpl/CMPL.txt",
    "nhtsa_listing": "https://static.nhtsa.gov/odi/ffdd/cmpl/",
    "edgar_names": "https://www.sec.gov/files/company_tickers.json",
}


def run():
    rows = {}
    for name, url in URLS.items():
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Cutover-portfolio/0.1 (https://github.com/mekala27-45/cutover)"
                },
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                payload = response.read(5_000_001)
                rows[name] = {
                    "status": "reachable",
                    "http_status": response.status,
                    "bytes_read": len(payload),
                    "url": url,
                }
        except Exception as exc:
            rows[name] = {"status": "unavailable", "error_type": type(exc).__name__, "url": url}
    rows["kaggle"] = {
        "status": "credentials_present_not_execution"
        if os.getenv("KAGGLE_USERNAME")
        and (os.getenv("KAGGLE_KEY") or os.getenv("KAGGLE_API_TOKEN"))
        else "not_configured"
    }
    rows["database"] = {
        "status": "configured_not_verified" if os.getenv("DATABASE_URL") else "not_configured"
    }
    out = {"checked_at": datetime.now(UTC).isoformat(), "probes": rows}
    Path("results").mkdir(exist_ok=True)
    Path("results/probe.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    run()

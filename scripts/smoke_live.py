"""Authored examples only. A receipt is checked separately through the DB connector."""

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = os.getenv("CUTOVER_API_BASE", "https://cutover-api.vercel.app")
EXPECTED = os.getenv("CUTOVER_EXPECTED_COMMIT", os.environ["GITHUB_SHA"])


def request(path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            status, body = response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        status, body = exc.code, json.load(exc)
    return {"status": status, "body": body, "elapsed_ms": (time.perf_counter() - started) * 1000}


def run() -> None:
    output = {"mode": "actual_live_guard_only_smoke", "checks": {}, "quality_claim": False}
    checks = output["checks"]
    try:
        for _ in range(12):
            checks["health"] = request("/health")
            if checks["health"]["body"].get("source_commit") == EXPECTED:
                break
            time.sleep(5)
        assert checks["health"]["status"] == 200
        assert checks["health"]["body"]["source_commit"] == EXPECTED
        assert checks["health"]["body"]["model_ready"] is False
        checks["release"] = request("/v1/release")
        assert checks["release"]["status"] == 200
        for name, text in [
            ("ordinary", "Authored verification: the dashboard clock loses its saved time."),
            ("safety", "Authored verification: smoke and fire appeared beside the engine."),
        ]:
            checks[name] = request("/v1/triage", {"narrative": text})
            assert checks[name]["status"] == 200
            body = checks[name]["body"]
            assert body["receipt_id"] and body["text_digest"]
            assert body["decision"]["action"] == "send_to_analyst"
            assert body["mode"] == "guard_only"
            assert text not in json.dumps(body)
        checks["invalid"] = request("/v1/triage", {"narrative": "short"})
        assert checks["invalid"]["status"] == 422
        assert "short" not in json.dumps(checks["invalid"]["body"])
        checks["criteria"] = request("/v1/criteria")
        assert checks["criteria"]["status"] == 200
        output["status"] = "passed"
    except Exception as exc:
        output.update(status="failed", failure_type=type(exc).__name__)
        raise
    finally:
        Path("recovered").mkdir(exist_ok=True)
        Path("recovered/live-smoke.json").write_text(json.dumps(output, indent=2) + "\n")
        print("CUTOVER_EVIDENCE live-smoke.json " + json.dumps(output, separators=(",", ":")))


if __name__ == "__main__":
    run()

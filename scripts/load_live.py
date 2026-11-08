"""Bounded open-loop load against the guard-only API; never model latency evidence."""

import concurrent.futures
import json
import math
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://cutover-api.vercel.app"
COUNT = 24
PERIOD_SECONDS = 2.0


def attempt(index: int, intended: float) -> dict:
    payload = json.dumps({
        "narrative": f"Authored load verification {index}: the dashboard clock loses saved time."
    }).encode()
    request = urllib.request.Request(
        BASE + "/v1/triage", data=payload, headers={"Content-Type": "application/json"}
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status, body = response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        status, body = exc.code, {}
    except Exception:
        status, body = 0, {}
    finished = time.perf_counter()
    return {
        "index": index, "status": status,
        "latency_from_intended_ms": (finished - intended) * 1000,
        "dispatch_delay_ms": (started - intended) * 1000,
        "receipt_id": body.get("receipt_id"),
        "text_digest": body.get("text_digest"),
        "action": body.get("decision", {}).get("action"),
        "mode": body.get("mode"),
    }


def run() -> None:
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = []
        for index in range(COUNT):
            intended = started + index * PERIOD_SECONDS
            time.sleep(max(0, intended - time.perf_counter()))
            futures.append(pool.submit(attempt, index, intended))
        rows = [f.result() for f in futures]
    times = sorted(r["latency_from_intended_ms"] for r in rows)
    result = {
        "mode": "actual_guard_only_open_loop_load",
        "requests": COUNT, "rate_per_second": 1 / PERIOD_SECONDS,
        "successful": sum(r["status"] == 200 for r in rows),
        "p50_ms": times[math.ceil(COUNT * .50) - 1],
        "p95_ms": times[math.ceil(COUNT * .95) - 1],
        "cold_start_ms": None,
        "cold_start_note": "A fresh cold container was not forced or independently observed.",
        "criterion_C5": "not_shown",
        "limitation": "Guard-only service; no INT8 encoder is serving.",
        "rows": rows,
    }
    Path("recovered").mkdir(exist_ok=True)
    Path("recovered/live-load.json").write_text(json.dumps(result, indent=2) + "\n")
    print("CUTOVER_EVIDENCE live-load.json " + json.dumps(result, separators=(",", ":")))
    if any(r["status"] != 200 or r["action"] != "send_to_analyst" for r in rows):
        raise SystemExit("guard_only_load_failed")


if __name__ == "__main__":
    run()

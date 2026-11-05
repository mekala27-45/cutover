"""Bounded API; no endpoint can change a release or close a complaint."""
from __future__ import annotations
import json
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from packages.core import Feature, STATEMENT, digest
from packages.api.store import BudgetExceeded, StorageUnavailable, triage, release_state

ROOT=Path(__file__).resolve().parent
app=FastAPI(title="Cutover",version="0.1.0",docs_url="/docs")
app.add_middleware(CORSMiddleware,allow_origins=["https://mekala27-45.github.io"],
                   allow_methods=["GET","POST"],allow_headers=["Content-Type"])

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    # FastAPI's default error includes the rejected input; do not echo complaint text.
    return JSONResponse(status_code=422,content={"error":"invalid_request",
                        "fields":[list(e["loc"]) for e in exc.errors()],"statement":STATEMENT})

@app.middleware("http")
async def body_limit(request: Request, call_next):
    length=request.headers.get("content-length")
    if length and (not length.isdigit() or int(length)>20000):
        return JSONResponse(status_code=413,content={"error":"body_too_large"})
    if request.method=="POST":
        body=await request.body()
        if len(body)>20000: return JSONResponse(status_code=413,content={"error":"body_too_large"})
    return await call_next(request)

@app.get("/health")
def health():
    return {"status":"guard_only","model_ready":False,
            "source_commit":os.getenv("VERCEL_GIT_COMMIT_SHA","local"),
            "registration_digest":digest(json.loads((ROOT/"evaluation/registration.json").read_text())),
            "statement":STATEMENT}

@app.post("/v1/triage")
def triage_route(feature: Feature, request: Request):
    try:
        result=triage(feature,request.client.host if request.client else "unknown")
        return result|{"statement":STATEMENT}
    except BudgetExceeded:
        raise HTTPException(429,detail="hourly_client_budget_exhausted",headers={"Retry-After":"3600"})
    except StorageUnavailable:
        raise HTTPException(503,detail="durable_storage_unavailable")

@app.get("/v1/release")
def releases():
    try: return release_state()|{"statement":STATEMENT}
    except StorageUnavailable: raise HTTPException(503,detail="release_state_unavailable")

@app.get("/v1/criteria")
def criteria():
    path=ROOT/"results/manifest.json"
    if not path.exists(): raise HTTPException(503,detail="evidence_manifest_unavailable")
    return {"criteria":json.loads(path.read_text())["criteria"],"statement":STATEMENT}

@app.get("/v1/shadow")
def shadow():
    path=ROOT/"results/shadow.json"
    if not path.exists():
        return {"status":"not_run","rows":[],"reason":"No promoted shadow evaluation.",
                "statement":STATEMENT}
    return json.loads(path.read_text())|{"statement":STATEMENT}

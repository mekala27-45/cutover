# Cutover operations

This is an incomplete portfolio system. The API currently reports guard-only and every successful response must send the complaint to an analyst. There is no promoted trained model.

## Current service boundary

The web application is hosted at https://mekala27-45.github.io/cutover/ and the API health endpoint at https://cutover-api.vercel.app/health. A healthy process is not evidence of a working database or a trained model. Check the release endpoint and a receipt from an authored test narrative separately.

## Deployment prerequisites

The dedicated database schema is installed. The runtime role can read release state, insert triage receipts and consume request budgets. It cannot change release state. DATABASE_URL and CUTOVER_SALT must be entered as encrypted production and preview environment variables for the dedicated Cutover Vercel project after the user explicitly approves that credential transfer. Neither value belongs in a repository, command log or document.

The Vercel free deployment quota was exhausted on 2026-11-05. Wait for its reset before attempting the prepared deployment. Do not upgrade a plan or bypass the quota. The deployment currently serving health is older than main.

## Failure behavior

A failed receipt insert must roll back the request and return HTTP 503. Never turn persistence failure into a successful triage. The request budget returns HTTP 429 after its allowed hourly count. An unavailable model sends the case to an analyst.

## Release and rollback

Release mutation is intentionally absent from the API. The repository has an Actions-only operator script, but its restricted writer secret and workflow are not yet commissioned. Before enabling a trained release, complete all criteria, real model comparisons, independent persistence checks and actual bad-release drills. Preserve the prior artifact by digest and verify byte equality after rollback.

## Reproduction

Install Python 3.12 dependencies, check registration, run tests and source gates. The committed data request starts the actual NHTSA workflow. Its downloads use the official archive names pinned in config/source-catalog.json. Data products in private/ never enter public artifacts. Only aggregate allowlisted output is exported.

# Cutover

Cutover is in development. Mandatory data, model, evaluation, deployment, rollout, and handover evidence is not yet complete. The project routes vehicle complaints to a component team or to a person, with no action that closes a case.

The original specification is in [docs/SPEC.md](docs/SPEC.md). Criteria and the evaluation plan are registered before scoring. Actual NHTSA results, recorded model inference and synthetic software tests remain separate.

## Run

Use Python 3.12. Install with `pip install -e '.[dev]'`, then run `python scripts/register.py --check`, `pytest`, and `python scripts/check_gates.py`.

The actual source and floor run is requested through the data workflow. It downloads public sources, drops personal fields before writing, constructs temporal splits, selects registered samples and trains the TF-IDF floor. It does not claim encoder or language model results.

cutover is a portfolio demonstration. Its customer is fictional, and public NHTSA vehicle complaints stand in for that customer inbox. It is not affiliated with NHTSA or any vehicle maker, it makes no safety determination, and it is not for safety, legal or regulatory use. It never closes a complaint: it routes one to a team or sends it to a person. Its costs are shadow prices from public list prices.

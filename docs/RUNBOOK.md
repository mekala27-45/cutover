# Cutover operations

The live service is guard-only. Every successful response sends the complaint to an analyst. A trained model has not been promoted.

## Live endpoints and verified boundary

The site is https://mekala27-45.github.io/cutover/ and the API is https://cutover-api.vercel.app. Check /health, /v1/release, /v1/criteria and /v1/shadow separately from POST /v1/triage. Use authored test text only.

The pooled Neon connection is working. public_results/live-smoke.json records the successful immutable-deployment check; independent-receipts.json contains receipts read through a separate database connection. live-load.json and independent-load-receipts.json record the bounded production load and independent reads. Those measurements apply to the guard-only service; cold-start model latency is unmeasured.

## Database rules

DATABASE_URL and CUTOVER_SALT are encrypted production/preview variables in the dedicated Cutover Vercel project. Neither value belongs in files or logs. The runtime role reads release state, inserts receipts and updates request budgets. It cannot write release state or switch history.

The pooler rejects the startup options parameter. connect() opens the connection and runs SET LOCAL statement_timeout inside its transaction. A failed receipt insert rolls back the request and budget increment and returns unavailable. Exceptions emit only a fixed failure category, type and SQLSTATE, never connection strings or narrative contents.

## Release holds

Release mutation is absent from the API. The Actions-only operator script exists, but the restricted writer secret and manual workflow have not been commissioned. The live switch drill remains unrun. Do not substitute direct owner SQL mutations for the required workflow evidence.

Before model promotion, obtain actual encoder and language-model evaluation, parity, private artifact provenance, the full criteria bill and planted-release drill. scripts/verify_release.py rejects the current incomplete manifest. Do not create a completion tag.

## Reproduction

Install Python 3.12 dependencies. Run registration checks, pytest with coverage, Ruff, strict mypy and the notebooks through nbmake. scripts/derive_baseline.py deterministically rebuilds the baseline report and both manifest copies from the frozen aggregate evidence. Never relabel that floor evidence as an encoder or cascade result.

The data workflow drops disallowed fields before disk writes. Only aggregate output leaves its runner. Private fitted weights and per-case records from the completed baseline run were discarded. New paired comparisons require a fresh run and an approved private artifact destination.

## Remaining access

Kaggle runtime and ModernBERT compatibility were observed previously. Qwen probe outputs could not be recovered after browser interruption. No browser-control tool is currently exposed in this work session, and local shell networking cannot resolve remote hosts. Continue connected-service work through the available integrations; do not invent missing GPU results or bypass authentication.

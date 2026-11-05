# Working on Cutover

Read docs/SPEC.md and DECISIONS.md before changing behavior. Set up Python 3.12 with pip install -e '.[dev]'. Run pytest and python scripts/check_gates.py. Build the web app with npm install and npm run build from web.

Treat config/criteria.yaml, config/plan.json and evaluation/registration.json as frozen. Change them only through a dated change request showing old and new values and preserving earlier verdicts. Never alter a promoted result, source lock or sealed test to improve a score.

Keep complaint narratives and personal source fields out of logs, public artifacts and commits. The public result exporter has an explicit aggregate allowlist. Never expand it without reviewing the publication boundary. Never fetch credentials into a file or display them.

Models receive Feature records only. They cannot see Label records. Every output is validated. Actions are route or send_to_analyst. Safety guards precede routing and the API never calls the recorded incumbent. Only the workflow writer can mutate release state.

Actual model execution, recorded inference, deterministic results and synthetic tests are separate evidence modes. Missing runs remain not shown. Do not create a release tag while a mandatory item lacks evidence.

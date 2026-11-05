# Cutover

Cutover is in development. Mandatory data, model, evaluation, deployment, rollout, and handover evidence is not yet complete. The project routes vehicle complaints to a component team or to a person, with no action that closes a case.

The original specification is in [docs/SPEC.md](docs/SPEC.md). Criteria and the evaluation plan are registered before scoring. Actual NHTSA results, recorded model inference and synthetic software tests remain separate.

## Run

Use Python 3.12. Install with `pip install -e '.[dev]'`, then run `python scripts/register.py --check`, `pytest`, and `python scripts/check_gates.py`.

The actual source and floor run is requested through the data workflow. It downloads public sources, drops personal fields before writing, constructs temporal splits, selects registered samples and trains the TF-IDF floor. It does not claim encoder or language model results.

cutover is a portfolio demonstration. Its customer is fictional, and public NHTSA vehicle complaints stand in for that customer inbox. It is not affiliated with NHTSA or any vehicle maker, it makes no safety determination, and it is not for safety, legal or regulatory use. It never closes a complaint: it routes one to a team or sends it to a person. Its costs are shadow prices from public list prices.

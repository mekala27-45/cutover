# Cutover

Cutover is in development. Mandatory data, model, evaluation, deployment, rollout, and handover evidence is not yet complete. The project routes vehicle complaints to a component team or to a person, with no action that closes a case.

The original specification is in [docs/SPEC.md](docs/SPEC.md). Criteria and the evaluation plan are registered before scoring. Actual NHTSA results, recorded model inference and synthetic software tests remain separate.

## Live surfaces

[Evidence dashboard](https://mekala27-45.github.io/cutover/) · [API health](https://cutover-api.vercel.app/health) · [Full completion checklist](RESULTS.md)

## Implementation map

| Capability | Implementation | Evidence state |
| --- | --- | --- |
| Strict decision contracts | packages/core | Behavioral tests passing |
| Privacy boundary and temporal intake | packages/intake | Actual intake still running |
| TF-IDF training and calibration | packages/floor | Synthetic fit and round-trip tested |
| Model output validation | packages/llm | Parser tested; model runs absent |
| Safety and escalation | packages/cascade | Property tests passing; real thresholds pending |
| Independent scoring and shadow prices | packages/evaluation | Tested mechanics; actual comparisons pending |
| Rollback and monitoring | packages/release | Synthetic tests; real drill pending |
| Transactional receipts | packages/api | Transaction tests; live credentials pending |
| Evidence sheet | web | Published and checked in a real browser |

## Run

Use Python 3.12. Install with `pip install -e '.[dev]'`, then run `python scripts/register.py --check`, `pytest`, and `python scripts/check_gates.py`.

The actual source and floor run is requested through the data workflow. It downloads public sources, drops personal fields before writing, constructs temporal splits, selects registered samples and trains the TF-IDF floor. It does not claim encoder or language model results.

cutover is a portfolio demonstration. Its customer is fictional, and public NHTSA vehicle complaints stand in for that customer inbox. It is not affiliated with NHTSA or any vehicle maker, it makes no safety determination, and it is not for safety, legal or regulatory use. It never closes a complaint: it routes one to a team or sends it to a person. Its costs are shadow prices from public list prices.

# Cutover build status

The end-to-end release is incomplete. The site and guard-only API are deployed. Mandatory actual model, evaluation and release evidence is still missing. No v0.1.0 completion tag has been created.

## Verified software behavior

The quality run at https://github.com/mekala27-45/cutover/actions/runs/42115683233 passed the contract tests, enforced coverage threshold, Ruff and strict typing. See public_results/service-probe.json for recorded check values and provenance. Synthetic software tests are separate from actual model evaluations.

The real-browser check covered every route, source disclosure, example buttons, light/dark themes and a mobile viewport. The live try form returned unavailable and did not claim a receipt. The independent database query confirmed that the runtime role cannot mutate release state.

## Definition of done

| Line | Status | Requirement | Evidence |
| --- | --- | --- | --- |
| 1 | not done | NHTSA intake | The current data workflow is still running; complete source digests, post-dedup split counts and registered sample evidence are not yet promoted. |
| 2 | not done | Discovery and label noise | The discovery collector exists, but a completed manifest-backed discovery memo and label-noise analysis are missing. |
| 3 | done | Registration before scoring | evaluation/registration.json locks criteria and plan before real held-out scoring; scripts/register.py --check passes. |
| 4 | not done | Floor, encoder, ONNX and INT8 | The floor passes synthetic training and serialization tests; real floor results, encoder training and parity evidence remain missing. |
| 5 | not done | Recorded language models | The strict parser is tested; neither registered language-model inference run has completed. |
| 6 | not done | Calibrated cascade | The safety guard and no-close property tests pass; real development operating points and interior comparisons remain pending. |
| 7 | not done | Every-arm evaluation | Independent grading, bootstrap and BH code exist; qualifying held-out results for all arms are absent. |
| 8 | done | C1 through C7 verdicts | public_results/manifest.json and the live criteria page explicitly show every criterion as not_shown with its missing-evidence reason. |
| 9 | not done | Durable live API | The Vercel health endpoint returns guard_only; the database environment transfer and independent successful receipt verification remain pending. |
| 10 | not done | 2026 shadow replay | No actual shadow model replay has been promoted. |
| 11 | not done | Bad-release and rollback drill | Synthetic monitor and digest-rollback tests pass; the required real planted-release drill has not run. |
| 12 | not done | Cost and ROI | Pinned MLSpend price rows and tested arithmetic exist; measured compute, every-arm trade-offs and ROI remain missing. |
| 13 | not done | Independent persistence and live load | Database grants were independently queried; end-to-end receipt, load and live switch checks remain pending. |
| 14 | not done | Handover pack | The operations runbook and source/model status are written; validated cards, reports and analyst workbook are incomplete. |
| 15 | not done | Recomputed promoted manifest | The current absence-of-evidence manifest is digested; promoted model runs and complete deterministic rederivation are missing. |
| 16 | not done | Live Pages and try flow | All thirteen routes, source disclosure, themes and mobile layout were checked; the successful live triage state remains blocked. |
| 17 | not done | Documentation and investigation records | README, decisions, architecture, repository skills and ADRs exist; the required completed investigation notebooks are absent. |
| 18 | not done | Release quality and tag | Coverage, Ruff and strict typing pass for the current implementation; palette validation, rederivation, full provenance and the completion tag remain pending. |

## Limitations and blocking dependencies

The scoped database connection and secret salt have not been added to Vercel because automatic approval review requires explicit authorization for that destination. Vercel also rejected the latest deployment because the free daily deployment allowance was exhausted. The serving commit is recorded separately from main.

Kaggle is signed in and displayed free T4 eligibility, but the notebook editor remained loading after a reload with Start session disabled. No GPU model probe, training or inference was started. No encoder or language-model performance, savings, latency SLO or rollout success is established.

The full data run was restarted after replacing a potentially expensive duplicate-candidate ordering. The archive downloads, their digests and pre-deduplication counts are now observed in data/complaints.lock.json. Post-deduplication counts and model results remain unavailable. There are no actual injection counts, slice gaps, label-noise estimates, interior-test results or planted-release trips to report yet.

Stretch work is not done and is not counted toward the mandatory checklist.

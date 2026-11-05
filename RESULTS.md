# Cutover build status

The end-to-end release is incomplete. The site and guard-only API are deployed. Mandatory actual model, evaluation and release evidence is still missing. No v0.1.0 completion tag has been created.

## Verified software behavior

The quality run at https://github.com/mekala27-45/cutover/actions/runs/42118328917 passed 66 tests with 83.19% package statement coverage, Ruff and strict typing. See public_results/service-probe.json for recorded check values and provenance. Synthetic software tests are separate from actual model evaluations.

The real-browser check covered every route, source disclosure, example buttons, light/dark themes and a mobile viewport. The live try form returned unavailable and did not claim a receipt. The independent database query confirmed that the runtime role cannot mutate release state.

## Definition of done

| Line | Status | Requirement | Evidence |
| --- | --- | --- | --- |
| 1 | not done | NHTSA intake | Intake completed: 618,446 accepted component rows, 429,716 grouped complaints and 6,691 duplicates removed. public_results/intake-progress.json records observed split counts; complete aggregate and registered sample evidence still need verification. |
| 2 | not done | Discovery and label noise | The discovery collector exists, but a completed manifest-backed discovery memo and label-noise analysis are missing. |
| 3 | done | Registration before scoring | evaluation/registration.json locks criteria and plan before real held-out scoring; scripts/register.py --check passes. |
| 4 | not done | Floor, encoder, ONNX and INT8 | The floor passes synthetic training and serialization tests; ModernBERT passed ten authored-input T4 runtime checks; real floor results, encoder training and parity evidence remain missing. |
| 5 | not done | Recorded language models | The strict parser is tested; neither registered language-model inference run has completed. |
| 6 | not done | Calibrated cascade | The safety guard and no-close property tests pass; real development operating points and interior comparisons remain pending. |
| 7 | not done | Every-arm evaluation | Independent grading, bootstrap and BH code exist; qualifying held-out results for all arms are absent. |
| 8 | done | C1 through C7 verdicts | public_results/manifest.json and the live criteria page explicitly show every criterion as not_shown with its missing-evidence reason. |
| 9 | not done | Durable live API | The Vercel health endpoint returns guard_only; encrypted database variables are configured; deployment and independent successful receipt verification remain pending. |
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

The user approved the scoped database connection and secret salt transfer on 2026-11-05. Both encrypted variables are configured for the Cutover Vercel project's production and preview environments, pending a new deployment. Vercel also rejected the latest deployment because the free daily deployment allowance was exhausted. The serving commit is recorded separately from main.

Kaggle became available and the T4 hardware and ModernBERT probes passed. public_results/encoder-probe.json records the exact Apache-2.0 revision, pinned Transformers version and ten authored-input forwards. The classifier head is untrained; these are compatibility results, not task accuracy. Qwen3-1.7B and Qwen3-8B-AWQ probes were launched but their outcome could not be retrieved after the local browser connection failed. The draft GPU session may still be active and should be stopped when idle. No language-model quality, savings, latency SLO or rollout success is established.

The intake run completed in workflow 42115683275. Its baseline then failed because str.splitlines() treats Unicode separators inside valid JSON strings as record boundaries. Commit eb58b77 fixes the reader and adds regression tests that also prevent record text from appearing in parse errors. Workflow 42118098139 passed intake again and reached actual baseline training; final model results are not yet available. There are no actual injection counts, slice gaps, label-noise estimates, interior-test results or planted-release trips to report yet.

Stretch work is not done and is not counted toward the mandatory checklist.

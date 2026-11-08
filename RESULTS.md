# Cutover build status

The end-to-end release remains incomplete. Actual floor results and durable guard-only serving are verified. No trained model or completion tag has been promoted.

## Verified evidence

See report/baseline.md for the generated floor metrics and their limits. public_results/live-smoke.json, independent-receipts.json, live-load.json and independent-load-receipts.json separate HTTP observations from database reads. public_results/quality-verification.json identifies the passing software and notebook run.

## Definition of done

| Line | Status | Requirement | Evidence |
| --- | --- | --- | --- |
| 1 | not done | NHTSA intake | Actual intake, source locks, split counts and split digests are saved; private registered sample provenance still needs an independent audit. |
| 2 | not done | Discovery and label noise | The full discovery memo, registered noise-pattern analysis and new groups by year remain missing. |
| 3 | done | Registration before scoring | evaluation/registration.json remains unchanged and registration checks pass. |
| 4 | not done | Floor, encoder, ONNX and INT8 | Actual floor evaluation is published; ModernBERT only passed a runtime probe, without fine-tuning or parity. |
| 5 | not done | Recorded language models | Qwen probe scripts exist, but recovered probe outputs, registered task inference and injection counts are missing. |
| 6 | not done | Calibrated cascade | Floor thresholds were selected on development; the encoder cascade and interior comparisons remain unmeasured. |
| 7 | not done | Every-arm evaluation | Floor test and shadow metrics are available; complete paired comparisons, BH, slices and noise sensitivity are absent. |
| 8 | done | C1 through C7 verdicts | The manifest and live criteria page explicitly retain not_shown for the unverified shipped system. |
| 9 | not done | Live API and release controls | Guard-only triage receipts are independently verified; trained serving, live canary and workflow switch verification remain missing. |
| 10 | not done | 2026 shadow replay | The floor was graded on shadow; cascade disagreements, alarms and unseen-group analysis remain missing. |
| 11 | not done | Bad-release drill and rollback | Only synthetic monitor/rollback checks exist; real model variants and incident evidence are missing. |
| 12 | not done | Cost and ROI | Price rows and arithmetic tests exist; inference-only compute and every-arm ROI are unmeasured. |
| 13 | not done | Persistence, load and live switch | Independent receipts and bounded guard-only load are verified; model cold start and the live switch drill are missing. |
| 14 | not done | Handover pack | The baseline report and updated runbook exist; complete model cards, validation reports and analyst workbook remain missing. |
| 15 | not done | Full manifest rederivation | The baseline report and manifest rederive without drift in tests; all-arm inputs are not available. |
| 16 | not done | Live site and browser verification | public_results/browser-verification.json records all browser tests passing, including the live receipt; an actual sleeping-service check remains unobserved. |
| 17 | done | Documentation and investigations | README evidence matrix, dated decisions, three executed investigation notebooks, AGENTS, skills, SPEC and ADRs are present. |
| 18 | not done | Release quality and completion tag | Software tests, notebooks, coverage, Ruff and strict typing pass; full release provenance, palette/skills checks and the final tag remain outstanding. |

## Limitations and blocking dependencies

The floor operating point exceeds the registered review-load target. Its results cannot establish encoder, recorded-model or cascade quality. Published aggregates cannot reproduce discarded private weights and per-case predictions, so a fresh complete run and private artifact retention are needed for new paired comparisons.

The API is guard-only. Its measured request times are not trained-model latency. A genuine cold start was not forced or independently observed, and no live switch drill or planted-release drill has completed. All shipped-system criteria remain not_shown.

The Vercel quota blocker is resolved and pooled database access is corrected. Browser-control tooling is currently unavailable for recovering the Kaggle session; local shell networking also cannot resolve remote hosts. CI browser tests and connected-service tools remain usable. GPU outputs, further model implementation and evaluation, and the remaining handover work are still required.

## Stretch

Analyst note drafter, second customer, weekly drift report, tuned small model, MCP server and hardening are not done and are not counted toward mandatory completion.

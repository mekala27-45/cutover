# Actual TF-IDF baseline

This report is derived by scripts/derive_baseline.py from public_results/floor.json.
It describes the floor, not the encoder, language-model arms or live API.

| Split | Complaints | Queue hit | Queue hit 95% interval | Safety recall | Review share |
| --- | ---: | ---: | --- | ---: | ---: |
| shadow | 65,761 | 78.37% | 78.06% to 78.68% | 99.34% | 76.73% |
| test | 103,889 | 78.45% | 78.20% to 78.70% | 98.56% | 73.42% |

The queue interval uses the registered seeded complaint bootstrap. Safety recall
and review share above are point estimates; bounds were not exported for these metrics.

Training used 162,629 complaints and development used 32,662. Development selected C=1.
Thresholds: routing=0.9, safety=0.01, out-of-scope=0.3.

The floor review share is 73.42%, above the registered 40% load target. This operating point is not ready for release.
The shipped-system C1-C7 verdicts remain not shown because its required arms are absent.

The runner discarded private per-case records and model weights after exporting aggregates.
Aggregate results cannot reproduce paired arm comparisons, new slices or the trained model.
A future complete run must preserve those in an approved private artifact destination.

No p95 latency, inference-only throughput, cost saving or ROI is inferred from total run time.
Source commit: eb58b77126fab15a290f4fdfb312759db463b878.
Workflow: https://github.com/mekala27-45/cutover/actions/runs/42118098139.

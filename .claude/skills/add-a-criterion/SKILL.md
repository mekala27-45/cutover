---
name: add-a-criterion
description: Review a requested acceptance criterion change against Cutover's registered evaluation contract.
---

Read config/criteria.yaml, config/plan.json, evaluation/registration.json, and DECISIONS.md. Identify the metric, threshold, population, owner and interval rule. Check whether held-out scoring has happened. Preserve previous registrations and runs. For a changed criterion after scoring, create a dated change request identifying the prior version, reason and new evaluation population before preparing a new registration. Never overwrite an old result or describe a changed criterion as preregistered. Run scripts/register.py --check and the criterion tests. Report the concrete differences and their evidence.

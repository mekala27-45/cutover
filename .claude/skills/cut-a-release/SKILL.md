---
name: cut-a-release
description: Check Cutover release evidence and prepare a reversible promotion or rollback.
---

Read RESULTS.md, docs/RUNBOOK.md, evaluation/registration.json and public_results/manifest.json. Verify every required criterion and provenance field. Do not infer a passed release gate from software tests alone. Check the deployed commit and deployment quota. Verify database persistence with an independent read. Only the authorized Actions writer may change release_state. Preserve stable artifact bytes and verify their digest before rollback. Record the incident, version, operator reason and fresh post-action evidence. If a required result is absent, record not done and leave the release on hold. Never create the completion tag while the mandatory checklist is incomplete.

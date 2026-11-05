# Decisions

## 2026-11-05: registration byte normalization

The first CI run stopped before test scoring because Windows line endings produced a different byte digest on Linux. Registration now hashes parsed JSON with sorted keys and compact separators. The criterion values and plan have not changed. The original byte hashes were 5fbfe3b044d998258698d56baeefb2aac53195c7402b30a66cb506009ab6deba and a5e96d78596a46e49cf04c13c795d1043f9d929d818a2fa09342c05384c34638. The canonical hashes are in evaluation/registration.json. No model test results existed at this correction.

## 2026-11-05: restrict public data evidence

The data workflow has read-only repository permissions and exports only allowlisted aggregate evidence. No complaint narrative, ODINO or individual prediction is uploaded. Local runner records are discarded when the runner ends. Public auditability is limited to aggregate reports until a separately reviewed publication route is available.

## 2026-11-05: serving state before model promotion

The initial API is explicitly guard_only. It sends every complaint to a person and stores a receipt before answering. It makes no fitted model accuracy or completion claim. The safety word guard has priority. A failed database transaction returns unavailable.

## 2026-11-05: native FastAPI deployment probe

The current Vercel connection supports the FastAPI framework. The source includes a Dockerfile for portable reproduction. Native deployment is being checked; a container deployment is not yet verified.

## Archive discovery correction
The first live intake run failed before parsing because the static storage prefix was not an HTML catalog. The source now discovers archive names from NHTSA's official datasets page, including the observed 2020–2024 and 2025–2026 sets. There is no guessed-name fallback. No model evaluation ran before this change.

## Pinned source catalog
The published catalog returns HTTP 403 to the GitHub runner. The current archive names were read from NHTSA's public datasets page on 2026-11-05 and are now pinned in config/source-catalog.json. The runner only requests those official static downloads; it does not guess names or change its identity to defeat the catalog restriction.

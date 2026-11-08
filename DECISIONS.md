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

## 2026-11-05: lossless deduplication candidates
The initial full-overlap index could compare common phrases across most of the corpus. The replacement uses global-order prefix intersections at the registered Jaccard threshold, alongside MinHash LSH, and still verifies candidates with the original shingles. Hash collisions can only add candidates.

## 2026-11-05: empirical bootstrap counts
The bootstrap now samples multinomial counts over distinct observed metric values. This preserves the empirical resampling distribution for complaint-level binary and paired metrics without allocating a resample-by-population array. The resample count and seed in config/plan.json are unchanged.

## 2026-11-05: scoped runtime role
A direct database privilege query confirmed that cutover_api can insert receipts and update its request budget, but cannot update release_state or insert switch_history. The runtime cannot approve its own deployment.

## 2026-11-05: committed receipt before response
The API transaction owns both the hourly budget increment and receipt insert. A failed insert rolls back both and returns unavailable. tests/test_storage_contract.py checks ordering, rollback, and the absence of the narrative and client address in SQL parameters.

## 2026-11-05: free deployment ceiling
Vercel returned api-deployments-free-per-day after its free deployment allowance was exhausted. The source remains ahead of the serving commit. No paid upgrade was attempted; deployment remains blocked until the quota resets.

## 2026-11-05: explicit evidence absence
The public manifest marks all acceptance criteria not_shown while required model evidence is missing. The site uses empty evidence states rather than presenting fixture performance as a model result. The actual browser check observed this on all routes.

## 2026-11-05: price provenance
The shadow price rows come from mlspend at commit 4fafd79. That book contains two T4 spot rows with the same id. config/price-book.json selects the latest effective date on or before the analysis date and retains its source digest. No measured throughput or cost-saving claim follows from the price row alone.

## 2026-11-05: quality gates as failures
After behavioral tests reached the required coverage level and strict typing passed, CI was changed to fail on coverage below the threshold, Ruff errors, or strict type errors. Diagnostic output remains available so a green test count does not conceal quality failures.

## 2026-11-05: batched source changes
Later changes use a Git tree and a checked branch update to publish one coherent commit. Earlier single-file updates created unnecessary partial-build cancellations. Public history remains intact.

## 2026-11-05: rare-first prefix ordering
The first full intake did not finish within its initial observation window. Code inspection identified common boilerplate as a potential source of excessive prefix candidates under lexical ordering. Prefixes now use one corpus-wide frequency order with deterministic lexical ties. The Jaccard guarantee is unchanged. Progress output contains stage names, counts and source digests only. The obsolete run is cancelled to preserve the runner budget.

## 2026-11-05: approved runtime credential transfer
The user approved the recommended scoped connection and HMAC salt setup. Vercel confirmed both encrypted variables for production and preview. No credential value is committed or recorded in public evidence. Deployment remains pending the previously observed free daily quota reset.

## 2026-11-05: JSONL record boundaries
Actual intake completed, then the floor reader failed on a narrative containing a Unicode line separator. Python str.splitlines splits more than JSONL's LF record delimiter. The reader now iterates physical UTF-8 file lines and reports a line number without including the record in errors. Two regressions pass. Data, labels, thresholds and scoring criteria are unchanged.

## 2026-11-05: observed GPU compatibility
The previously unavailable Kaggle editor loaded and a T4 session started. ModernBERT-base passed ten authored-input forwards at fp16 with SDPA. Its new classification head is untrained, so no task accuracy is inferred. Encoder and language-model dependencies are kept in separate virtual environments. The Qwen probe outcome remains unverified after loss of browser control.

## 2026-11-05: local execution interruption
The local terminal rejected the runtime's Windows sandbox path configuration and the browser process could not restart. Remote GitHub connectors remained usable. Verified sources and evidence were preserved through GitHub; no unobserved GPU result or successful live receipt was claimed.

## 2026-11-07: pooled connection startup parameters
Live diagnostics identified an unsupported startup parameter. The runtime now sets statement_timeout with SET LOCAL after opening a transaction. It does not weaken TLS or expand database permissions. Independent receipt reads confirm that the corrected path commits both authored requests.

## 2026-11-07: release reads without write privileges
SELECT FOR SHARE would require write privileges on the release table. Ordinary SELECT now captures the release version used by the request; the same version is written into its receipt. The runtime still cannot mutate release state.

## 2026-11-07: aggregate evidence recovery
The completed floor artifacts were recovered by a read-only Actions workflow, checked against the frozen source and registration digests, and rendered by scripts/derive_baseline.py. Raw narratives and per-case records were not recovered or published. Full model and paired comparisons remain unavailable.

## 2026-11-07: immutable deployment verification
Production alias propagation briefly returned different serving revisions across requests. The smoke verification targets the exact immutable fixed deployment and records its commit. A separate production load and browser check verifies the public domain after propagation.

## 2026-11-07: browser runner compatibility
The pinned Playwright version does not support the newly selected ubuntu-latest image. The browser job uses ubuntu-24.04 explicitly; the dependency version and test assertions are unchanged.

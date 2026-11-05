CREATE SCHEMA IF NOT EXISTS cutover;
CREATE TABLE IF NOT EXISTS cutover.release_state (
  singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
  stable_digest text NOT NULL CHECK (stable_digest ~ '^[a-f0-9]{64}$'),
  canary_digest text CHECK (canary_digest ~ '^[a-f0-9]{64}$'),
  canary_weight numeric NOT NULL DEFAULT 0 CHECK (canary_weight BETWEEN 0 AND 1),
  killed boolean NOT NULL DEFAULT false,
  version bigint NOT NULL DEFAULT 1,
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS cutover.triage_log (
  receipt_id uuid PRIMARY KEY,
  text_digest text NOT NULL CHECK (text_digest ~ '^[a-f0-9]{64}$'),
  client_digest text NOT NULL CHECK (client_digest ~ '^[a-f0-9]{64}$'),
  release_digest text NOT NULL,
  release_version bigint NOT NULL,
  decision jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (decision #>> '{decision,action}' IN ('route','send_to_analyst')),
  CHECK (NOT decision ? 'narrative')
);
CREATE TABLE IF NOT EXISTS cutover.client_budget (
  client_digest text NOT NULL,
  window_start timestamptz NOT NULL,
  used integer NOT NULL CHECK (used BETWEEN 1 AND 60),
  PRIMARY KEY (client_digest,window_start)
);
CREATE TABLE IF NOT EXISTS cutover.switch_history (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  enabled boolean NOT NULL,
  reason text NOT NULL CHECK (length(reason) BETWEEN 3 AND 300),
  release_version bigint NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

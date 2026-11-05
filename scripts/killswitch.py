"""Operator entry point. Only the Actions writer credential may mutate state."""

import argparse
import os

from packages.api.store import connect


def main():
    if os.getenv("GITHUB_ACTIONS") != "true":
        raise SystemExit("actions_only")
    parser = argparse.ArgumentParser()
    parser.add_argument("--enabled", choices=["true", "false"], required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    if not 3 <= len(args.reason) <= 300:
        raise SystemExit("invalid_reason")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE cutover.release_state SET killed=%s,version=version+1,"
                "updated_at=now() WHERE singleton=true RETURNING version",
                (args.enabled == "true",),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError("release_not_initialized")
            cur.execute(
                "INSERT INTO cutover.switch_history(enabled,reason,release_version) "
                "VALUES (%s,%s,%s)",
                (args.enabled == "true", args.reason, row[0]),
            )
    print("switch state committed")


if __name__ == "__main__":
    main()

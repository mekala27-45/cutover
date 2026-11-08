"""Import and exercise guard-only serving in an isolated base dependency environment."""

import importlib.util
import json

import app


def main() -> None:
    # The former base dependency set overflowed the deployment's startup disk.
    for module in ("numpy", "scipy", "sklearn", "pyarrow", "torch", "transformers"):
        if importlib.util.find_spec(module) is not None:
            raise RuntimeError("analysis_dependency_in_runtime:" + module)
    health = app.health()
    assert health["status"] == "guard_only" and health["model_ready"] is False
    assert health["registration_digest"] and health["price_digest"]
    assert app.criteria()["criteria"]
    assert app.shadow()["status"] == "not_run"
    print(json.dumps({"runtime": "base_only", "health": "passed", "model_ready": False}))


if __name__ == "__main__":
    main()

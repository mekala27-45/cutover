from pathlib import Path

import pytest

from scripts.verify_release import verify


def test_current_incomplete_manifest_cannot_ship():
    with pytest.raises(ValueError, match="acceptance_criteria_not_met"):
        verify(Path(__file__).resolve().parents[1])

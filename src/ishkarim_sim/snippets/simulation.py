"""
simulation.py — fragmenty kodu z WORK.md dla obszaru sim.

UWAGA: To są fragmenty referencyjne wyekstrahowane z notatek badawczych.
Mogą wymagać dostosowania przed użyciem w produkcji.

Zawiera 1 fragmentów. Każdy poprzedzony komentarzem ze źródłem.
"""
# ruff: noqa
# type: ignore
from __future__ import annotations

# Source: New economic  and social simulation tools
def test_replay_determinism():
    run1 = run_simulation("configs/exp_001.yaml")
    run2 = run_simulation("configs/exp_001.yaml")
    assert run1["events_hash"] == run2["events_hash"]
    assert run1["metrics"]["total_volume"] == run2["metrics"]["total_volume"]

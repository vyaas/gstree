"""
test_bani_flow.py — Bani Flow trail correctness.

Validates that get_bani_flow returns chronologically sorted, non-empty
results for compositions that are known to appear in recordings.
"""

import pytest
from carnatic.graph_api import CarnaticGraph


def test_bani_flow_maakelara_has_entries(graph: CarnaticGraph) -> None:
    """
    get_bani_flow for maakelara_vicaaramu must return at least one entry
    (from the Jamshedpur 1961 recording and/or legacy youtube[] entries).
    """
    flow = graph.get_bani_flow("maakelara_vicaaramu")
    assert len(flow) >= 1, "Expected at least one bani flow entry for maakelara_vicaaramu"


def test_bani_flow_maakelara_includes_jamshedpur(graph: CarnaticGraph) -> None:
    """The Jamshedpur 1961 performance of Makelara must appear in the bani flow."""
    flow = graph.get_bani_flow("maakelara_vicaaramu")
    recording_ids = {e.get("recording_id") for e in flow}
    assert "jamshedpur_1961_madurai_mani_iyer" in recording_ids


def test_bani_flow_is_chronologically_sorted(graph: CarnaticGraph) -> None:
    """
    get_bani_flow entries must be sorted by date (ascending).
    Entries without a date sort last (date == '' or None).
    """
    flow = graph.get_bani_flow("maakelara_vicaaramu")
    dates = [e.get("date") or "9999" for e in flow]
    assert dates == sorted(dates), (
        f"Bani flow is not chronologically sorted: {dates}"
    )


def test_bani_flow_all_entries_have_composition_id(graph: CarnaticGraph) -> None:
    """Every entry in a bani flow must carry the queried composition_id."""
    flow = graph.get_bani_flow("maakelara_vicaaramu")
    for entry in flow:
        assert entry.get("composition_id") == "maakelara_vicaaramu", (
            f"Bani flow entry has wrong composition_id: {entry.get('composition_id')}"
        )


def test_bani_flow_gitarthamu_has_entries(graph: CarnaticGraph) -> None:
    """
    get_bani_flow for gitarthamu must return entries from legacy youtube[] data
    (multiple musicians have youtube[] entries for this composition).
    """
    flow = graph.get_bani_flow("gitarthamu")
    assert len(flow) >= 1, "Expected at least one bani flow entry for gitarthamu"


def test_bani_flow_nonexistent_composition_returns_empty(graph: CarnaticGraph) -> None:
    """get_bani_flow for an unknown composition_id returns an empty list."""
    flow = graph.get_bani_flow("nonexistent_composition_xyz")
    assert flow == []


def test_bani_flow_entries_have_required_fields(graph: CarnaticGraph) -> None:
    """Every bani flow entry must carry the minimum required fields."""
    required = ("composition_id", "display_title", "performers")
    flow = graph.get_bani_flow("maakelara_vicaaramu")
    for entry in flow:
        for field in required:
            assert field in entry, (
                f"Bani flow entry missing required field '{field}': {entry}"
            )

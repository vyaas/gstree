"""
conftest.py — shared pytest fixtures for the Carnatic test suite.

The CarnaticGraph instance is created once per test session and shared
across all test modules. This avoids redundant file I/O.
"""

import sys
from pathlib import Path

import pytest

# Ensure the project root is on sys.path so `carnatic.graph_api` is importable
# regardless of how pytest is invoked.
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from carnatic.graph_api import CarnaticGraph  # noqa: E402

GRAPH_JSON = PROJECT_ROOT / "carnatic" / "data" / "graph.json"


@pytest.fixture(scope="session")
def graph() -> CarnaticGraph:
    """
    Session-scoped CarnaticGraph fixture.
    Loads graph.json once; all tests share the same instance.
    """
    if not GRAPH_JSON.exists():
        pytest.skip(
            f"graph.json not found at {GRAPH_JSON}. "
            "Run migrate_to_graph_json.py and build_recording_index.py first."
        )
    return CarnaticGraph(GRAPH_JSON)

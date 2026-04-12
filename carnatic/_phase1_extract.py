#!/usr/bin/env python3
"""
_phase1_extract.py — One-shot extractor for Phase 1 of the render-refactor plan.

Reads carnatic/render.py and writes the carnatic/render/ package files by
slicing exact line ranges. Does NOT modify render.py itself.

Run from project root:
    python3 carnatic/_phase1_extract.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent          # carnatic/
SRC  = ROOT / "render.py"
PKG  = ROOT / "render"

lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)

def extract(start: int, end: int) -> str:
    """Return lines[start-1 : end] (1-based, inclusive)."""
    return "".join(lines[start - 1 : end])

# ── create package directory ───────────────────────────────────────────────────
PKG.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. carnatic/render/__init__.py
# ─────────────────────────────────────────────────────────────────────────────
init_content = '''\
"""
carnatic/render/__init__.py — Public API for the render package.
"""
from .data_loaders import load_compositions, load_recordings, yt_video_id, timestamp_to_seconds
from .data_transforms import build_recording_lookups, build_composition_lookups
from .graph_builder import build_elements
from .html_generator import render_html
from .sync import sync_graph_json

__all__ = [
    "load_compositions",
    "load_recordings",
    "yt_video_id",
    "timestamp_to_seconds",
    "build_recording_lookups",
    "build_composition_lookups",
    "build_elements",
    "render_html",
    "sync_graph_json",
]
'''
(PKG / "__init__.py").write_text(init_content, encoding="utf-8")
print("[WRITE] carnatic/render/__init__.py")

# ─────────────────────────────────────────────────────────────────────────────
# 2. carnatic/render/data_loaders.py
#    Sources: yt_video_id (76-79), load_compositions (83-87),
#             load_recordings (89-113), timestamp_to_seconds (115-122)
#    Refactored to accept Path parameters.
# ─────────────────────────────────────────────────────────────────────────────
data_loaders_content = '''\
"""
carnatic/render/data_loaders.py — Pure I/O functions for loading Carnatic data.

All functions accept explicit Path parameters so they are testable without
relying on module-level globals.
"""
import json
import re
from pathlib import Path


def yt_video_id(url: str) -> "str | None":
    """Extract an 11-character YouTube video ID from any YouTube URL form."""
    m = re.search(r"(?:v=|youtu\\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


def timestamp_to_seconds(ts: str) -> int:
    """Convert \'MM:SS\' or \'HH:MM:SS\' to integer seconds."""
    parts = [int(p) for p in ts.strip().split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    raise ValueError(f"Unrecognised timestamp format: {ts!r}")


def load_compositions(compositions_file: Path) -> dict:
    """Load compositions.json; return empty structure if absent."""
    if compositions_file.exists():
        return json.loads(compositions_file.read_text(encoding="utf-8"))
    return {"ragas": [], "composers": [], "compositions": []}


def load_recordings(recordings_dir: Path, recordings_file: Path) -> dict:
    """
    Load recordings from a recordings/ directory (one .json per recording).
    Each file is a bare recording object — no {"recordings": [...]} wrapper.
    Files are sorted alphabetically by name for a deterministic compile order.
    Files whose names start with \'_\' (e.g. _index.json) are skipped.

    Falls back to the legacy monolithic recordings_file if the directory does
    not exist (backward-compatible during migration).
    """
    if recordings_dir.is_dir():
        files = sorted(
            f for f in recordings_dir.glob("*.json")
            if not f.name.startswith("_")
        )
        recordings = [
            json.loads(f.read_text(encoding="utf-8"))
            for f in files
        ]
        return {"recordings": recordings}
    # legacy fallback: monolithic recordings.json
    if recordings_file.exists():
        return json.loads(recordings_file.read_text(encoding="utf-8"))
    return {"recordings": []}
'''
(PKG / "data_loaders.py").write_text(data_loaders_content, encoding="utf-8")
print("[WRITE] carnatic/render/data_loaders.py")

# ─────────────────────────────────────────────────────────────────────────────
# 3. carnatic/render/data_transforms.py
#    Sources: build_recording_lookups (124-195), build_composition_lookups (197-255)
# ─────────────────────────────────────────────────────────────────────────────
transforms_header = '''\
"""
carnatic/render/data_transforms.py — Denormalisation and lookup-table builders.
"""
from collections import defaultdict

'''
transforms_body = extract(124, 255)
(PKG / "data_transforms.py").write_text(transforms_header + transforms_body, encoding="utf-8")
print("[WRITE] carnatic/render/data_transforms.py")

# ─────────────────────────────────────────────────────────────────────────────
# 4. carnatic/render/graph_builder.py
#    Sources: constants (27-72), build_elements (259-344)
#    build_elements uses yt_video_id → import from .data_loaders
# ─────────────────────────────────────────────────────────────────────────────
gb_header = '''\
"""
carnatic/render/graph_builder.py — Cytoscape element construction.

Constants (ERA_COLORS, ERA_LABELS, INSTRUMENT_SHAPES, NODE_SIZES,
ERA_FONT_SIZES) live here alongside build_elements().
"""
from collections import defaultdict
from .data_loaders import yt_video_id

'''
gb_constants = extract(25, 72)   # ERA_COLORS … ERA_FONT_SIZES block
gb_blank     = "\n"
gb_elements  = extract(259, 344) # build_elements()
(PKG / "graph_builder.py").write_text(
    gb_header + gb_constants + gb_blank + gb_elements, encoding="utf-8"
)
print("[WRITE] carnatic/render/graph_builder.py")

# ─────────────────────────────────────────────────────────────────────────────
# 5. carnatic/render/html_generator.py
#    Sources: render_html (348-3493) — verbatim, no edits
# ─────────────────────────────────────────────────────────────────────────────
hg_header = '''\
"""
carnatic/render/html_generator.py — HTML template assembly.

render_html() returns the complete self-contained graph.html string.
Phase 2 will extract the embedded HTML/JS template into a separate file.
"""
import json

'''
hg_body = extract(348, 3493)
(PKG / "html_generator.py").write_text(hg_header + hg_body, encoding="utf-8")
print("[WRITE] carnatic/render/html_generator.py")

# ─────────────────────────────────────────────────────────────────────────────
# 6. carnatic/render/sync.py
#    Sources: _sync_graph_json (3497-3579) — renamed to sync_graph_json
# ─────────────────────────────────────────────────────────────────────────────
sync_header = '''\
"""
carnatic/render/sync.py — graph.json sync logic (ADR-016).

sync_graph_json() keeps graph.json current from musicians.json,
compositions.json, and the recordings/ directory before each render.
Atomic write via temp file + os.replace.
"""
import json
import os
import tempfile
from pathlib import Path

'''
# Extract the function body and rename _sync_graph_json → sync_graph_json
sync_body_raw = extract(3497, 3579)
sync_body = sync_body_raw.replace("def _sync_graph_json(", "def sync_graph_json(", 1)
# The function uses `import os as _os` and `import tempfile as _tempfile` inline;
# since we now import at module level, replace those inline imports with pass-throughs.
sync_body = sync_body.replace("    import os as _os\n", "")
sync_body = sync_body.replace("    import tempfile as _tempfile\n", "")
sync_body = sync_body.replace("_os.replace(", "os.replace(")
sync_body = sync_body.replace("_tempfile.NamedTemporaryFile(", "tempfile.NamedTemporaryFile(")
(PKG / "sync.py").write_text(sync_header + sync_body, encoding="utf-8")
print("[WRITE] carnatic/render/sync.py")

# ─────────────────────────────────────────────────────────────────────────────
# 7. Rewrite carnatic/render.py as thin orchestrator
# ─────────────────────────────────────────────────────────────────────────────
orchestrator = '''\
#!/usr/bin/env python3
"""
render.py — Orchestrator: renders graph.html from Carnatic knowledge graph data.

Delegates to carnatic/render/ package modules:
  sync          → sync graph.json from source files
  data_loaders  → load JSON data
  data_transforms → build lookup tables
  graph_builder → build Cytoscape elements
  html_generator → assemble final HTML
"""
import sys
from pathlib import Path

ROOT              = Path(__file__).parent
GRAPH_FILE        = ROOT / "data" / "graph.json"
DATA_FILE         = ROOT / "data" / "musicians.json"
COMPOSITIONS_FILE = ROOT / "data" / "compositions.json"
RECORDINGS_FILE   = ROOT / "data" / "recordings.json"
OUT_FILE          = ROOT / "graph.html"

# Ensure project root is on sys.path for package imports
_project_root = str(ROOT.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from carnatic.render.sync import sync_graph_json
from carnatic.render.data_loaders import load_compositions, load_recordings
from carnatic.render.data_transforms import build_recording_lookups, build_composition_lookups
from carnatic.render.graph_builder import build_elements
from carnatic.render.html_generator import render_html


def main() -> None:
    # Step 0: sync graph.json from source files (ADR-016)
    if GRAPH_FILE.exists() and DATA_FILE.exists():
        sync_graph_json(GRAPH_FILE, DATA_FILE, COMPOSITIONS_FILE)

    # Step 1: load data (ADR-013: graph.json preferred, legacy fallback)
    if GRAPH_FILE.exists():
        from carnatic.graph_api import CarnaticGraph
        cg = CarnaticGraph(GRAPH_FILE)
        graph = {
            "nodes": cg.get_all_musicians(),
            "edges": cg.get_all_edges(),
        }
        comp_data = {
            "ragas":        cg.get_all_ragas(),
            "composers":    cg.get_all_composers(),
            "compositions": cg.get_all_compositions(),
        }
        recordings_data = {"recordings": cg.get_all_recordings()}
        print(f"[LOAD] graph.json  ({len(graph[\'nodes\'])} nodes, {len(graph[\'edges\'])} edges, "
              f"{len(recordings_data[\'recordings\'])} recordings)")
    else:
        import json
        graph           = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        comp_data       = load_compositions(COMPOSITIONS_FILE)
        recordings_data = load_recordings(ROOT / "data" / "recordings", RECORDINGS_FILE)
        print(f"[LOAD] musicians.json (legacy)  ({len(graph[\'nodes\'])} nodes, {len(graph[\'edges\'])} edges)")

    # Step 2: build lookup tables
    composition_to_nodes, raga_to_nodes = build_composition_lookups(graph, comp_data, recordings_data)
    musician_to_performances, composition_to_performances, raga_to_performances = \\
        build_recording_lookups(recordings_data, comp_data)

    # Step 3: build Cytoscape elements
    elements = build_elements(graph)

    # Step 4: render HTML
    html = render_html(
        elements, graph, comp_data,
        composition_to_nodes, raga_to_nodes,
        recordings_data,
        musician_to_performances,
        composition_to_performances,
        raga_to_performances,
    )
    OUT_FILE.write_text(html, encoding="utf-8")
    print(f"[RENDERED] {OUT_FILE}  ({len(graph[\'nodes\'])} nodes, {len(graph[\'edges\'])} edges)")


if __name__ == "__main__":
    main()
'''
SRC.write_text(orchestrator, encoding="utf-8")
print("[WRITE] carnatic/render.py  (thin orchestrator)")

print("\n[DONE] All files written. Run: python3 carnatic/render.py")

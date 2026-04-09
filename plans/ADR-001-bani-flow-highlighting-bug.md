# ADR-001: Fix Bani Flow Musician Highlighting for Structured Recordings

**Status:** Accepted
**Date:** 2026-04-08

---

## Context

The Bani Flow feature allows rasikas to filter the graph by composition or raga, highlighting musicians who have performed that work. This is a **core immersion pattern** - the ability to trace a composition's transmission across the parampara.

However, a critical bug exists: **musicians only light up if they have `youtube[]` entries in `musicians.json`**. Musicians who appear solely in the structured `recordings/` directory are invisible to the highlighting logic, even though they appear correctly in the listening trail.

### Current Behaviour

- **Gitarthamu** (works): 7 musicians highlighted because they have `youtube[]` entries in `musicians.json`
- **Bantureeti Kolu** (broken): 0 musicians highlighted, even though Ramnad Krishnan performed it in `wesleyan_1967_ramnad_krishnan.json`

### The Architectural Tension

We have **two data sources** for recordings:

1. **Legacy schema** (`musicians.json` → `youtube[]` array) - flat, embedded in musician nodes
2. **Structured schema** (`recordings/*.json`) - normalized, session-based, multi-performer

The bug exists because [`build_composition_lookups()`](carnatic/render.py:191) only indexes the legacy schema. The structured schema is indexed separately by [`build_recording_lookups()`](carnatic/render.py:119), but those indices are not merged into the graph highlighting logic.

---

## Pattern

This resolves the **Levels of Scale** pattern failure. A composition exists at multiple scales:
- The abstract work (in `compositions.json`)
- The individual performance (in `recordings/*.json`)
- The musician who transmitted it (in `musicians.json`)

The graph must honour all three levels. When a rasika selects a composition, **every musician who has transmitted it must light up**, regardless of which data source documents that transmission.

---

## Decision

**Merge the structured recordings index into the composition-to-nodes mapping.**

Specifically, modify [`build_composition_lookups()`](carnatic/render.py:191) to:

1. Continue indexing legacy `youtube[]` entries (backward compatibility)
2. **Also index structured recordings** by extracting `musician_id` from each performance's `performers[]` array
3. Return a **unified** `composition_to_nodes` dict that includes musicians from both sources

### Code Changes Required

#### File: [`carnatic/render.py`](carnatic/render.py:191)

**Current signature:**
```python
def build_composition_lookups(graph: dict, comp_data: dict) -> tuple[dict, dict]:
```

**New signature:**
```python
def build_composition_lookups(
    graph: dict, 
    comp_data: dict, 
    recordings_data: dict
) -> tuple[dict, dict]:
```

**Logic changes:**

1. After indexing legacy `youtube[]` entries, iterate through `recordings_data["recordings"]`
2. For each recording → session → performance:
   - Extract `composition_id` and `raga_id`
   - Extract all `musician_id` values from `performers[]` (skip `None`)
   - Add each `musician_id` to `composition_to_nodes[composition_id]`
   - Add each `musician_id` to `raga_to_nodes[raga_id]` (if raga_id is set)
3. Deduplicate (already handled by the existing `if node_id not in ...` checks)

#### File: [`carnatic/render.py`](carnatic/render.py:1524) - `main()` function

**Current call order:**
```python
recordings_data = load_recordings()
composition_to_nodes, raga_to_nodes = build_composition_lookups(graph, comp_data)
musician_to_performances, composition_to_performances, raga_to_performances = \
    build_recording_lookups(recordings_data, comp_data)
```

**New call order:**
```python
recordings_data = load_recordings()
composition_to_nodes, raga_to_nodes = build_composition_lookups(
    graph, comp_data, recordings_data  # Pass recordings_data
)
musician_to_performances, composition_to_performances, raga_to_performances = \
    build_recording_lookups(recordings_data, comp_data)
```

---

## Consequences

### Positive

1. **Fixes the bug** - All musicians who have performed a composition will now be highlighted, regardless of data source
2. **No data migration required** - This is purely a rendering pipeline fix
3. **Backward compatible** - Legacy `youtube[]` entries continue to work
4. **Consistent with listening trail** - The graph highlighting will now match what appears in the listening trail
5. **Scales forward** - As more structured recordings are added, they automatically participate in Bani Flow highlighting

### Negative

1. **Slight performance cost** - We now iterate through recordings twice (once for `build_composition_lookups`, once for `build_recording_lookups`)
   - **Mitigation**: This is acceptable. The recordings dataset is small (currently 4 files), and the iteration is O(n) where n = total performances across all recordings. For a dataset of ~100 recordings with ~10 performances each, this is ~1000 iterations - negligible.

2. **Potential for duplicate highlighting** - If a musician has both a legacy `youtube[]` entry AND appears in structured recordings for the same composition, they will be indexed twice
   - **Mitigation**: Already handled. The existing code checks `if node_id not in composition_to_nodes[cid]` before appending, so duplicates are automatically prevented.

### What the Carnatic Coder Must Implement

1. Modify [`build_composition_lookups()`](carnatic/render.py:191) signature to accept `recordings_data: dict`
2. Add a second indexing loop after the existing `youtube[]` loop:
   ```python
   # Index structured recordings
   for rec in recordings_data.get("recordings", []):
       for session in rec.get("sessions", []):
           performers = session.get("performers", [])
           for perf in session.get("performances", []):
               comp_id = perf.get("composition_id")
               raga_id = perf.get("raga_id")
               
               # Infer raga from composition if not set
               if not raga_id and comp_id:
                   raga_id = comp_raga.get(comp_id)
               
               # Index each performer
               for pf in performers:
                   mid = pf.get("musician_id")
                   if mid:
                       if comp_id and mid not in composition_to_nodes[comp_id]:
                           composition_to_nodes[comp_id].append(mid)
                       if raga_id and mid not in raga_to_nodes[raga_id]:
                           raga_to_nodes[raga_id].append(mid)
   ```
3. Update the call site in [`main()`](carnatic/render.py:1528) to pass `recordings_data`

### What the Librarian Must Do

**Nothing.** This is a pure rendering fix. No data changes required.

---

## Alternatives Considered

### Alternative 1: Deprecate legacy `youtube[]` schema entirely

**Rejected.** This would require migrating all existing `youtube[]` entries to structured recordings, which is a large data migration effort. The dual-schema approach is working; we just need to index both sources.

### Alternative 2: Build a separate highlighting layer in JavaScript

**Rejected.** The highlighting logic should be driven by the same data that populates the listening trail. Splitting the logic would create two sources of truth and risk future divergence.

### Alternative 3: Only index structured recordings, ignore legacy `youtube[]`

**Rejected.** This would break highlighting for compositions that only have legacy entries (e.g., many of the single YouTube links added early in the project).

---

## Verification

After implementing this fix, verify:

1. **Bantureeti Kolu** now highlights Ramnad Krishnan when selected in Bani Flow
2. **Gitarthamu** continues to highlight all 7 musicians (no regression)
3. The listening trail continues to show all performances (no change expected)
4. No console errors in the browser
5. Run `python carnatic/render.py` and verify the output HTML contains Ramnad Krishnan in `compositionToNodes["bantureeti_kolu"]`

---

## Query This Enables

**Rasika query:** "Show me everyone in the parampara who has sung Bantureeti Kolu."

**Before this fix:** Empty graph (broken).  
**After this fix:** Ramnad Krishnan lights up, edges to his gurus and shishyas remain visible, the listening trail shows his 1967 Wesleyan performance.

This is the **immersion pattern** working as designed: the rasika can now trace the transmission of this rare Hamsanadam composition through the lineage.

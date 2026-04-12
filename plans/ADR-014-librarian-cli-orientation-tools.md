# ADR-014: Librarian CLI Orientation Tools

**Status:** Proposed
**Date:** 2026-04-12

---

## Context

### The problem

The Librarian's current session-startup protocol (defined in `carnatic/.clinerules` and
`.roomodes`) requires reading two large JSON files in full before doing anything:

```
1. Read carnatic/data/musicians.json   ← potentially 3,000+ lines
2. Read carnatic/data/compositions.json ← potentially 1,000+ lines
```

This is expensive in three ways:

1. **Token cost.** The full files consume a large fraction of the context window before
   any work begins. As the graph grows, this cost grows linearly.

2. **Guesswork.** The Librarian reads the files to answer questions like "is this
   musician already in the graph?" or "does this raga exist?" — questions that are
   trivially answerable by a targeted query. Reading the whole file to answer a point
   query is the wrong tool.

3. **Fragility.** When the Librarian patches `graph.json` by hand (using `apply_diff`),
   it must mentally track the current state of the file. A CLI tool that returns the
   exact current value of a field removes the need for that mental model.

### The opportunity

`carnatic/graph_api.py` (ADR-013, Phase 2) already implements the full traversal layer
as a pure Python class. Every query the Librarian needs to answer at session start is
already a method call away. What is missing is a set of **thin CLI wrappers** that
expose those methods as one-line shell commands with terse, LLM-readable output.

The governing question: *what does the Librarian actually need to know before touching
the data?*

| Question | Current method | Proposed method |
|---|---|---|
| How many musicians/ragas/compositions/recordings are in the graph? | Read both JSON files, count manually | `python3 carnatic/graph_api.py --stats` (already exists) |
| Is musician X already in the graph? | Scan `musicians.json` | `python3 carnatic/cli.py musician-exists <id_or_label>` |
| Is this YouTube URL already attached to any node? | Scan all `youtube[]` arrays | `python3 carnatic/cli.py url-exists <url>` |
| Does raga X exist in `compositions.json`? | Read `compositions.json` | `python3 carnatic/cli.py raga-exists <id_or_name>` |
| Does composition X exist? | Read `compositions.json` | `python3 carnatic/cli.py composition-exists <id_or_title>` |
| What are the exact field values for musician X? | Read `musicians.json`, find node | `python3 carnatic/cli.py get-musician <id>` |
| Who are the gurus of musician X? | Read `musicians.json`, trace edges | `python3 carnatic/cli.py gurus-of <id>` |
| Who are the shishyas of musician X? | Read `musicians.json`, trace edges | `python3 carnatic/cli.py shishyas-of <id>` |
| Is recording R already in the graph? | Scan `recording_refs` | `python3 carnatic/cli.py recording-exists <id>` |
| What compositions are in raga X? | Read `compositions.json` | `python3 carnatic/cli.py compositions-in-raga <id>` |
| After patching, is the graph coherent? | Visual inspection | `python3 -m pytest carnatic/tests/ -q` |

---

## Pattern

**Levels of Scale** (Alexander, *A Pattern Language*, Pattern 26) — orientation must
happen at the right scale. The Librarian does not need to read the whole building to
answer a reference question. A catalogue query (does this entry exist?) operates at a
different scale than a full data read. The CLI tools enforce the correct scale for each
question.

**Strong Centres** — each CLI command is a strong centre: a single, named, purposeful
operation with a predictable output contract. The Librarian can compose these commands
without understanding the internals of `graph_api.py`.

**Boundaries** — the CLI layer is the boundary between the Librarian's natural-language
reasoning and the graph's machine-readable state. It is a clean interface: command in,
terse structured output out. No JSON parsing required on the Librarian's side.

---

## Decision

### Tool: `carnatic/cli.py`

A single entry-point script that exposes all Librarian-facing queries as subcommands.
It is a thin wrapper over `CarnaticGraph` — no logic of its own. Every subcommand
prints terse, structured output designed to be read by an LLM in a single glance.

**Design principles:**

1. **Terse output by default.** Commands print the minimum information needed to answer
   the question. `--verbose` or `--json` flags expand to full detail when needed.

2. **Exit codes are semantic.** Exit 0 = found/valid. Exit 1 = not found/invalid.
   This allows the Librarian to use the exit code as a boolean without parsing output.

3. **Fuzzy matching on labels.** Existence checks accept both `id` (snake_case) and
   `label` (display name, case-insensitive substring match). This handles the common
   case where the Librarian knows the musician's name but not their exact ID.

4. **All commands are read-only.** `cli.py` never writes to any file. It is a query
   tool only. Writes go through the Librarian's established `apply_diff` workflow.

5. **Invokable from project root.** All commands run as
   `python3 carnatic/cli.py <subcommand> [args]`.

---

### Subcommand taxonomy

#### Group 1 — Orientation (replaces full file reads at session start)

```
python3 carnatic/cli.py stats
```
**Output:**
```
Musicians:    42  (nodes)
Edges:        38  (guru-shishya)
Ragas:        24
Composers:    12
Compositions: 67
Recordings:    8  (structured concert files)
```
*Replaces: reading both JSON files to count entries.*

---

#### Group 2 — Existence checks (replaces scanning for duplicates)

```
python3 carnatic/cli.py musician-exists <query>
```
`<query>` is matched against both `id` (exact) and `label` (case-insensitive substring).

**Output (found):**
```
FOUND  madurai_mani_iyer  "Madurai Mani Iyer"  golden_age  vocal
```
**Output (not found):**
```
NOT FOUND  "parulana mata"
```
Exit 0 if found, exit 1 if not found.

---

```
python3 carnatic/cli.py raga-exists <query>
```
`<query>` matched against `id` (exact) and `name`/`aliases` (case-insensitive).

**Output (found):**
```
FOUND  kapi  "Kapi"  aliases: ["Kafi"]  melakarta: null
```
**Output (not found):**
```
NOT FOUND  "kapi"
```

---

```
python3 carnatic/cli.py composition-exists <query>
```
`<query>` matched against `id` (exact) and `title` (case-insensitive substring).

**Output (found):**
```
FOUND  parulana_mata  "Parulana Mata"  raga: kapi  composer: tyagaraja
```
**Output (not found):**
```
NOT FOUND  "parulana mata"
```

---

```
python3 carnatic/cli.py recording-exists <query>
```
`<query>` matched against `id` (exact) and `title` (case-insensitive substring).

**Output (found):**
```
FOUND  jamshedpur_1961_madurai_mani_iyer  "Madurai Mani Iyer — Jamshedpur, 1961"  date: 1961
```

---

```
python3 carnatic/cli.py url-exists <url>
```
Checks whether the YouTube video ID extracted from `<url>` already appears in any
`youtube[]` entry across all musician nodes, or as the `video_id` of any recording.

**Output (found in musician node):**
```
FOUND  video_id: lNSJJMWLtfc
  musician node:  abhishek_raghuram  youtube[2]
```
**Output (found in recording):**
```
FOUND  video_id: _rj8fHJiSLA
  recording:  poonamallee_1965  "Srinivasa Farms Concert, Poonamallee 1965"
```
**Output (not found):**
```
NOT FOUND  video_id: XXXXXXXXXXX
```
*This is the key tool for the YouTube ingestion workflow. The Librarian runs this
before adding any YouTube link — no more scanning `youtube[]` arrays by eye.*

---

#### Group 3 — Lookup (replaces targeted reads of specific nodes)

```
python3 carnatic/cli.py get-musician <id>
```
Returns the full musician node as compact JSON (one field per line).

**Output:**
```json
{
  "id": "madurai_mani_iyer",
  "label": "Madurai Mani Iyer",
  "born": 1912,
  "died": 1968,
  "era": "golden_age",
  "instrument": "vocal",
  "bani": "semmangudi",
  "youtube_count": 3,
  "sources": ["Wikipedia"]
}
```
*Note: `youtube_count` replaces the full `youtube[]` array in default output.
Use `--json` to get the full node including all youtube entries.*

---

```
python3 carnatic/cli.py get-raga <id>
```
```
python3 carnatic/cli.py get-composition <id>
```
Same pattern — compact summary by default, `--json` for full object.

---

```
python3 carnatic/cli.py gurus-of <musician_id>
```
**Output:**
```
Gurus of madurai_mani_iyer:
  muthiah_bhagavatar  "Harikesanallur Muthiah Bhagavatar"  confidence: 0.95
```

---

```
python3 carnatic/cli.py shishyas-of <musician_id>
```
**Output:**
```
Shishyas of semmangudi_srinivasa_iyer:
  ms_subbulakshmi     "M.S. Subbulakshmi"     confidence: 0.85
  ramnad_krishnan     "Ramnad Krishnan"        confidence: 0.90
  ...
```

---

```
python3 carnatic/cli.py lineage <musician_id>
```
**Output:**
```
Lineage chain (upward) from tm_krishna:
  tm_krishna          "T.M. Krishna"           contemporary
  semmangudi_srinivasa_iyer  "Semmangudi Srinivasa Iyer"  living_pillars
  ...
```

---

```
python3 carnatic/cli.py recordings-for <musician_id>
```
**Output:**
```
Recordings for lalgudi_jayaraman:
  jamshedpur_1961_madurai_mani_iyer  "Madurai Mani Iyer — Jamshedpur, 1961"  1961
  music_academy_1965_lalgudi         "Lalgudi Jayaraman — Music Academy 1965"  1965
```

---

```
python3 carnatic/cli.py compositions-in-raga <raga_id>
```
**Output:**
```
Compositions in raga kapi:
  parulana_mata  "Parulana Mata"  composer: tyagaraja  tala: adi
  ...
```

---

#### Group 4 — Validation (replaces visual inspection after patching)

```
python3 carnatic/cli.py validate
```
Runs the same referential integrity checks as the test suite, but as a single
command with human-readable output. Designed to be run after any patch.

**Output (clean):**
```
✓  All musician_ids in recordings exist in graph
✓  All composition_ids in performances exist in compositions
✓  All raga_ids in performances exist in ragas
✓  All composer_ids in performances exist in composers
✓  No duplicate (source, target) edge pairs
✓  No self-loop edges
Graph is coherent.
```

**Output (errors found):**
```
✗  Recording poonamallee_1965 session 1 performer: musician_id 'xyz' not in graph
✗  Recording jamshedpur_1961 perf 3: composition_id 'unknown_comp' not in compositions
2 integrity errors found.
```
Exit 0 if clean, exit 1 if errors.

*This replaces running the full pytest suite for a quick post-patch sanity check.
The full suite (`pytest carnatic/tests/ -q`) remains the authoritative validator.*

---

### Before/after JSON shape

This ADR does not change any data schema. It adds a new Python script only.

**Before (session startup):**
```
# Librarian reads ~4,000 lines of JSON before doing anything
read_file: carnatic/data/musicians.json   → 3,000+ lines
read_file: carnatic/data/compositions.json → 1,000+ lines
```

**After (session startup):**
```bash
# Librarian runs one command to orient
python3 carnatic/cli.py stats
# → 6 lines of output

# Then targeted queries as needed
python3 carnatic/cli.py musician-exists "Parulana Mata"
python3 carnatic/cli.py url-exists "https://youtu.be/XXXXXXXXXXX"
```

---

### Updated `.clinerules` session startup

The new session startup protocol for the Librarian replaces steps 1–2:

```
## Session startup
1. Run `python3 carnatic/cli.py stats` to orient (replaces reading musicians.json + compositions.json).
2. Use targeted CLI queries (see CLI Tools section below) before any read_file call.
3. Read the Open questions section below — it is the living memory of this project.
4. At the end of every session: update the Open questions section, then hand off to the Git Fiend.
```

The full file reads (`read_file: musicians.json`) are **reserved for patching sessions**
where the Librarian needs to construct an `apply_diff` block. Even then, the Librarian
should use `get-musician <id>` to retrieve the exact current value of a field before
constructing the diff — not read the whole file.

---

### Updated Librarian workflow for YouTube ingestion

The YouTube ingestion workflow (Workflow A in `READYOU.md`) gains a mandatory first step:

```
Step 0 — Check for duplicates FIRST.
  python3 carnatic/cli.py url-exists <url>
  If FOUND: report to user, do not add.
  If NOT FOUND: proceed to Step 1.

Step 1 — Check if the artist is in the graph.
  python3 carnatic/cli.py musician-exists "<artist name from title>"
  If FOUND: note the exact id for use in the youtube entry.
  If NOT FOUND: flag — do not create a node without user instruction.

Step 2 — Check if the raga is in compositions.json.
  python3 carnatic/cli.py raga-exists "<raga name from title>"
  If FOUND: note the exact id.
  If NOT FOUND: add raga first (Workflow E), then proceed.

Step 3 — Check if the composition is in compositions.json.
  python3 carnatic/cli.py composition-exists "<composition name from title>"
  If FOUND: note the exact id.
  If NOT FOUND: add composition first (Workflow E), then proceed.

Steps 4–8: unchanged from current Workflow A.
```

---

## Consequences

### What this enables

- **Token reduction at session start.** The Librarian no longer reads two large JSON
  files before doing anything. Orientation costs 6 lines of output instead of 4,000+
  lines of JSON.

- **Deterministic duplicate detection.** `url-exists` and `musician-exists` are
  machine-checked, not eye-scanned. False negatives (missed duplicates) become
  structurally impossible.

- **Faster iteration.** The Librarian can answer "is X in the graph?" in one command
  instead of a read-file + mental scan cycle.

- **Post-patch validation without pytest.** `validate` gives immediate feedback after
  any `apply_diff` without requiring the full test suite.

- **Composable workflow.** The CLI tools compose: check existence → get exact field
  values → construct diff → validate. Each step is a single command.

### What this forecloses

- **Nothing.** This ADR adds a new script; it does not remove or change any existing
  file, schema, or workflow. The full file reads remain available when needed (e.g.
  when constructing a large `apply_diff` block that touches many nodes).

### What this does NOT change

- The data schema (`graph.json`, `recordings/*.json`, `compositions.json`) — unchanged.
- The `apply_diff` patching workflow — unchanged.
- The test suite (`carnatic/tests/`) — unchanged; `validate` is a convenience wrapper,
  not a replacement.
- The Librarian's hard constraints — unchanged.

### Queries that become possible (or cheaper)

| Query | Before | After |
|---|---|---|
| Is "Parulana Mata" in the graph? | Read compositions.json (~1000 lines) | `composition-exists "parulana mata"` → 1 line |
| Is this YouTube URL a duplicate? | Scan all youtube[] arrays by eye | `url-exists <url>` → 1 line |
| What is Madurai Mani Iyer's exact `bani` field? | Read musicians.json, find node | `get-musician madurai_mani_iyer` → 8 lines |
| Who are Semmangudi's shishyas? | Read musicians.json, trace edges | `shishyas-of semmangudi_srinivasa_iyer` → N lines |
| Is the graph coherent after my patch? | Run pytest (requires test knowledge) | `validate` → pass/fail |

---

## Implementation

**Agent:** Carnatic Coder  
**Deliverable:** `carnatic/cli.py` — a single script, ~300 lines, wrapping `CarnaticGraph`  
**Dependencies:** `carnatic/graph_api.py` (ADR-013 Phase 2, already implemented)  
**No new dependencies** beyond what ADR-013 already requires.

**After implementation:**
- Carnatic Coder updates `carnatic/.clinerules` session startup section.
- Carnatic Coder updates `.roomodes` Librarian `customInstructions` session startup section.
- Graph Architect updates this ADR status to Accepted.
- Git Fiend commits: `chore(config): add librarian CLI orientation tools`.

---

## Subcommand reference (for `.clinerules` embedding)

```bash
# Orientation
python3 carnatic/cli.py stats

# Existence checks (exit 0 = found, exit 1 = not found)
python3 carnatic/cli.py musician-exists   <id_or_label>
python3 carnatic/cli.py raga-exists       <id_or_name>
python3 carnatic/cli.py composition-exists <id_or_title>
python3 carnatic/cli.py recording-exists  <id_or_title>
python3 carnatic/cli.py url-exists        <youtube_url>

# Lookup (compact summary; add --json for full object)
python3 carnatic/cli.py get-musician      <id>
python3 carnatic/cli.py get-raga          <id>
python3 carnatic/cli.py get-composition   <id>
python3 carnatic/cli.py gurus-of          <musician_id>
python3 carnatic/cli.py shishyas-of       <musician_id>
python3 carnatic/cli.py lineage           <musician_id>
python3 carnatic/cli.py recordings-for    <musician_id>
python3 carnatic/cli.py compositions-in-raga <raga_id>

# Validation (exit 0 = coherent, exit 1 = errors found)
python3 carnatic/cli.py validate
```

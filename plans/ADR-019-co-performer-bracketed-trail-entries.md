# ADR-019: Co-performer-Bracketed Listening Trail Entries

**Status:** Proposed
**Date:** 2026-04-12

---

## Context

### The symptom

The screenshot shows the Bani Flow left panel with Raga: Kapi selected. The listening trail
shows the same performance listed multiple times — once for each matched musician node:

```
BANI FLOW ♩
[Filter trail…]

Raga: Kapi

◆ Vina Dhanammal          1867–1938
  Viruttam (Pasuram) — Kulam  45:08 ↗
  Tharum

● T. Brinda               1912–1996
  Parulanna Matta             15:48 ↗

● Semmangudi Srinivasa Iyer  1908–2…
  Parulanna Matta (Javali)  3:09:37 ↗

● TM Krishna               b. 1976
  Nee Matumme · Kapi - TM Krishna,
  Karnatic Modern II Mumbai 2018  00:00 ↗

■ Akkarai Subbulakshmi     b. None
  Nee Matumme · Kapi - TM Krishna,
  Karnatic Modern II Mumbai 2018  00:00 ↗

● TM Krishna               b. 1976
  Ni Matumme · Kapi - TM Krishna,
  Kolkata 2019                00:00 ↗

■ Akkarai Subbulakshmi     b. None
  Ni Matumme · Kapi - TM Krishna,
  Kolkata 2019                00:00 ↗

● TM Krishna               b. 1976
  Jagadodharana               00:00 ↗

■ Akkarai Subbulakshmi     b. None
  Jagadodharana               00:00 ↗

● TM Krishna               b. 1976
  Virutham + Poonguyil Koovum
  Poonjolayil · Kapi - TM Krishna &
  Akkarai Subbulakshmi, Parallel
  Lines Bangalore 2020        00:00 ↗

■ Akkarai Subbulakshmi     b. None
  Virutham + Poonguyil Koovum…  00:00 ↗
```

TM Krishna and Akkarai Subbulakshmi appear as **separate rows for the same performance**,
doubling every entry in the trail. The rasika sees N×M rows instead of N rows, where M is
the number of matched musicians who share the same recording.

### Root cause in the code

[`buildListeningTrail()`](../carnatic/render.py:2063) builds `rows` from two sources:

**Source 1 — legacy `youtube[]` entries (lines 2090–2105):**
The outer loop iterates `matchedNodeIds` — every musician node that matched the Bani Flow
filter. For each node, it iterates `d.tracks` (the node's `youtube[]` array). When two
musicians (TMK and Akkarai) both have the same video in their `youtube[]` arrays — same
`vid`, same `composition_id` — the loop emits **two rows** for the same performance.
There is no deduplication by `(vid, offset_seconds)`.

**Source 2 — structured recordings (lines 2107–2141):**
`compositionToPerf[id]` and `ragaToPerf[id]` are built in
[`build_recording_lookups()`](../carnatic/render.py:124). Each entry is one `PerformanceRef`
per performance (not per performer), so structured recordings do **not** duplicate. However,
the rendering loop at line 2113 picks only the `primaryPerformer` (vocal or first), discarding
all co-performers from the display. This means the rasika cannot see who else performed.

### The two distinct problems

| Problem | Source | Effect |
|---|---|---|
| **Duplication** | Legacy `youtube[]` entries shared across multiple nodes | N rows for 1 performance |
| **Co-performer invisibility** | Structured recordings show only primary performer | Co-performers hidden |

Both problems have the same structural fix: **group by performance identity, show co-performers
as a single bracketed entry**.

### Why this matters architecturally

The Bani Flow trail answers the question: *"Who has performed this composition/raga, and when?"*
The current rendering answers: *"Which matched nodes have this composition/raga in their
`youtube[]` array?"* — a fundamentally different (and weaker) question.

When TMK and Akkarai perform together, the tradition treats that as **one performance event**
with two principal artists. The trail should reflect this: one row, two names. The current
rendering treats it as two independent events — which is both factually wrong and visually
cluttered.

The duplication also breaks the rasika's ability to navigate: a trail of 10 unique performances
becomes a trail of 20 rows, making it twice as hard to scan and compare.

### Asymmetry with ADR-018

ADR-018 fixed the right panel (musician → concerts): one bracket per concert, compositions
inside. ADR-019 fixes the left panel (composition/raga → performances): one row per
performance, co-performers shown inline. These are the two axes of the tradition:

- **Right panel:** *event axis* — what did this musician perform, and where?
- **Left panel:** *music axis* — who has performed this composition/raga, and when?

Both axes must show co-performers. Both must avoid duplication. The fix is symmetric in
intent, though different in visual form: the right panel uses collapsible brackets (many
compositions per concert); the left panel uses inline co-performer display (many performers
per performance row).

---

## Forces in tension

1. **Fidelity to the oral tradition** — A duet is one performance, not two. The tradition
   does not separate TMK's contribution from Akkarai's in the same concert. The trail must
   honour this unity.

2. **Navigability** — The rasika must be able to click a row to play the performance, and
   click an artist name to select that node in the graph. Both affordances must survive the
   grouping.

3. **Discoverability** — The rasika must be able to see at a glance who performed together.
   Co-performer names must be visible without expanding anything — the trail is already a
   flat list, not a hierarchy.

4. **Scalability** — As more recordings are added, the trail will grow. Deduplication by
   performance identity is the only structure that keeps the trail readable.

5. **Symmetry with ADR-018** — The left and right panels must use the same conceptual model:
   performance events are the primary unit; musicians are attributes of those events.

6. **Legacy compatibility** — The `youtube[]` entries in `musicians.json` are the primary
   data source for most musicians. The fix must work for both legacy and structured recordings.

7. **Sort stability** — The current sort (year → born → label) must be preserved for the
   deduplicated rows. When multiple musicians share a row, the sort key is the earliest
   `born` among the co-performers (or the primary performer's `born`).

---

## Pattern

### **Strong Centres** (Alexander, Pattern 1)

A performance is a **strong centre** — a bounded, historically significant event with its
own identity: composition, raga, date, performers. The current rendering treats each
musician's `youtube[]` entry as an independent centre, which destroys the performance's
identity as a whole.

The fix restores the performance as the primary centre. Each performance gets **one row**
in the trail. The musicians are attributes of that row — co-performers shown inline,
each clickable to navigate to their node.

### **Levels of Scale** (Alexander, Pattern 5)

The Bani Flow trail has two natural levels of scale:

```
Level 1: The composition or raga (selected in the search box)
Level 2: The performance (one row — date, co-performers, composition title, timestamp)
```

The current rendering collapses the performance level by duplicating it once per musician.
The fix restores the correct two-level structure.

### **Boundaries** (Alexander, Pattern 101)

The performance row is a **boundary** — it separates one performance event from another.
Without deduplication, the boundary is blurred: the rasika cannot tell whether two adjacent
rows are two different performances or two musicians in the same performance.

### **Gradients** (Alexander, Pattern 9)

The trail is already a gradient of disclosure: the rasika sees the artist name and date
first, then the composition title and timestamp. The fix extends this gradient: the rasika
sees the **primary artist** first (bold, with shape icon), then the **co-performers** inline
(smaller, muted), then the composition and timestamp. Broad context first, detail inline.

---

## Decision

### The deduplication model: group by performance identity

**Performance identity** is defined as `(vid, offset_seconds)` for legacy tracks, and
`(recording_id, session_index, performance_index)` for structured recordings.

Two rows with the same performance identity are the **same performance**. They must be
merged into one row with a combined co-performer list.

### Grouping logic

**Step 1 — Collect all rows as before** (legacy + structured), but tag each with its
performance identity key.

**Step 2 — Group by performance identity key:**

```javascript
const perfMap = new Map(); // key → { primaryRow, coPerformers[] }

rows.forEach(row => {
  const key = row.isStructured
    ? `${row.recording_id}::${row.session_index}::${row.performance_index}`
    : `${row.track.vid}::${row.track.offset_seconds}`;

  if (!perfMap.has(key)) {
    perfMap.set(key, { primary: row, coPerformers: [] });
  } else {
    // Merge: add this musician as a co-performer of the existing row
    perfMap.get(key).coPerformers.push({
      nodeId:      row.nodeId,
      artistLabel: row.artistLabel,
      color:       row.color,
      shape:       row.shape,
    });
  }
});
```

**Step 3 — For structured recordings**, the `performers[]` array on the `PerformanceRef`
already contains all co-performers. Use it directly instead of relying on the node-iteration
loop. The primary performer is the vocal (or first); all others are co-performers.

**Step 4 — Sort the deduplicated rows** by `(year, born, artistLabel)` as before.

**Step 5 — Render one `<li>` per deduplicated row**, with co-performers shown inline.

### Visual structure — before and after

#### Before (current — duplicated rows)

```
┌─────────────────────────────────────────────┐
│ Raga: Kapi                                  │
│                                             │
│ ◆ TM Krishna               b. 1976          │
│   Nee Matumme · Kapi - TM Krishna,          │
│   Karnatic Modern II Mumbai 2018  00:00 ↗   │
│                                             │
│ ■ Akkarai Subbulakshmi     b. None          │
│   Nee Matumme · Kapi - TM Krishna,          │
│   Karnatic Modern II Mumbai 2018  00:00 ↗   │
│                                             │
│ ◆ TM Krishna               b. 1976          │
│   Ni Matumme · Kapi - TM Krishna,           │
│   Kolkata 2019              00:00 ↗          │
│                                             │
│ ■ Akkarai Subbulakshmi     b. None          │
│   Ni Matumme · Kapi - TM Krishna,           │
│   Kolkata 2019              00:00 ↗          │
└─────────────────────────────────────────────┘
```

#### After (deduplicated — one row per performance, co-performers inline)

```
┌─────────────────────────────────────────────┐
│ Raga: Kapi                                  │
│                                             │
│ ◆ TM Krishna  ■ Akkarai Subbulakshmi  2018  │
│   Nee Matumme                  00:00 ↗      │
│   Karnatic Modern II Mumbai 2018            │
│                                             │
│ ◆ TM Krishna  ■ Akkarai Subbulakshmi  2019  │
│   Ni Matumme                   00:00 ↗      │
│   Kolkata 2019                              │
│                                             │
│ ◆ TM Krishna  ■ Akkarai Subbulakshmi  2020  │
│   Virutham + Poonguyil Koovum  00:00 ↗      │
│   Parallel Lines Bangalore 2020             │
│                                             │
│ ◆ TM Krishna                          —     │
│   Jagadodharana                00:00 ↗      │
└─────────────────────────────────────────────┘
```

### HTML structure — revised `<li>` shape

```html
<!-- One <li> per deduplicated performance -->
<li class="trail-item" data-vid="XXXXXXXXXXX" data-offset="0">

  <!-- Row 1: artists + year -->
  <div class="trail-header">
    <!-- Primary artist (bold, with shape icon, clickable to select node) -->
    <span class="trail-artist trail-artist-primary" data-node-id="tm_krishna">
      <span class="trail-shape-icon ellipse" style="background:#83a598"></span>
      TM Krishna
    </span>
    <!-- Co-performers (muted, each clickable to select their node) -->
    <span class="trail-copeformers">
      <span class="trail-artist trail-artist-co" data-node-id="akkarai_subbulakshmi">
        <span class="trail-shape-icon rectangle" style="background:#d3869b"></span>
        Akkarai Subbulakshmi
      </span>
    </span>
    <!-- Year (right-aligned) -->
    <span class="trail-lifespan">2018</span>
  </div>

  <!-- Row 2: composition title + timestamp link -->
  <div class="trail-row2">
    <span class="trail-label">Nee Matumme</span>
    <a class="trail-link" href="…" target="_blank">00:00 ↗</a>
  </div>

  <!-- Row 3: context label (concert/event name) — only for legacy tracks -->
  <div class="trail-context">Karnatic Modern II Mumbai 2018</div>

</li>
```

### CSS additions

```css
/* ── co-performer display in trail ── */
.trail-coperformers {
  display: inline-flex; align-items: center; gap: 6px;
  flex-wrap: wrap;
}

.trail-artist-primary {
  font-weight: bold;
  color: var(--yellow);
}

.trail-artist-co {
  font-weight: normal;
  font-size: 0.72rem;
  color: var(--fg3);   /* muted — secondary to primary */
  cursor: pointer;
}
.trail-artist-co:hover { color: var(--yellow); text-decoration: underline; }

/* Context label (event/concert name for legacy tracks) */
.trail-context {
  font-size: 0.65rem;
  color: var(--gray);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

### Revised `buildListeningTrail` grouping logic (pseudocode)

```javascript
function buildListeningTrail(type, id, matchedNodeIds) {
  // ... (composer label unchanged) ...

  // ── 1. Collect raw rows (unchanged from current) ──────────────────────────
  const rawRows = [];

  // Legacy youtube[] entries
  matchedNodeIds.forEach(nid => {
    const d = cy.getElementById(nid).data();
    d.tracks.forEach(t => {
      if (/* matches type and id */) {
        rawRows.push({ nodeId: nid, artistLabel: d.label, born: d.born,
                       lifespan: d.lifespan, color: d.color, shape: d.shape,
                       track: t, isStructured: false,
                       perfKey: `${t.vid}::${t.offset_seconds || 0}` });
      }
    });
  });

  // Structured recordings
  const structuredPerfs = type === 'comp'
    ? (compositionToPerf[id] || [])
    : (ragaToPerf[id] || []);

  structuredPerfs.forEach(p => {
    const primaryPerformer = p.performers.find(pf => pf.role === 'vocal') || p.performers[0];
    // ... resolve artistLabel, nodeId, born, pNode as before ...
    rawRows.push({
      nodeId, artistLabel, born, lifespan, color, shape,
      track: { vid: p.video_id, label: p.display_title,
               year: p.date ? parseInt(p.date) : null,
               offset_seconds: p.offset_seconds },
      isStructured: true,
      perfKey: `${p.recording_id}::${p.session_index}::${p.performance_index}`,
      // Carry full performers list for co-performer display
      allPerformers: p.performers,
      recording_id: p.recording_id,
      session_index: p.session_index,
      performance_index: p.performance_index,
    });
  });

  // ── 2. Deduplicate by perfKey ─────────────────────────────────────────────
  const perfMap = new Map(); // perfKey → merged row

  rawRows.forEach(row => {
    if (!perfMap.has(row.perfKey)) {
      perfMap.set(row.perfKey, {
        ...row,
        coPerformers: [],  // additional performers beyond primary
      });
    } else {
      const existing = perfMap.get(row.perfKey);
      // Add this musician as a co-performer if not already present
      const alreadyPresent = existing.nodeId === row.nodeId ||
        existing.coPerformers.some(cp => cp.nodeId === row.nodeId);
      if (!alreadyPresent) {
        existing.coPerformers.push({
          nodeId:      row.nodeId,
          artistLabel: row.artistLabel,
          color:       row.color,
          shape:       row.shape,
        });
      }
    }
  });

  // For structured recordings: populate coPerformers from performers[] directly
  // (more reliable than relying on node-iteration order)
  perfMap.forEach(row => {
    if (row.isStructured && row.allPerformers) {
      row.coPerformers = [];
      row.allPerformers.forEach(pf => {
        if (pf.musician_id === row.nodeId) return; // skip primary
        const coNode = pf.musician_id ? cy.getElementById(pf.musician_id) : null;
        row.coPerformers.push({
          nodeId:      pf.musician_id || null,
          artistLabel: coNode ? coNode.data('label') : (pf.unmatched_name || '?'),
          color:       coNode ? coNode.data('color') : null,
          shape:       coNode ? coNode.data('shape') : null,
        });
      });
    }
  });

  // ── 3. Sort deduplicated rows ─────────────────────────────────────────────
  const rows = [...perfMap.values()].sort((a, b) => {
    const ay = a.track.year, by = b.track.year;
    if (ay !== by) { if (ay == null) return 1; if (by == null) return -1; return ay - by; }
    const ab = a.born, bb = b.born;
    if (ab !== bb) { if (ab == null) return 1; if (bb == null) return -1; return ab - bb; }
    return a.artistLabel.localeCompare(b.artistLabel);
  });

  // ── 4. Render one <li> per deduplicated row ───────────────────────────────
  rows.forEach(row => {
    const li = buildTrailItem(row);
    trailList.appendChild(li);
  });

  trail.style.display = rows.length > 0 ? 'block' : 'none';
}
```

### `buildTrailItem` helper (new function)

```javascript
function buildTrailItem(row) {
  const li = document.createElement('li');
  li.dataset.vid = row.track.vid;
  li.className   = playerRegistry.has(row.track.vid) ? 'playing' : '';
  li.addEventListener('click', () =>
    openOrFocusPlayer(row.track.vid, row.track.label, row.artistLabel,
                      row.isStructured ? row.track.offset_seconds : undefined));

  // ── Row 1: artists + year ──────────────────────────────────────────────
  const headerDiv = document.createElement('div');
  headerDiv.className = 'trail-header';

  // Primary artist
  const primarySpan = buildArtistSpan(row, /* isPrimary */ true);
  headerDiv.appendChild(primarySpan);

  // Co-performers
  if (row.coPerformers && row.coPerformers.length > 0) {
    const coDiv = document.createElement('span');
    coDiv.className = 'trail-coperformers';
    row.coPerformers.forEach(cp => {
      coDiv.appendChild(buildArtistSpan(cp, /* isPrimary */ false));
    });
    headerDiv.appendChild(coDiv);
  }

  // Year / lifespan
  const lifespanSpan = document.createElement('span');
  lifespanSpan.className = 'trail-lifespan';
  lifespanSpan.textContent = row.lifespan || (row.track.year ? String(row.track.year) : '');
  headerDiv.appendChild(lifespanSpan);

  // ── Row 2: composition title + timestamp link ──────────────────────────
  let compTitle = row.track.label;
  if (!row.isStructured && row.track.composition_id) {
    const comp = compositions.find(c => c.id === row.track.composition_id);
    if (comp) compTitle = comp.title;
  }

  const labelSpan = document.createElement('span');
  labelSpan.className = 'trail-label';
  labelSpan.textContent = compTitle;

  const offsetSecs = row.isStructured ? row.track.offset_seconds : 0;
  const linkA = document.createElement('a');
  linkA.className = 'trail-link';
  linkA.href = ytDirectUrl(row.track.vid, offsetSecs || undefined);
  linkA.target = '_blank';
  linkA.textContent = offsetSecs > 0 ? `${formatTimestamp(offsetSecs)} ↗` : '00:00 ↗';
  linkA.addEventListener('click', e => e.stopPropagation());

  const row2Div = document.createElement('div');
  row2Div.className = 'trail-row2';
  row2Div.appendChild(labelSpan);
  row2Div.appendChild(linkA);

  li.appendChild(headerDiv);
  li.appendChild(row2Div);
  return li;
}

function buildArtistSpan(row, isPrimary) {
  const span = document.createElement('span');
  span.className = isPrimary
    ? 'trail-artist trail-artist-primary'
    : 'trail-artist trail-artist-co';

  if (row.color || row.shape) {
    const icon = document.createElement('span');
    icon.className = `trail-shape-icon ${row.shape || 'ellipse'}`;
    if ((row.shape || 'ellipse') === 'triangle') {
      icon.style.borderBottomColor = row.color || 'var(--gray)';
    } else {
      icon.style.background = row.color || 'var(--gray)';
    }
    span.appendChild(icon);
  }

  span.appendChild(document.createTextNode(row.artistLabel));

  if (row.nodeId) {
    span.addEventListener('click', e => {
      e.stopPropagation();
      cy.elements().removeClass('faded highlighted bani-match');
      applyBaniFilter(type, id);
      const n = cy.getElementById(row.nodeId);
      if (n && n.length) selectNode(n);
    });
  }

  return span;
}
```

### Filter bar behaviour with deduplicated rows

The existing `trail-filter` input filters by artist name and composition title. With
deduplicated rows, the filter must also match **co-performer names**:

```javascript
document.getElementById('trail-filter').addEventListener('input', function() {
  const q = this.value.toLowerCase().trim();
  trailList.querySelectorAll('li:not(.trail-no-match)').forEach(li => {
    if (!q) { li.style.display = 'flex'; return; }
    // Match primary artist
    const primaryText = (li.querySelector('.trail-artist-primary') || {}).textContent || '';
    // Match co-performers
    const coTexts = [...li.querySelectorAll('.trail-artist-co')]
      .map(el => el.textContent).join(' ');
    // Match composition title
    const labelText = (li.querySelector('.trail-label') || {}).textContent || '';
    const matches = [primaryText, coTexts, labelText]
      .some(t => t.toLowerCase().includes(q));
    li.style.display = matches ? 'flex' : 'none';
  });
  // ... no-match message logic unchanged ...
});
```

---

## Before / After JSON shape

No data schema change is required. The `PerformanceRef` shape in `compositionToPerf` and
`ragaToPerf` already carries `performers[]` with all co-performers. The `youtube[]` entries
in `musicians.json` are unchanged. The change is entirely in the rendering layer.

### PerformanceRef (unchanged — already carries full performers list)

```json
{
  "recording_id":      "music_academy_1966_semmangudi",
  "video_id":          "XXXXXXXXXXX",
  "title":             "Music Academy December Season 1966 — Semmangudi Srinivasa Iyer",
  "short_title":       "Music Academy 1966",
  "date":              "1966-12",
  "session_index":     1,
  "performance_index": 3,
  "timestamp":         "00:45:00",
  "offset_seconds":    2700,
  "display_title":     "Parulanna Matta",
  "composition_id":    "parulanna_matta",
  "raga_id":           "kapi",
  "tala":              "adi",
  "composer_id":       "tyagaraja",
  "notes":             null,
  "type":              null,
  "performers": [
    { "musician_id": "semmangudi_srinivasa_iyer", "role": "vocal" },
    { "musician_id": "lalgudi_jayaraman",         "role": "violin" },
    { "musician_id": null, "role": "mridangam",   "unmatched_name": "Umayalpuram Sivaraman" }
  ]
}
```

### Legacy youtube[] entry (unchanged)

```json
{
  "url":            "https://youtu.be/XXXXXXXXXXX",
  "label":          "Nee Matumme · Kapi - TM Krishna, Karnatic Modern II Mumbai 2018",
  "composition_id": "nee_matumme",
  "raga_id":        "kapi",
  "year":           2018
}
```

The deduplication key for this entry is `vid::offset_seconds` = `XXXXXXXXXXX::0`.
When both TMK and Akkarai have this entry, the second occurrence is merged into the first
as a co-performer, not emitted as a separate row.

---

## Consequences

### Queries this enables

| Rasika query | Before | After |
|---|---|---|
| "Who has performed Nee Matumme in Kapi?" | Two rows: TMK and Akkarai separately | One row: TMK + Akkarai together |
| "Did TMK and Akkarai perform together?" | Visible only by noticing duplicate rows | Explicit: co-performer names shown inline |
| "How many distinct performances of this raga exist?" | Count ÷ 2 (or ÷ N for N co-performers) | Count directly — one row per performance |
| "I want to filter by Akkarai" | Type "Akkarai" — shows her rows only, loses TMK context | Type "Akkarai" — shows all rows where she appears, with TMK visible as co-performer |
| "Who performed Kapi at the Music Academy 1966?" | Primary performer only (Semmangudi) | Semmangudi + Lalgudi + Umayalpuram Sivaraman all visible |

### What this enables beyond the current data

- **Co-performer navigation from the trail** — clicking a co-performer name selects their
  node in the graph, just as clicking the primary artist does. This makes the trail a
  navigation surface for the entire ensemble, not just the lead artist.
- **Ensemble discovery** — the rasika can see at a glance which musicians habitually
  performed together in a given raga or composition. This is a new query that was
  previously impossible without opening each recording separately.
- **Accurate performance count** — the trail header can show "N performances" where N is
  the true count of distinct events, not the inflated count of musician-event pairs.

### What this forecloses

- **Per-musician filtering in the trail** — the current behaviour (selecting a node in the
  graph highlights only that node's rows in the trail) will need to be updated. When rows
  are deduplicated, a row belongs to multiple musicians. The highlight logic must be updated
  to highlight a row if **any** of its performers (primary or co-) matches the selected node.
  This is a rendering fix, not a schema change.

### Interaction with ADR-018 (right panel concert brackets)

ADR-018 and ADR-019 are symmetric fixes:
- ADR-018: right panel groups by concert (event axis) — one bracket per concert, compositions inside
- ADR-019: left panel deduplicates by performance (music axis) — one row per performance, co-performers inline

Together they establish the principle: **the performance event is the primary unit of
display in both panels**. Musicians are attributes of events, not the other way around.

### Interaction with ADR-011 (left-right sidebar symmetry)

ADR-011 established that the left panel groups by composition and the right panel groups
by concert. ADR-019 refines the left panel's grouping: within a composition/raga, entries
are grouped by **performance event** (deduplicated), not by musician. This is the correct
refinement of ADR-011's intent.

### Interaction with ADR-012 (same-concert track switching)

ADR-012 established that clicking a second track from the same concert updates the existing
player window. This behaviour is unchanged: the `vid` on each deduplicated row is the same
as before; the player registry lookup by `vid` continues to work correctly.

---

## CLI queries — rasika queries must be answerable at the command line

The deduplication logic must also be reflected in the CLI. The existing
`python3 carnatic/cli.py bani-flow <composition_id>` command (if present) must return
deduplicated entries — one dict per performance event, with a `co_performers` list — not
one dict per musician.

### Gap analysis against current CLI

| Rasika query | Current CLI support | Gap |
|---|---|---|
| "Who has performed Nee Matumme in Kapi?" | `bani-flow nee_matumme` — returns one entry per musician | ✗ Duplicates; no co-performer grouping |
| "Who performed together in this raga?" | No command | ✗ Missing |
| "How many distinct performances of this composition exist?" | Count of `bani-flow` entries ÷ N co-performers | ✗ Inflated count |

### Required change to `get_bani_flow` in `graph_api.py`

The [`get_bani_flow()`](../carnatic/graph_api.py:336) method must be updated to return
**deduplicated** entries. The deduplication key is `(video_id, offset_seconds)` for legacy
entries and `(recording_id, session_index, performance_index)` for structured entries.

Each returned dict gains a `co_performers` field:

```python
{
  "recording_id":      "music_academy_1966_semmangudi",
  "video_id":          "XXXXXXXXXXX",
  "title":             "Music Academy December Season 1966",
  "short_title":       "Music Academy 1966",
  "date":              "1966-12",
  "session_index":     1,
  "performance_index": 3,
  "timestamp":         "00:45:00",
  "offset_seconds":    2700,
  "display_title":     "Parulanna Matta",
  "composition_id":    "parulanna_matta",
  "raga_id":           "kapi",
  "tala":              "adi",
  "composer_id":       "tyagaraja",
  "notes":             null,
  "type":              null,
  "performers": [
    { "musician_id": "semmangudi_srinivasa_iyer", "role": "vocal" },
    { "musician_id": "lalgudi_jayaraman",         "role": "violin" },
    { "musician_id": null, "role": "mridangam",   "unmatched_name": "Umayalpuram Sivaraman" }
  ],
  "co_performers": [
    { "musician_id": "lalgudi_jayaraman",  "label": "Lalgudi Jayaraman",    "role": "violin" },
    { "musician_id": null,                 "label": "Umayalpuram Sivaraman","role": "mridangam" }
  ]
}
```

The `co_performers` field is the `performers[]` list minus the primary performer (vocal or
first). For legacy `youtube[]` entries, `co_performers` is populated by merging duplicate
entries that share the same `(video_id, offset_seconds)` key.

### Deduplication pseudocode for `get_bani_flow`

```python
def get_bani_flow(self, composition_id: str) -> list[dict]:
    raw_refs: list[dict] = []

    # Structured recordings (unchanged collection logic)
    for rec in self._all_recordings_loaded():
        for session in rec.get("sessions", []):
            performers = session.get("performers", [])
            for perf in session.get("performances", []):
                if perf.get("composition_id") == composition_id:
                    ref = self._make_perf_ref(rec, session, perf, performers)
                    ref["_perf_key"] = f"{ref['recording_id']}::{ref['session_index']}::{ref['performance_index']}"
                    raw_refs.append(ref)

    # Legacy youtube[] entries
    for node in self._musician_nodes:
        for yt in node.get("youtube", []):
            if yt.get("composition_id") == composition_id:
                vid = self._yt_video_id(yt.get("url", ""))
                offset = 0
                ref = { ... }  # existing shape
                ref["_perf_key"] = f"{vid}::{offset}"
                raw_refs.append(ref)

    # Deduplicate by _perf_key
    seen: dict[str, dict] = {}
    for ref in raw_refs:
        key = ref["_perf_key"]
        if key not in seen:
            seen[key] = ref
        else:
            # Merge: add this performer to co_performers of existing entry
            existing = seen[key]
            existing.setdefault("co_performers", [])
            for pf in ref.get("performers", []):
                mid = pf.get("musician_id")
                already = any(
                    cp.get("musician_id") == mid
                    for cp in existing["co_performers"]
                )
                if not already and mid != existing.get("_primary_musician_id"):
                    node_label = self._musician_by_id.get(mid, {}).get("label") if mid else None
                    existing["co_performers"].append({
                        "musician_id": mid,
                        "label":       node_label or pf.get("unmatched_name", "?"),
                        "role":        pf.get("role"),
                    })

    # Remove internal keys before returning
    result = []
    for ref in seen.values():
        ref.pop("_perf_key", None)
        ref.pop("_primary_musician_id", None)
        result.append(ref)

    # Sort chronologically
    return sorted(result, key=lambda r: r.get("date") or "9999")
```

---

## Implementation

**Agent:** Carnatic Coder
**Files:**
- [`carnatic/render.py`](../carnatic/render.py) — JavaScript and CSS changes:
  - Deduplication logic in `buildListeningTrail()`
  - New `buildTrailItem()` helper function
  - New `buildArtistSpan()` helper function
  - CSS additions for `.trail-artist-primary`, `.trail-artist-co`, `.trail-coperformers`, `.trail-context`
  - Updated `trail-filter` event listener to match co-performer names
- [`carnatic/graph_api.py`](../carnatic/graph_api.py) — Update `get_bani_flow()` to return deduplicated entries with `co_performers` field

**No data schema changes.** All required fields (`performers[]`, `video_id`, `offset_seconds`,
`recording_id`, `session_index`, `performance_index`) are already present in the
`PerformanceRef` shape and in the `youtube[]` entries.

**Verification:**

```bash
# UI: open graph, select Raga: Kapi in Bani Flow
# → trail shows one row for "Nee Matumme" (not two)
# → TMK and Akkarai both visible in the same row
# → clicking TMK name selects TMK node; clicking Akkarai name selects Akkarai node
# → clicking the row plays the video

# UI: type "Akkarai" in trail filter
# → all rows where Akkarai appears are shown (including rows where TMK is primary)
# → rows where Akkarai does not appear are hidden

# CLI:
python3 carnatic/graph_api.py --bani-flow nee_matumme
# → one entry, with co_performers: [{ musician_id: "akkarai_subbulakshmi", ... }]

python3 carnatic/graph_api.py --bani-flow parulanna_matta
# → one entry for Music Academy 1966, with co_performers: Lalgudi + Umayalpuram
```
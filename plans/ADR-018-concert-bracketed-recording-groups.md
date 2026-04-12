# ADR-018: Concert-Bracketed Recording Groups in the Musician Panel

**Status:** Proposed  
**Date:** 2026-04-12

---

## Context

### The symptom

The screenshot shows Ramnad Krishnan's right-sidebar recording list. Twelve compositions appear as twelve undifferentiated rows:

```
RECORDINGS
Bālē Bālēndu Bhūṣaṇi
Reetigowla
Poonamallee 1965                00:00 ↗

Abhimānamennedu
Begada
Poonamallee 1965                4:00 ↗

Bhajana Parulakēla
Surutti
Poonamallee 1965               16:50 ↗

Śrī Māninī Manōhara
Poorna Shadjam
Poonamallee 1965               27:34 ↗

Yagnadulu Sukhamanu
Jayamanohari
Wesleyan 1967                  00:00 ↗

Enduku Nirdaya
Harikambhoji
Wesleyan 1967                  10:56 ↗

Bantureeti Kolu
Hamsanadam
Wesleyan 1967                  33:42 ↗
…
```

The user's diagnosis is exact: *"We are losing the significance of the concert recording here. For being a special collection, being flattened like this does the momentous occasions injustice."*

### Why this matters architecturally

The Poonamallee 1965 concert is not twelve compositions. It is **one event** — a celebration of the Sangita Kalanidhi conferment on Alathur Sivasubramania Iyer — at which eight of the most significant musicians of the golden age performed together in eight distinct sessions. The Wesleyan 1967 concert is **one event** — Ramnad Krishnan and T. Viswanathan performing for Wesleyan University students, a landmark in the transmission of the tradition to the West.

When these events are flattened into a list of compositions, the rasika loses:

1. **The occasion** — why this concert happened, what it commemorated
2. **The co-performers** — who played alongside the selected musician in each session
3. **The session structure** — which compositions belong to the same continuous performance block
4. **The concert as a centre** — the sense that this was a singular, unrepeatable gathering

The current rendering treats the concert as a *container for compositions*. The tradition treats the concert as a *living event* in which compositions are moments.

### Root cause in the code

[`buildRecordingsList()`](../carnatic/render.py:1334) receives `structuredPerfs` from `musicianToPerformances[nodeId]` — a flat array of `PerformanceRef` objects. Each `PerformanceRef` carries `recording_id`, `short_title`, `session_index`, `performers[]`, `date`, `title` (full concert title), and `occasion`. But the rendering loop at line 1394 discards all grouping information and emits one `<li>` per composition.

The data is already correct and complete. The `PerformanceRef` shape (built in [`build_recording_lookups()`](../carnatic/render.py:124)) carries everything needed to reconstruct the concert bracket. The problem is entirely in the rendering layer.

### The asymmetry with the left panel

ADR-011 established that the left panel (Bani Flow) and right panel (Musician) should be symmetric in structure and behaviour. The left panel correctly groups recordings by composition — the rasika sees all performances of a raga together. The right panel should group recordings by concert — the rasika sees all compositions of a concert together. These are the two natural axes of the tradition: *what was played* (left) and *where and when it was played* (right).

Flattening in the right panel breaks this symmetry at the level of meaning, not just visual structure.

---

## Forces in tension

1. **Immersion** — The rasika must be able to lose themselves in a concert as a whole, not just navigate individual compositions. The concert bracket is the container of immersion.

2. **Significance** — The Poonamallee 1965 and Wesleyan 1967 concerts are historically significant events. Their significance is communicated by the occasion, the co-performers, and the session structure — none of which is visible in the current flat list.

3. **Navigability** — The rasika must still be able to click individual compositions to play them at the correct timestamp. The bracket must not obstruct navigation.

4. **Discoverability** — A long concert (8 compositions) should not dominate the panel when collapsed. The rasika must be able to see at a glance how many concerts exist and expand only the ones they want.

5. **Scalability** — As more structured recordings are added, the flat list will grow to 30, 50, 100 items. Grouping by concert is the only structure that scales without becoming unreadable.

6. **Left-panel symmetry** — The left panel groups by composition; the right panel must group by concert. Both panels must support the same two-level interaction: (1) select a group, (2) navigate within it.

7. **Co-performer visibility** — The musician panel is where the rasika learns *when and where musicians played together*. This information is in `performers[]` on every `PerformanceRef` but is currently invisible.

---

## Pattern

### **Strong Centres** (Alexander, Pattern 1)

A concert recording is a **strong centre** — a bounded, historically significant event with its own identity, occasion, performers, and internal structure. The compositions within it are sub-centres, not independent centres. The current flat list treats each composition as an independent centre, which destroys the concert's identity as a whole.

The fix restores the concert as the primary centre. Each concert gets a **bracket** — a header that names the event, shows the date, and lists the co-performers. The compositions are sub-centres within the bracket, navigable but subordinate.

### **Levels of Scale** (Alexander, Pattern 5)

The tradition has three natural levels of scale in the right panel:

```
Level 1: The musician (selected node)
Level 2: The concert (recording event — occasion, date, venue, co-performers)
Level 3: The composition (individual performance — raga, tala, timestamp)
```

The current rendering collapses levels 2 and 3 into a single flat list. The fix restores all three levels, each with its own visual weight and interaction affordance.

### **Boundaries** (Alexander, Pattern 101)

The concert bracket is a **boundary** — it separates one concert from another, and separates the concert header (level 2) from the composition list (level 3). Without this boundary, the rasika cannot tell where one concert ends and another begins. The boundary is not decorative; it is the structural element that makes the concert a legible unit.

### **Gradients** (Alexander, Pattern 9)

The transition from collapsed (concert header only) to expanded (concert header + composition list) is a **gradient** of disclosure. The rasika sees the concert's identity first (name, date, co-performers), then chooses to expand it to see the compositions. This is the correct gradient: broad context first, detail on demand.

---

## Decision

### The rendering model: concert brackets with collapsible composition lists

Replace the flat `<li>` per composition with a **two-level structure**:

```
Level 2: Concert bracket (always visible, collapsed by default)
  ├── Concert title + date                    [▶ expand button]
  ├── Co-performers (comma-separated names)
  └── [Collapsed: composition count shown]

Level 3: Composition list (visible when expanded)
  ├── Composition 1: title · raga · tala      timestamp ↗
  ├── Composition 2: title · raga · tala      timestamp ↗
  └── …
```

### Grouping logic

**Group by `recording_id` first, then by `session_index` within the recording.**

For a musician who appears in multiple sessions of the same concert (e.g. Semmangudi Srinivasa Iyer appears in sessions 2, 3, and 4 of Poonamallee 1965), the bracket shows the full concert once, with only the sessions in which the selected musician appears.

**Sort order:**
- Concerts: chronological by `date` (ascending; nulls last)
- Sessions within a concert: by `session_index` (ascending)
- Compositions within a session: by `offset_seconds` (ascending — concert order)

Legacy `youtube[]` tracks (non-structured) remain as flat `<li>` items, sorted chronologically by `year`, appearing after all structured concert brackets. They are not bracketed because they lack the session/performer structure.

### Visual structure — before and after

#### Before (current flat list)

```
┌─────────────────────────────────────────┐
│ RECORDINGS                              │
│                                         │
│ Bālē Bālēndu Bhūṣaṇi                   │
│ Reetigowla                              │
│ Poonamallee 1965              00:00 ↗  │
│                                         │
│ Abhimānamennedu                         │
│ Begada                                  │
│ Poonamallee 1965               4:00 ↗  │
│                                         │
│ Bhajana Parulakēla                      │
│ Surutti                                 │
│ Poonamallee 1965              16:50 ↗  │
│                                         │
│ Śrī Māninī Manōhara                     │
│ Poorna Shadjam                          │
│ Poonamallee 1965              27:34 ↗  │
│                                         │
│ Yagnadulu Sukhamanu                     │
│ Jayamanohari                            │
│ Wesleyan 1967                 00:00 ↗  │
│                                         │
│ Enduku Nirdaya                          │
│ Harikambhoji                            │
│ Wesleyan 1967                 10:56 ↗  │
│ …                                       │
└─────────────────────────────────────────┘
```

#### After (concert-bracketed, collapsed by default)

```
┌─────────────────────────────────────────┐
│ RECORDINGS                              │
│                                         │
│ ▶ Poonamallee 1965            Jan 1965  │
│   Ramnad Krishnan, T.N. Krishnan,       │
│   Vellore Ramabhadran  · 4 pieces       │
│                                         │
│ ▶ Wesleyan University 1967       1967   │
│   Ramnad Krishnan, T. Viswanathan,      │
│   V. Tyagarajan, T. Ranganathan · 8 pcs │
│                                         │
└─────────────────────────────────────────┘
```

#### After (Wesleyan 1967 expanded)

```
┌─────────────────────────────────────────┐
│ RECORDINGS                              │
│                                         │
│ ▶ Poonamallee 1965            Jan 1965  │
│   Ramnad Krishnan, T.N. Krishnan,       │
│   Vellore Ramabhadran  · 4 pieces       │
│                                         │
│ ▼ Wesleyan University 1967       1967   │  ← expanded
│   Ramnad Krishnan, T. Viswanathan,      │
│   V. Tyagarajan, T. Ranganathan         │
│   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄  │
│   Yagnadulu Sukhamanu                   │
│   Jayamanohari · Adi          00:00 ↗  │
│                                         │
│   Enduku Nirdaya                        │
│   Harikambhoji · Adi          10:56 ↗  │
│                                         │
│   Bantureeti Kolu                       │
│   Hamsanadam · Deshadi        33:42 ↗  │
│                                         │
│   Kaligiyunte                           │
│   Keeravani · Adi             44:41 ↗  │
│                                         │
│   Samayamide Rara                       │
│   Behag · Rupakam           1:24:04 ↗  │
│                                         │
│   Janathi Ramam — Ragamalika            │
│   Saveri · Sahana · Surutti  1:34:27 ↗ │
│                                         │
│   Ni Nama Roopamulaku                   │
│   Sowrashtram · Adi          1:54:33 ↗  │
│                                         │
└─────────────────────────────────────────┘
```

### Data shape — what the renderer needs

The `PerformanceRef` objects in `musicianToPerformances` already carry all required fields. No data schema change is needed. The renderer must group them client-side:

```javascript
// Group structuredPerfs by recording_id, then session_index
const concertMap = new Map(); // recording_id → { meta, sessions: Map<session_index → perfs[]> }

structuredPerfs.forEach(p => {
  if (!concertMap.has(p.recording_id)) {
    concertMap.set(p.recording_id, {
      recording_id: p.recording_id,
      title:        p.title,
      short_title:  p.short_title,
      date:         p.date,
      year:         p.date ? parseInt(p.date) : null,
      sessions:     new Map(),
    });
  }
  const concert = concertMap.get(p.recording_id);
  if (!concert.sessions.has(p.session_index)) {
    concert.sessions.set(p.session_index, {
      session_index: p.session_index,
      performers:    p.performers,   // PerformanceRef carries performers[]
      perfs:         [],
    });
  }
  concert.sessions.get(p.session_index).perfs.push(p);
});

// Sort concerts chronologically
const concerts = [...concertMap.values()].sort((a, b) => {
  if (a.year == null) return 1;
  if (b.year == null) return -1;
  return a.year - b.year;
});
```

### Co-performer display

For each concert bracket, show the **full performer list** from all sessions in which the selected musician appears. Deduplicate by `musician_id`. For matched musicians (`musician_id` not null), show the node `label` from the graph data. For unmatched musicians (`musician_id: null`), show `unmatched_name`. Exclude the selected musician themselves from the co-performer list.

```javascript
// Collect all performers across all sessions of this concert
const coPerformerSet = new Map(); // musician_id or unmatched_name → display label
concert.sessions.forEach(session => {
  session.performers.forEach(pf => {
    if (pf.musician_id === nodeId) return; // skip self
    const key   = pf.musician_id || ('_' + pf.unmatched_name);
    const label = pf.musician_id
      ? (cy.getElementById(pf.musician_id).data('label') || pf.musician_id)
      : (pf.unmatched_name || '?');
    coPerformerSet.set(key, label);
  });
});
const coPerformers = [...coPerformerSet.values()].join(', ');
```

### Expand/collapse interaction

- **Default state:** All concert brackets are **collapsed**. The header shows: concert title, date, co-performers (truncated to one line), and piece count.
- **Click the bracket header:** Toggle expanded/collapsed. The composition list slides in/out (CSS `max-height` transition or simple `display` toggle).
- **Click a composition row:** Play in the floating player at the correct `offset_seconds`. Does not collapse the bracket.
- **Click the `↗` link:** Open YouTube at the timestamp in a new tab. Does not collapse the bracket.
- **Expand button:** `▶` (collapsed) / `▼` (expanded) — a small chevron or triangle at the left edge of the bracket header.

### HTML structure

```html
<!-- Concert bracket (one per recording_id) -->
<div class="concert-bracket" data-recording-id="wesleyan_1967_ramnad_krishnan">

  <!-- Bracket header — always visible, click to toggle -->
  <div class="concert-header" onclick="toggleConcert(this)">
    <span class="concert-chevron">▶</span>
    <div class="concert-header-body">
      <div class="concert-title-row">
        <span class="concert-title">Wesleyan University 1967</span>
        <span class="concert-date">1967</span>
      </div>
      <div class="concert-performers">
        Ramnad Krishnan, T. Viswanathan, V. Tyagarajan, T. Ranganathan
      </div>
      <div class="concert-count">8 pieces</div>
    </div>
  </div>

  <!-- Composition list — hidden until expanded -->
  <ul class="concert-perf-list" style="display:none">
    <li class="concert-perf-item" data-vid="AnNb0zRmauM">
      <div class="rec-row1">
        <span class="rec-title">Yagnadulu Sukhamanu</span>
      </div>
      <div class="rec-row2">
        <span class="rec-meta">Jayamanohari · Adi</span>
        <a class="rec-link" href="…" target="_blank">00:00 ↗</a>
      </div>
    </li>
    <!-- … more compositions … -->
  </ul>

</div>
```

### CSS additions

```css
/* ── concert bracket ── */
.concert-bracket {
  border-bottom: 1px solid var(--bg2);
  padding: 0;
}
.concert-bracket:last-child { border-bottom: none; }

.concert-header {
  display: flex; align-items: flex-start; gap: 6px;
  padding: 6px 0; cursor: pointer;
}
.concert-header:hover .concert-title { color: var(--yellow); }

.concert-chevron {
  font-size: 0.60rem; color: var(--gray);
  flex-shrink: 0; margin-top: 3px; width: 10px; text-align: center;
  user-select: none;
}
.concert-bracket.expanded .concert-chevron::before { content: '▼'; }
.concert-bracket:not(.expanded) .concert-chevron::before { content: '▶'; }
/* hide the text node inside .concert-chevron when using ::before */
.concert-chevron { font-size: 0; }
.concert-chevron::before { font-size: 0.60rem; }

.concert-header-body { flex: 1; min-width: 0; }

.concert-title-row {
  display: flex; align-items: baseline; gap: 4px; width: 100%;
}
.concert-title {
  font-size: 0.78rem; font-weight: bold; color: var(--fg1);
  flex: 1; min-width: 0;
}
.concert-date {
  font-size: 0.68rem; color: var(--gray);
  flex-shrink: 0; margin-left: auto; padding-left: 6px;
}

.concert-performers {
  font-size: 0.68rem; color: var(--fg3);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  margin-top: 2px;
}
.concert-bracket.expanded .concert-performers {
  white-space: normal; /* show full list when expanded */
}

.concert-count {
  font-size: 0.65rem; color: var(--gray); margin-top: 2px;
}
.concert-bracket.expanded .concert-count { display: none; }

/* ── composition list inside bracket ── */
.concert-perf-list {
  list-style: none;
  padding-left: 16px; /* indent under chevron */
  margin-bottom: 4px;
}
.concert-perf-item {
  padding: 4px 0; border-bottom: 1px solid var(--bg2);
  cursor: pointer; display: flex; flex-direction: column; gap: 2px;
}
.concert-perf-item:last-child { border-bottom: none; }
.concert-perf-item:hover .rec-title { color: var(--yellow); }
.concert-perf-item.playing .rec-title { color: var(--aqua); }
```

### JavaScript additions

```javascript
// Toggle expand/collapse of a concert bracket
function toggleConcert(headerEl) {
  const bracket = headerEl.closest('.concert-bracket');
  const list    = bracket.querySelector('.concert-perf-list');
  const isOpen  = bracket.classList.contains('expanded');
  if (isOpen) {
    bracket.classList.remove('expanded');
    list.style.display = 'none';
  } else {
    bracket.classList.add('expanded');
    list.style.display = 'block';
  }
}
```

### Filter bar behaviour with brackets

The existing `rec-filter` input must be extended to work with the bracketed structure:

- Typing in the filter **expands all brackets** that contain at least one matching composition, and **hides** brackets with no matches.
- Within an expanded bracket, non-matching compositions are hidden.
- Clearing the filter **collapses all brackets** back to their default state.

```javascript
// Extended rec-filter logic (replaces current flat-list filter)
document.getElementById('rec-filter').addEventListener('input', function() {
  const q = this.value.toLowerCase().trim();

  // Handle concert brackets
  document.querySelectorAll('.concert-bracket').forEach(bracket => {
    const items = bracket.querySelectorAll('.concert-perf-item');
    let bracketHasMatch = false;

    items.forEach(li => {
      if (!q) {
        li.style.display = 'flex';
        bracketHasMatch = true;
        return;
      }
      const titleText = (li.querySelector('.rec-title') || {}).textContent || '';
      const metaText  = (li.querySelector('.rec-meta')  || {}).textContent || '';
      const matches   = titleText.toLowerCase().includes(q) ||
                        metaText.toLowerCase().includes(q);
      li.style.display = matches ? 'flex' : 'none';
      if (matches) bracketHasMatch = true;
    });

    if (!q) {
      // Reset: collapse all brackets
      bracket.style.display = 'block';
      bracket.classList.remove('expanded');
      bracket.querySelector('.concert-perf-list').style.display = 'none';
    } else if (bracketHasMatch) {
      // Expand brackets with matches
      bracket.style.display = 'block';
      bracket.classList.add('expanded');
      bracket.querySelector('.concert-perf-list').style.display = 'block';
    } else {
      // Hide brackets with no matches
      bracket.style.display = 'none';
    }
  });

  // Handle legacy flat items (unchanged)
  document.querySelectorAll('#recordings-list > li.rec-legacy').forEach(li => {
    if (!q) { li.style.display = 'flex'; return; }
    const titleText = (li.querySelector('.rec-title') || {}).textContent || '';
    const metaText  = (li.querySelector('.rec-meta')  || {}).textContent || '';
    li.style.display = (titleText.toLowerCase().includes(q) ||
                        metaText.toLowerCase().includes(q)) ? 'flex' : 'none';
  });
});
```

### Revised `buildRecordingsList` structure (pseudocode)

```javascript
function buildRecordingsList(nodeId, nodeData) {
  const recList = document.getElementById('recordings-list');
  recList.innerHTML = '';

  const nd = nodeData || cy.getElementById(nodeId).data();
  const legacyTracks    = nd.tracks || [];
  const structuredPerfs = musicianToPerformances[nodeId] || [];

  // ── 1. Build concert brackets from structured perfs ──────────────────────────
  const concertMap = new Map();
  structuredPerfs.forEach(p => { /* group by recording_id → session_index */ });
  const concerts = [...concertMap.values()].sort(/* by year */);

  concerts.forEach(concert => {
    const bracket = buildConcertBracket(concert, nodeId);
    recList.appendChild(bracket);
  });

  // ── 2. Append legacy tracks as flat items ────────────────────────────────────
  const sortedLegacy = legacyTracks.slice().sort(/* by year */);
  sortedLegacy.forEach(t => {
    const li = buildLegacyItem(t, nd.label);
    li.classList.add('rec-legacy');
    recList.appendChild(li);
  });

  // ── 3. Show/hide panel ───────────────────────────────────────────────────────
  const hasContent = concerts.length > 0 || legacyTracks.length > 0;
  document.getElementById('recordings-panel').style.display = hasContent ? 'block' : 'none';
  document.getElementById('rec-filter').style.display       = hasContent ? 'block' : 'none';
}
```

---

## Before / After JSON shape

No data schema change is required. The `PerformanceRef` shape in `musicianToPerformances` already carries all needed fields. The change is entirely in the rendering layer.

### PerformanceRef (unchanged — already carries grouping fields)

```json
{
  "recording_id":      "wesleyan_1967_ramnad_krishnan",
  "video_id":          "AnNb0zRmauM",
  "title":             "Wesleyan University Concert, 1967 — Ramnad Krishnan & T. Viswanathan",
  "short_title":       "Wesleyan 1967",
  "date":              "1967",
  "session_index":     1,
  "performance_index": 2,
  "timestamp":         "00:10:56",
  "offset_seconds":    656,
  "display_title":     "Enduku Nirdaya",
  "composition_id":    "enduku_nirdaya",
  "raga_id":           "harikambhoji",
  "tala":              "adi",
  "composer_id":       "tyagaraja",
  "notes":             null,
  "type":              null,
  "performers": [
    { "musician_id": "ramnad_krishnan",  "role": "vocal" },
    { "musician_id": "t_viswanathan",    "role": "flute" },
    { "musician_id": null, "role": "violin",   "unmatched_name": "V. Tyagarajan" },
    { "musician_id": null, "role": "mridangam","unmatched_name": "T. Ranganathan" },
    { "musician_id": null, "role": "tampura",  "unmatched_name": "Jon B. Higgins" }
  ]
}
```

The `performers[]` array on every `PerformanceRef` is the key that makes co-performer display possible without any schema change.

---

## Consequences

### Queries this enables

| Rasika query | Before | After |
|---|---|---|
| "I've selected Ramnad Krishnan. What concerts did he give?" | Impossible — 12 undifferentiated rows | Two concert brackets: Poonamallee 1965 (4 pieces) and Wesleyan 1967 (8 pieces) |
| "Who played alongside Ramnad Krishnan at Wesleyan?" | Invisible | Co-performer line in bracket header: T. Viswanathan, V. Tyagarajan, T. Ranganathan |
| "What was the occasion for the Poonamallee 1965 concert?" | Invisible | Bracket header shows short_title; full occasion available on hover or in a future detail panel |
| "I want to hear the Wesleyan 1967 concert in order" | Must scroll and click 8 separate rows | Expand bracket → click first composition → same-concert track switching (ADR-012) handles the rest |
| "I want to find all recordings of Begada raga by Ramnad Krishnan" | Type "Begada" in filter — works but shows concert name as context | Type "Begada" in filter — bracket expands, non-Begada compositions hidden, concert context preserved |
| "I've selected Semmangudi. When did he play with Musiri?" | Invisible | Poonamallee 1965 bracket shows both names in co-performer line |

### What this enables beyond the current data

- **Occasion display** — The `occasion` field in the recording JSON (e.g. "Celebration of the conferment of the Sangita Kalanidhi award…") can be shown as a tooltip or expanded detail on the bracket header. This is a future enhancement; the field is already in the data.
- **Session sub-brackets** — For concerts with multiple sessions (e.g. Poonamallee 1965 has 8 sessions), a future enhancement could show session-level sub-brackets within the concert bracket. The current ADR groups all sessions of a concert into one bracket for simplicity.
- **Concert-level play button** — A future enhancement could add a "play from beginning" button on the bracket header that opens the concert video at `offset_seconds: 0`. The `video_id` is already in the bracket data.

### What this forecloses

- **Flat chronological sort across all compositions** — The current sort (year → offset_seconds) is replaced by concert grouping. Within a concert, compositions are in concert order (by `offset_seconds`). Across concerts, concerts are in chronological order. The rasika can no longer see all compositions of a given year in a single flat list — but this was never a useful query for the musician panel.

### Interaction with ADR-012 (same-concert track switching)

ADR-012 established that clicking a second track from the same concert updates the existing player window rather than opening a new one. This behaviour is unchanged and works correctly with the bracketed structure: all compositions within a bracket share the same `video_id`, so clicking any of them will update the same player window.

### Interaction with ADR-011 (left-right sidebar symmetry)

The left panel groups by composition (all performances of a raga together). The right panel now groups by concert (all compositions of a concert together). This is the correct symmetric structure: left = music axis, right = event axis. Both panels support the same two-level interaction: (1) select a group, (2) navigate within it.

---

## CLI queries — rasika queries must be answerable at the command line

Every query the UI enables must also be answerable via [`carnatic/cli.py`](../carnatic/cli.py) and [`carnatic/graph_api.py`](../carnatic/graph_api.py). This is the principle of **queryability without the browser** — the scholar, the Librarian agent, and the Carnatic Coder must all be able to answer these questions from the terminal.

### Gap analysis against current CLI

| Rasika query | Current CLI support | Gap |
|---|---|---|
| "What concerts did Ramnad Krishnan give?" | `recordings-for ramnad_krishnan` — lists recording titles and dates | ✓ Partially covered. Returns full recording dicts, not a bracketed summary. |
| "Who played alongside Ramnad Krishnan at Wesleyan?" | `python3 carnatic/graph_api.py --concert wesleyan_1967_ramnad_krishnan` — full programme JSON | ✓ Covered via `graph_api.py`. Not yet exposed in `cli.py`. |
| "When did Semmangudi and Musiri play together?" | No command | ✗ Missing |
| "Who has played alongside Ramnad Krishnan across all concerts?" | No command | ✗ Missing |
| "Show me the Wesleyan 1967 concert programme in order" | `python3 carnatic/graph_api.py --concert wesleyan_1967_ramnad_krishnan` | ✓ Covered via `graph_api.py`. Not yet in `cli.py`. |

### New CLI commands required

The Carnatic Coder must add three new subcommands to [`carnatic/cli.py`](../carnatic/cli.py) and the corresponding API methods to [`carnatic/graph_api.py`](../carnatic/graph_api.py):

---

#### 1. `concerts-for <musician_id>`

**Purpose:** Show all concerts in which a musician appears, grouped and bracketed — the CLI equivalent of the UI bracket view.

**Output format:**

```
Concerts for ramnad_krishnan:

  Srinivasa Farms Concert, Poonamallee 1965   [Jan 1965]
    Session 1 — vocal: Ramnad Krishnan · violin: T.N. Krishnan · mridangam: Vellore Ramabhadran
    4 pieces: bālē bālēndu bhūṣaṇi · abhimānamenneḍu · bhajana parulakēla · śrī māninī manōhara

  Wesleyan University Concert, 1967           [1967]
    Session 1 — vocal: Ramnad Krishnan · flute: T. Viswanathan · violin: V. Tyagarajan · mridangam: T. Ranganathan · tampura: Jon B. Higgins
    8 pieces: Yagnadulu Sukhamanu · Enduku Nirdaya · Bantureeti Kolu · Kaligiyunte · Tani Avarthanam · Samayamide Rara · Janathi Ramam — Ragamalika · Ni Nama Roopamulaku
```

**API method required on `CarnaticGraph`:**

```python
def get_concerts_for_musician(self, musician_id: str) -> list[dict]:
    """
    Return a list of concert bracket dicts for the given musician.
    Each dict contains:
      {
        "recording_id": str,
        "title":        str,
        "short_title":  str,
        "date":         str,
        "sessions": [
          {
            "session_index": int,
            "performers":    [...],   # full performer list for this session
            "performances":  [...],   # PerformanceRef list for this session
          }
        ]
      }
    Only sessions in which the musician appears are included.
    Concerts are sorted chronologically by date.
    """
```

**CLI command spec:**

```
python3 carnatic/cli.py concerts-for <musician_id>
```

Exit 0 if any concerts found. Exit 1 if musician not found or no concerts.

---

#### 2. `co-performers-of <musician_id>`

**Purpose:** List every musician who has shared a session with the given musician across all structured recordings. This answers "who has played alongside X?"

**Output format:**

```
Co-performers of ramnad_krishnan (across all structured recordings):

  t_viswanathan          "T. Viswanathan"          flute    — Wesleyan 1967
  tn_krishnan            "T.N. Krishnan"            violin   — Poonamallee 1965
  vellore_ramabhadran    "Vellore Ramabhadran"      mridangam — Poonamallee 1965
  [unmatched]            "V. Tyagarajan"            violin   — Wesleyan 1967
  [unmatched]            "T. Ranganathan"           mridangam — Wesleyan 1967
  [unmatched]            "Jon B. Higgins"           tampura  — Wesleyan 1967
```

**API method required on `CarnaticGraph`:**

```python
def get_co_performers_of(self, musician_id: str) -> list[dict]:
    """
    Return a deduplicated list of co-performer dicts for the given musician.
    Each dict contains:
      {
        "musician_id":    str | None,   # None if unmatched
        "label":          str,          # node label if matched; unmatched_name if not
        "role":           str,          # instrument/role
        "recording_ids":  list[str],    # all recordings where they co-performed
      }
    Sorted: matched musicians first (by label), then unmatched (by name).
    The given musician is excluded from their own co-performer list.
    """
```

**CLI command spec:**

```
python3 carnatic/cli.py co-performers-of <musician_id>
```

Exit 0 if any co-performers found. Exit 1 if musician not found or no structured recordings.

---

#### 3. `concerts-with <musician_id_a> <musician_id_b>`

**Purpose:** Find all concerts in which two specific musicians appeared together in the same session. This answers "when did X and Y play together?"

**Output format:**

```
Concerts where semmangudi_srinivasa_iyer and musiri_subramania_iyer appeared together:

  Srinivasa Farms Concert, Poonamallee 1965   [Jan 1965]
    Session 3 — vocal: Musiri Subramania Iyer · vocal: Semmangudi Srinivasa Iyer
                violin: T.N. Krishnan · violin: Lalgudi Jayaraman
                mridangam: Umayalpuram Sivaraman · mridangam: Vellore Ramabhadran
    1 piece: evarani nirṇayiñcirirā (Devamritavarshini · Adi)
```

**API method required on `CarnaticGraph`:**

```python
def get_concerts_with(self, musician_id_a: str, musician_id_b: str) -> list[dict]:
    """
    Return a list of concert bracket dicts (same shape as get_concerts_for_musician)
    for concerts where both musicians appear in the SAME session.
    Only sessions containing both musicians are included.
    Sorted chronologically.
    """
```

**CLI command spec:**

```
python3 carnatic/cli.py concerts-with <musician_id_a> <musician_id_b>
```

Exit 0 if any shared concerts found. Exit 1 if either musician not found or no shared concerts.

---

#### 4. `concert <recording_id>` (expose existing `get_concert_programme` in `cli.py`)

[`graph_api.py`](../carnatic/graph_api.py) already has [`get_concert_programme()`](../carnatic/graph_api.py:385) which returns the full resolved programme. It is exposed via `python3 carnatic/graph_api.py --concert <id>` but **not** via [`cli.py`](../carnatic/cli.py). The Carnatic Coder must add it to `cli.py`:

**Output format (human-readable, not JSON):**

```
Concert: Wesleyan University Concert, 1967 — Ramnad Krishnan & T. Viswanathan
Date:    1967
Venue:   Wesleyan University, USA

Session 1
  Performers: vocal: Ramnad Krishnan · flute: T. Viswanathan · violin: V. Tyagarajan
              mridangam: T. Ranganathan · tampura: Jon B. Higgins
  Performances:
    1.  00:00:00  Yagnadulu Sukhamanu          Jayamanohari · Adi
    2.  00:10:56  Enduku Nirdaya               Harikambhoji · Adi
    3.  00:33:42  Bantureeti Kolu              Hamsanadam · Deshadi
    4.  00:44:41  Kaligiyunte                  Keeravani · Adi
    5.  01:18:33  Tani Avarthanam              [tani]
    6.  01:24:04  Samayamide Rara              Behag · Rupakam
    7.  01:34:27  Janathi Ramam — Ragamalika   [ragamalika]
    8.  01:54:33  Ni Nama Roopamulaku          Sowrashtram · Adi
```

**CLI command spec:**

```
python3 carnatic/cli.py concert <recording_id>
python3 carnatic/cli.py concert <recording_id> --json
```

Exit 0 if found. Exit 1 if not found.

---

### Updated `cli.py` docstring

The Carnatic Coder must update the module docstring in [`carnatic/cli.py`](../carnatic/cli.py) to include the new commands:

```
python3 carnatic/cli.py concerts-for      <musician_id>
python3 carnatic/cli.py co-performers-of  <musician_id>
python3 carnatic/cli.py concerts-with     <musician_id_a> <musician_id_b>
python3 carnatic/cli.py concert           <recording_id>  [--json]
```

---

## Implementation

**Agent:** Carnatic Coder
**Files:**
- [`carnatic/render.py`](../carnatic/render.py) — JavaScript and CSS changes (UI bracket rendering)
- [`carnatic/graph_api.py`](../carnatic/graph_api.py) — three new API methods: `get_concerts_for_musician`, `get_co_performers_of`, `get_concerts_with`
- [`carnatic/cli.py`](../carnatic/cli.py) — four new subcommands: `concerts-for`, `co-performers-of`, `concerts-with`, `concert`

**No data schema changes.** All required fields (`recording_id`, `session_index`, `performers[]`, `short_title`, `date`, `occasion`) are already present in the `PerformanceRef` shape and in the recording JSON files.

**Verification:**

```bash
# UI: open graph, select Ramnad Krishnan → two concert brackets visible, collapsed
# UI: expand Wesleyan 1967 → 8 compositions in concert order, co-performers shown
# UI: type "Begada" in filter → Poonamallee 1965 bracket expands, only Begada piece visible

# CLI:
python3 carnatic/cli.py concerts-for ramnad_krishnan
python3 carnatic/cli.py co-performers-of ramnad_krishnan
python3 carnatic/cli.py concerts-with semmangudi_srinivasa_iyer musiri_subramania_iyer
python3 carnatic/cli.py concert wesleyan_1967_ramnad_krishnan
python3 carnatic/cli.py concert wesleyan_1967_ramnad_krishnan --json
```
# ADR-022: Raga Panel Navigability — Mela, Cakra, Janyas, and Notes Tooltip

**Status:** Accepted
**Date:** 2026-04-12

---

## Context

### The symptom

ADR-020 gave the Bani Flow left panel a first-class subject header: when a rasika
searches for "Kapi", they see the raga name in bold yellow with a Wikipedia link.
ADR-021 enriched the data model with `is_melakarta`, `cakra`, and `parent_raga`
fields, and added CLI traversal commands (`janyas-of`, `mela-of`, `cakra-of`).

But the UI has not yet consumed this enriched data. Searching "Kapi" today shows:

```
◉ Kapi                                    ↗
  also: Kaapi
```

A rasika who searches for Kapi wants to know:

- *What mela is this?* (Harikambhoji, 28th melakarta)
- *What cakra?* (Cakra 5 — Bana)
- *What are the swaras?* (the arohana/avarohana, or at least the character)

A rasika who searches for Kharaharapriya wants to know:

- *Is this a melakarta?* (Yes — Mela 22, Cakra 4 Veda)
- *What are its janyas?* (Reetigowla, Abheri, Atana, Sriraga, Huseni…)
- *Can I navigate to a janya directly from here?*

Neither of these traversals is possible today. The `#bani-subject-sub` row shows
only aliases. The structural data exists in `compositions.json` — it is simply not
surfaced in the UI.

### The structural gap

The current [`buildListeningTrail()`](../carnatic/render.py:2223) raga branch
populates `#bani-subject-sub` with aliases only:

```javascript
// Row 2: aliases (if any)
if (raga && raga.aliases && raga.aliases.length > 0) {
  const aliasSpan = document.createElement('span');
  aliasSpan.id = 'bani-subject-aliases';
  aliasSpan.textContent = 'also: ' + raga.aliases.join(', ');
  subjectSub.appendChild(aliasSpan);
}
```

The `raga` object already carries `is_melakarta`, `cakra`, `parent_raga`, and
`notes` — but none of these are rendered. The `ragas` array (embedded in
`graph.html` by `render.py`) contains all the data needed; the UI simply does not
read it.

### The data readiness gap

The extraction script (`extract_melakarta_wikipedia.py`) has produced
`melakarta_patch.json` and `melakarta_new.json`. The Librarian has not yet applied
these patches — `kharaharapriya` currently has `is_melakarta: false` and
`cakra: null` in `compositions.json`. This ADR's UI changes depend on the Librarian
completing ADR-021 Phase 3–5 (patching existing melas, adding new melas, repairing
`parent_raga` on janya ragas). The UI must degrade gracefully when data is absent.

### Why the `notes` field is the right vehicle for swaras

The `notes` field on raga objects already contains arohana/avarohana text for mela
ragas added by the extraction script (e.g. `"arohana: S R2 G2 M1 P D2 N2 S"`).
For janya ragas it contains musicological character notes. Adding a separate
`swaras` or `arohana` field to the schema would require a new migration and a new
write command — and would duplicate information already in `notes`.

The correct pattern is a **hover tooltip** on the raga name: hovering over the bold
raga name in the header reveals the `notes` field as a tooltip. This surfaces the
arohana/avarohana and character description without cluttering the panel. It is the
same affordance used by the graph's node tooltips.

---

## Forces in tension

1. **Raga as a traversable strong centre** — The rasika who searches for
   Kharaharapriya must be able to navigate *downward* to its janyas without leaving
   the panel. The rasika who searches for Kapi must be able to navigate *upward* to
   its parent mela. The panel must support both directions of the Cakra → Mela →
   Janya gradient.

2. **Immersion without overload** — The panel is narrow. Showing all 18+ janyas of
   Kharaharapriya inline would overwhelm the panel and push the trail list off-screen.
   The janyas must be accessible but not always visible — a collapsed/expandable
   affordance is required.

3. **Graceful degradation** — The Librarian's ADR-021 data migration is in progress.
   Many ragas still have `is_melakarta: false` and `parent_raga: null`. The UI must
   show what it knows and omit what it does not — never showing incorrect data.

4. **Notes as tooltip, not inline text** — The `notes` field is free text of variable
   length (sometimes 200+ characters). It must not be rendered inline in the panel —
   it would break the layout. A hover tooltip is the correct affordance: always
   available, never intrusive.

5. **Janya navigation as a new traversal path** — Clicking a janya raga name in the
   "Janyas" dropdown must trigger a new Bani Flow search for that raga — the same
   action as typing the raga name in the search box. This creates a new in-panel
   navigation path that does not require the rasika to leave the panel or use the
   search box.

6. **No new schema fields** — The data needed for this ADR (`is_melakarta`, `cakra`,
   `parent_raga`, `notes`) is already in the schema (ADR-021). No new fields are
   required. This ADR is purely a UI change.

---

## Pattern

### **Gradients** (Alexander, Pattern 9)

The Cakra → Mela → Janya hierarchy is a natural gradient from broad to specific.
The raga panel must support traversal in both directions along this gradient:

- **Upward** (janya → mela → cakra): A janya raga's sub-label shows its parent mela
  as a clickable link. Clicking the mela name triggers a new Bani Flow search for
  that mela — the rasika climbs the gradient.
- **Downward** (mela → janyas): A mela raga's sub-label shows a "Janyas (N)" link.
  Clicking it expands a dropdown of all janya ragas. Clicking a janya name triggers
  a new Bani Flow search — the rasika descends the gradient.

### **Strong Centres** (Alexander, Pattern 1)

Each raga — mela or janya — is a strong centre. The panel must make each centre
legible: its position in the hierarchy (mela number, cakra), its character (notes
tooltip), and its relationships (parent mela for janyas; janya list for melas). A
strong centre is not just a name — it is a bounded world with connections.

### **Levels of Scale** (Alexander, Pattern 5)

The raga header now has four levels of scale:

```
Level 1: Raga name (bold yellow, 0.85rem) + Wikipedia link ↗
Level 2: Mela/cakra metadata OR parent mela link (0.70rem fg3)
Level 3: Aliases (0.68rem gray)
Level 4: Notes tooltip (on hover — not rendered inline)
```

The "Janyas" expandable sits between Level 2 and Level 3 — it is metadata about the
raga's structural role, not a content list. The janya dropdown is a Level 3 detail
that appears on demand.

### **Boundaries** (Alexander, Pattern 13)

The boundary between the raga header and the trail list is the `border-bottom` line
below `#bani-subject-header`. The janyas dropdown must appear *within* the header
boundary — not in the trail list. It is part of the raga's identity, not part of the
performance trail.

---

## Decision

### 1. Raga name tooltip — `notes` field on hover

Add a `title` attribute to `#bani-subject-name` containing the raga's `notes` field.
The browser renders this as a native tooltip on hover. No CSS change required.

```javascript
// In buildListeningTrail(), raga branch:
subjectName.textContent = raga ? raga.name : id;
if (raga && raga.notes) {
  subjectName.title = raga.notes;   // ← hover tooltip
}
```

**Example tooltip for Kapi:**
> Janya of Harikambhoji (28th melakarta); bhashanga raga admitting both G2 and G3;
> evokes srngara and karuna; a favourite raga for padams and javalis; associated with
> the devadasi repertoire

**Example tooltip for Kharaharapriya (after ADR-021 data migration):**
> 22nd melakarta; Cakra 4 (Veda); arohana S R2 G2 M1 P D2 N2 S; avarohana S N2 D2
> P M1 G2 R2 S; parent of Reetigowla, Abheri, Atana, Sriraga, Huseni, Dwijavanthi…

### 2. Sub-label enrichment — mela/cakra metadata and parent mela link

Replace the current aliases-only `#bani-subject-sub` content with a structured
three-line sub-label for raga searches:

#### Line 1 — Structural position (mela/cakra or parent mela)

**For a mela raga** (`is_melakarta === true`):

```
Mela 22 · Cakra 4 — Veda
```

Rendered as plain text (no links — the mela number and cakra are facts, not
navigation targets at this level).

**For a janya raga** (`parent_raga` is set):

```
Janya of [Harikambhoji] ↗
```

Where `[Harikambhoji]` is a clickable `bani-sub-link` that triggers
`buildListeningTrail('raga', parent_raga_id, ...)` — the same action as searching
for the parent mela in the search box. The `↗` is omitted here; the link itself is
the navigation affordance.

**If neither** (`is_melakarta` is absent/false and `parent_raga` is null):

Line 1 is omitted. The panel shows only aliases. This is the graceful degradation
case for ragas whose ADR-021 data has not yet been applied.

#### Line 2 — Aliases

```
also: Kaapi
```

Unchanged from current behaviour. Shown only if `aliases.length > 0`.

#### Line 3 — Janyas expandable (mela ragas only)

For mela ragas, after the aliases line, add a "Janyas" toggle:

```
▶ Janyas (18)
```

Clicking the toggle expands an inline dropdown within `#bani-subject-header`:

```
▼ Janyas (18)
  Reetigowla · Abheri · Atana · Sriraga
  Huseni · Dwijavanthi · Kannada · Kurinji
  Maund · Narayanagowla · Suruti · Gowla
  Sri · Dhenuka · Devamritavarshini
  Manirangu · Devagandhari · Kaanada
```

Each janya name is a `bani-sub-link` that calls
`buildListeningTrail('raga', janya_id, ...)`. The dropdown is a `<div>` with
`display: none` toggled by the click. It wraps names with `flex-wrap: wrap` and
`gap: 4px`.

The janya count `(N)` is computed at render time from the `ragas` array:
`ragas.filter(r => r.parent_raga === id).length`. This is a client-side count —
no new API call.

### 3. Visual structure — before and after

#### Before (current — raga search "Kapi")

```
┌─────────────────────────────────────────────┐
│ ◉ Kapi                               ↗      │  ← bold yellow 0.85rem
│   also: Kaapi                               │  ← 0.68rem gray
│ ─────────────────────────────────────────── │
│ [Filter trail…]                             │
│ ● Vina Dhanammal  1867–1938                 │
│   Viruttam (Pasuram) — Kulam  45:08 ↗       │
└─────────────────────────────────────────────┘
```

#### After (raga search "Kapi" — janya with parent set)

```
┌─────────────────────────────────────────────┐
│ ◉ Kapi [hover → notes tooltip]       ↗      │  ← bold yellow 0.85rem
│   Janya of Harikambhoji              ←link  │  ← 0.70rem fg3, name is bani-sub-link
│   also: Kaapi                               │  ← 0.68rem gray
│ ─────────────────────────────────────────── │
│ [Filter trail…]                             │
│ ● Vina Dhanammal  1867–1938                 │
└─────────────────────────────────────────────┘
```

#### After (raga search "Kharaharapriya" — mela raga, janyas collapsed)

```
┌─────────────────────────────────────────────┐
│ ◉ Kharaharapriya [hover → notes]     ↗      │  ← bold yellow 0.85rem
│   Mela 22 · Cakra 4 — Veda                 │  ← 0.70rem fg3, plain text
│   also: Kara Harapriya                      │  ← 0.68rem gray
│   ▶ Janyas (18)                             │  ← 0.68rem teal, clickable toggle
│ ─────────────────────────────────────────── │
│ [Filter trail…]                             │
│ ● Ramnad Krishnan  1918–1973                │
└─────────────────────────────────────────────┘
```

#### After (raga search "Kharaharapriya" — janyas expanded)

```
┌─────────────────────────────────────────────┐
│ ◉ Kharaharapriya [hover → notes]     ↗      │
│   Mela 22 · Cakra 4 — Veda                 │
│   also: Kara Harapriya                      │
│   ▼ Janyas (18)                             │
│   ┌─────────────────────────────────────┐   │
│   │ Reetigowla · Abheri · Atana         │   │  ← each name is a bani-sub-link
│   │ Sriraga · Huseni · Dwijavanthi      │   │
│   │ Kannada · Kurinji · Maund           │   │
│   │ Narayanagowla · Suruti · Gowla      │   │
│   │ Sri · Dhenuka · Devamritavarshini   │   │
│   │ Manirangu · Devagandhari · Kaanada  │   │
│   └─────────────────────────────────────┘   │
│ ─────────────────────────────────────────── │
│ [Filter trail…]                             │
└─────────────────────────────────────────────┘
```

### 4. HTML additions — within `#bani-subject-header`

The existing `#bani-subject-header` block gains two new child elements:

```html
<div id="bani-subject-header" style="display:none">
  <!-- Row 1: name + outbound link (unchanged) -->
  <div id="bani-subject-name-row">
    <span id="bani-subject-icon" class="bani-subject-icon"></span>
    <span id="bani-subject-name"></span>
    <a id="bani-subject-link" class="bani-subject-link" href="#"
       target="_blank" style="display:none">&#8599;</a>
  </div>
  <!-- Row 2: sub-label (mela/cakra or parent mela, or raga·tala·composer) -->
  <div id="bani-subject-sub"></div>
  <!-- Row 3: aliases (NEW — extracted from sub for independent styling) -->
  <div id="bani-subject-aliases-row" style="display:none"></div>
  <!-- Row 4: janyas toggle + dropdown (NEW — mela ragas only) -->
  <div id="bani-janyas-row" style="display:none">
    <span id="bani-janyas-toggle" class="bani-janyas-toggle">&#9654; Janyas</span>
    <span id="bani-janyas-count" class="bani-janyas-count"></span>
    <div id="bani-janyas-list" class="bani-janyas-list" style="display:none"></div>
  </div>
</div>
```

**Key structural change:** The aliases line is extracted from `#bani-subject-sub`
into its own `#bani-subject-aliases-row` div. This allows the janyas toggle to
appear *after* the aliases, not mixed into the sub-label. The `#bani-subject-sub`
div now contains only the structural metadata (mela/cakra or parent mela link).

### 5. CSS additions

```css
/* ── Raga panel navigability (ADR-022) ── */

/* Aliases row — below sub-label */
#bani-subject-aliases-row {
  font-size: 0.68rem; color: var(--gray);
  margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Janyas toggle row */
#bani-janyas-row {
  margin-top: 4px;
  font-size: 0.68rem;
}

.bani-janyas-toggle {
  color: var(--teal); cursor: pointer;
  user-select: none;
}
.bani-janyas-toggle:hover { text-decoration: underline; }

.bani-janyas-count {
  color: var(--gray); margin-left: 2px;
}

/* Janyas dropdown list */
.bani-janyas-list {
  margin-top: 4px;
  padding: 4px 6px;
  background: var(--bg2);
  border-radius: 3px;
  display: flex; flex-wrap: wrap; gap: 2px 6px;
  font-size: 0.68rem;
  max-height: 120px;
  overflow-y: auto;
}

/* Each janya name in the dropdown */
.bani-janya-link {
  color: var(--blue); text-decoration: none; cursor: pointer;
  white-space: nowrap;
}
.bani-janya-link:hover { text-decoration: underline; }

/* Raga name tooltip — no CSS needed; uses native title attribute */
```

### 6. JavaScript changes — `buildListeningTrail` raga branch

Replace the current raga branch (lines 2223–2241 of [`render.py`](../carnatic/render.py))
with the following structured construction:

```javascript
} else {
  // ── Raga search ────────────────────────────────────────────────────────────
  const raga = ragas.find(r => r.id === id);

  // Row 1: raga name + Wikipedia link + notes tooltip
  subjectName.textContent = raga ? raga.name : id;
  if (raga && raga.notes) {
    subjectName.title = raga.notes;          // hover tooltip
  }
  const ragaSrc = raga && raga.sources && raga.sources[0];
  if (ragaSrc) {
    subjectLink.href = ragaSrc.url;
    subjectLink.style.display = 'inline';
  }

  // Row 2 (#bani-subject-sub): structural position
  subjectSub.innerHTML = '';
  if (raga && raga.is_melakarta) {
    // Mela raga: show mela number and cakra
    const mela_num  = raga.melakarta;
    const cakra_num = raga.cakra;
    const cakra_name = CAKRA_NAMES[cakra_num] || String(cakra_num);
    if (mela_num && cakra_num) {
      const melaSpan = document.createElement('span');
      melaSpan.textContent = `Mela ${mela_num} \u00b7 Cakra ${cakra_num} \u2014 ${cakra_name}`;
      subjectSub.appendChild(melaSpan);
    }
  } else if (raga && raga.parent_raga) {
    // Janya raga: show parent mela as a clickable link
    const parentRaga = ragas.find(r => r.id === raga.parent_raga);
    const parentName = parentRaga ? parentRaga.name : raga.parent_raga;
    const janyaLabel = document.createElement('span');
    janyaLabel.textContent = 'Janya of ';
    janyaLabel.style.color = 'var(--fg3)';
    const parentLink = document.createElement('a');
    parentLink.className = 'bani-sub-link';
    parentLink.href = '#';
    parentLink.textContent = parentName;
    parentLink.addEventListener('click', e => {
      e.preventDefault();
      triggerBaniSearch('raga', raga.parent_raga);
    });
    janyaLabel.appendChild(parentLink);
    subjectSub.appendChild(janyaLabel);
  }
  // (if neither: sub-label is empty — graceful degradation)

  // Row 3 (#bani-subject-aliases-row): aliases
  const aliasesRow = document.getElementById('bani-subject-aliases-row');
  aliasesRow.textContent = '';
  aliasesRow.style.display = 'none';
  if (raga && raga.aliases && raga.aliases.length > 0) {
    aliasesRow.textContent = 'also: ' + raga.aliases.join(', ');
    aliasesRow.style.display = 'block';
  }

  // Row 4 (#bani-janyas-row): janyas toggle (mela ragas only)
  const janyasRow    = document.getElementById('bani-janyas-row');
  const janyasList   = document.getElementById('bani-janyas-list');
  const janyasToggle = document.getElementById('bani-janyas-toggle');
  const janyasCount  = document.getElementById('bani-janyas-count');
  janyasRow.style.display = 'none';
  janyasList.style.display = 'none';
  janyasList.innerHTML = '';

  if (raga && raga.is_melakarta) {
    const janyas = ragas.filter(r => r.parent_raga === id);
    if (janyas.length > 0) {
      janyasCount.textContent = `(${janyas.length})`;
      janyasToggle.textContent = '\u25b6 Janyas';
      janyasRow.style.display = 'block';

      // Populate janya links
      janyas.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
      janyas.forEach(j => {
        const a = document.createElement('a');
        a.className = 'bani-janya-link';
        a.href = '#';
        a.textContent = j.name || j.id;
        a.addEventListener('click', e => {
          e.preventDefault();
          triggerBaniSearch('raga', j.id);
        });
        janyasList.appendChild(a);
      });

      // Toggle behaviour
      janyasToggle.onclick = () => {
        const open = janyasList.style.display !== 'none';
        janyasList.style.display = open ? 'none' : 'flex';
        janyasToggle.textContent = open ? '\u25b6 Janyas' : '\u25bc Janyas';
      };
    }
  }
}
```

### 7. `triggerBaniSearch` helper function

The janya navigation requires a programmatic way to trigger a Bani Flow search for
a raga ID — the same action as the user typing a raga name in the search box and
selecting it. The Carnatic Coder must extract this logic into a named helper:

```javascript
/**
 * Programmatically trigger a Bani Flow search for a raga or composition.
 * Equivalent to the user selecting an item from the bani-search-dropdown.
 * @param {'raga'|'comp'} type
 * @param {string} id  — raga id or composition id
 */
function triggerBaniSearch(type, id) {
  // Find the matched node IDs for this raga/composition
  const matchedNodeIds = findMatchedNodeIds(type, id);
  // Update the search input label
  const searchInput = document.getElementById('bani-search-input');
  const entity = type === 'raga'
    ? ragas.find(r => r.id === id)
    : compositions.find(c => c.id === id);
  if (searchInput && entity) {
    searchInput.value = entity.name || entity.title || id;
  }
  // Highlight matched nodes in the graph
  highlightBaniNodes(matchedNodeIds);
  // Build the trail
  buildListeningTrail(type, id, matchedNodeIds);
  document.getElementById('trail-filter').style.display = 'block';
  document.getElementById('trail-filter').value = '';
}
```

The Carnatic Coder must identify the existing code path that handles a bani-search
dropdown selection and refactor it to call `triggerBaniSearch` — ensuring the
programmatic path and the user-interaction path are identical.

### 8. `CAKRA_NAMES` constant in the rendered JavaScript

The `CAKRA_NAMES` lookup (already present in [`cli.py`](../carnatic/cli.py) and
[`graph_api.py`](../carnatic/graph_api.py)) must be embedded in the rendered
JavaScript by `render.py`:

```javascript
const CAKRA_NAMES = {
  1: 'Indu', 2: 'Netra', 3: 'Agni', 4: 'Veda',
  5: 'Bana', 6: 'Rutu', 7: 'Rishi', 8: 'Vasu',
  9: 'Brahma', 10: 'Disi', 11: 'Rudra', 12: 'Aditya'
};
```

This is a static constant — it does not change with data. It should be placed near
the top of the `<script>` block, alongside other static constants.

### 9. Before / After JSON shape

No schema change. All fields used by this ADR are already in the schema:

| field | source | used for |
|---|---|---|
| `raga.is_melakarta` | ADR-021 | determines mela vs janya branch |
| `raga.melakarta` | existing | mela number display |
| `raga.cakra` | ADR-021 | cakra number display |
| `raga.parent_raga` | existing (repaired by ADR-021) | parent mela link |
| `raga.aliases` | existing | aliases line |
| `raga.notes` | existing | hover tooltip |
| `raga.sources[0].url` | existing | Wikipedia outbound link |

#### Raga object — Kapi (janya, current state — no change needed)

```json
{
  "id": "kapi",
  "name": "Kapi",
  "aliases": ["Kaapi"],
  "melakarta": null,
  "parent_raga": "harikambhoji",
  "is_melakarta": false,
  "cakra": null,
  "notes": "Janya of Harikambhoji (28th melakarta); bhashanga raga admitting both G2 and G3; evokes srngara and karuna; a favourite raga for padams and javalis; associated with the devadasi repertoire",
  "sources": [{ "url": "https://en.wikipedia.org/wiki/Kapi_(raga)", "label": "Wikipedia", "type": "wikipedia" }]
}
```

**UI renders:**
- Row 1: `Kapi` (bold yellow) + `↗` Wikipedia link; hover → notes tooltip
- Row 2: `Janya of` **`Harikambhoji`** (clickable → triggers Harikambhoji search)
- Row 3: `also: Kaapi`
- Row 4: (no janyas toggle — not a mela)

#### Raga object — Kharaharapriya (mela, after ADR-021 Librarian migration)

```json
{
  "id": "kharaharapriya",
  "name": "Kharaharapriya",
  "aliases": ["Kara Harapriya"],
  "melakarta": 22,
  "is_melakarta": true,
  "cakra": 4,
  "parent_raga": null,
  "notes": "22nd melakarta; Cakra 4 (Veda); arohana S R2 G2 M1 P D2 N2 S; avarohana S N2 D2 P M1 G2 R2 S; parent of Reetigowla, Abheri, Atana, Sriraga, Huseni, Dwijavanthi, Kannada, Kurinji, Maund, Narayanagowla, Suruti, Gowla, Sri, Dhenuka, Devamritavarshini, Manirangu, Devagandhari, Kaanada",
  "sources": [{ "url": "https://en.wikipedia.org/wiki/Kharaharapriya", "label": "Wikipedia", "type": "wikipedia" }]
}
```

**UI renders:**
- Row 1: `Kharaharapriya` (bold yellow) + `↗`; hover → notes tooltip with arohana
- Row 2: `Mela 22 · Cakra 4 — Veda`
- Row 3: `also: Kara Harapriya`
- Row 4: `▶ Janyas (18)` → expands to 18 clickable janya names

---

## Consequences

### Queries this enables

| Rasika query | Before | After |
|---|---|---|
| "What mela is Kapi?" | Read notes free text | `Janya of Harikambhoji` shown in sub-label |
| "Navigate to Harikambhoji from Kapi" | Type in search box | Click `Harikambhoji` link in sub-label |
| "What cakra is Kharaharapriya?" | Not visible in UI | `Mela 22 · Cakra 4 — Veda` in sub-label |
| "What are the janyas of Kharaharapriya?" | Not possible in UI | Click `▶ Janyas (18)` to expand list |
| "Navigate from Kharaharapriya to Abheri" | Type in search box | Click `Abheri` in janyas dropdown |
| "What are the swaras of this raga?" | Not visible in UI | Hover over raga name → notes tooltip |
| "Is Kharaharapriya a melakarta?" | Not visible in UI | `Mela 22` in sub-label confirms it |
| "What is the character of Kapi?" | Not visible in UI | Hover over `Kapi` → tooltip with character notes |

### What this enables beyond the current data

- **In-panel raga traversal** — The rasika can now navigate the Cakra → Mela →
  Janya hierarchy entirely within the left panel, without touching the search box.
  Clicking a parent mela link or a janya name triggers a new Bani Flow search,
  updating the trail list to show performances of that raga. This is the raga
  equivalent of clicking a shishya name in the right panel to navigate the lineage.

- **Swaras on demand** — The hover tooltip surfaces arohana/avarohana and character
  notes without consuming panel space. For mela ragas added by the ADR-021 extraction
  script, the tooltip will contain the full arohana/avarohana. For janya ragas, it
  contains the musicological character description. The rasika gets the information
  they need without the panel becoming a reference card.

- **Janya count as a structural signal** — The `▶ Janyas (18)` label communicates
  the structural importance of a mela raga before the rasika expands it. A mela with
  18 janyas is a major hub; a mela with 2 janyas is a minor one. This is information
  a student or scholar would want to know.

- **Graceful degradation as a migration signal** — When `is_melakarta` is absent or
  false and `parent_raga` is null, the sub-label is empty. This is a visible signal
  to the Librarian that the ADR-021 migration has not yet been applied to this raga.
  The absence of structural metadata is itself informative.

- **`triggerBaniSearch` as a reusable primitive** — Extracting the bani search
  trigger into a named function enables future ADRs to programmatically navigate the
  Bani Flow panel from other UI surfaces (e.g. clicking a raga name in the right
  panel's recording trail, or clicking a raga in a future cakra wheel view).

### What this forecloses

- **Inline arohana/avarohana display** — The decision to use a hover tooltip rather
  than inline text forecloses a persistent display of swaras in the panel. If a
  future ADR adds a dedicated `arohana`/`avarohana` schema field, the tooltip could
  be replaced by an inline display — but the tooltip is the correct affordance for
  now, given the variable length of the `notes` field.

- **Bhashanga secondary parents** — Kapi is a bhashanga raga with a primary parent
  (Harikambhoji) and secondary borrowings. This ADR shows only the primary
  `parent_raga`. Secondary parents are in `notes` and will appear in the tooltip.
  A future ADR may add `secondary_parents: []` to the schema if the UI needs to
  traverse them.

- **Janya sorting** — The janyas dropdown sorts alphabetically by name. A future ADR
  may sort by frequency of performance (most-recorded janyas first) once recording
  data is richer. Alphabetical is the correct default.

### Interaction with ADR-020 (raga/composition header parity)

ADR-020 established the `#bani-subject-header` structure. ADR-022 enriches the raga
branch of that structure. The composition branch (`type === 'comp'`) is unchanged.
The HTML additions (rows 3 and 4) are new elements appended to `#bani-subject-header`
— they do not affect the composition branch because they are hidden by default and
only shown in the raga branch.

### Interaction with ADR-021 (melakarta first-class citizens)

ADR-022 is the UI consumer of ADR-021's data. The two ADRs have a dependency:
ADR-022's mela/cakra display and janyas dropdown are only populated once the
Librarian completes ADR-021 Phases 3–5. The UI degrades gracefully until then.
The Carnatic Coder should implement ADR-022 immediately — the graceful degradation
path ensures no regression while the Librarian completes the data migration.

---

## Implementation

**Agent:** Carnatic Coder
**Files:** [`carnatic/render.py`](../carnatic/render.py)

### Step 1: Add `CAKRA_NAMES` constant to the JavaScript block

Near the top of the `<script>` section in `render.py`, add:

```javascript
const CAKRA_NAMES = {
  1: 'Indu', 2: 'Netra', 3: 'Agni', 4: 'Veda',
  5: 'Bana', 6: 'Rutu', 7: 'Rishi', 8: 'Vasu',
  9: 'Brahma', 10: 'Disi', 11: 'Rudra', 12: 'Aditya'
};
```

Note: in `render.py`'s f-string template, `{` and `}` must be doubled as `{{` and
`}}` to avoid Python format-string interpolation. The object literal above must be
written as `{{` / `}}` in the Python source.

### Step 2: Add new HTML rows to `#bani-subject-header`

In the HTML template, after `<div id="bani-subject-sub"></div>`, add:

```html
<!-- Row 3: aliases (ADR-022) -->
<div id="bani-subject-aliases-row" style="display:none"></div>
<!-- Row 4: janyas toggle + dropdown (ADR-022, mela ragas only) -->
<div id="bani-janyas-row" style="display:none">
  <span id="bani-janyas-toggle" class="bani-janyas-toggle">&#9654; Janyas</span>
  <span id="bani-janyas-count" class="bani-janyas-count"></span>
  <div id="bani-janyas-list" class="bani-janyas-list" style="display:none"></div>
</div>
```

### Step 3: Add CSS rules

After the existing `#bani-subject-aliases` rule, add the ADR-022 CSS block
(see Decision §5 above).

### Step 4: Refactor `buildListeningTrail` raga branch

Replace the current raga branch (the `else` block after `if (type === 'comp')`)
with the structured construction in Decision §6 above.

**Critical:** The `#bani-subject-aliases-row` and `#bani-janyas-row` elements must
be reset to `display:none` at the top of `buildListeningTrail` (alongside the
existing `subjectSub.innerHTML = ''` reset), so they do not persist across searches.

Add to the reset block at the top of `buildListeningTrail`:

```javascript
document.getElementById('bani-subject-aliases-row').style.display = 'none';
document.getElementById('bani-subject-aliases-row').textContent = '';
document.getElementById('bani-janyas-row').style.display = 'none';
document.getElementById('bani-janyas-list').style.display = 'none';
document.getElementById('bani-janyas-list').innerHTML = '';
```

Also add these resets to the `clearBaniFlow()` function (or equivalent) that hides
the panel when the search is cleared.

### Step 5: Extract `triggerBaniSearch` helper

Identify the existing code path that handles a bani-search dropdown item click
(the `click` handler on `.bani-dropdown-item` or equivalent). Extract the core
logic into `triggerBaniSearch(type, id)` as specified in Decision §7. Update the
dropdown click handler to call `triggerBaniSearch`. Verify that the programmatic
path (from janya/parent links) and the user-interaction path (from the dropdown)
produce identical results.

### Step 6: Regenerate and verify

```bash
python3 carnatic/render.py
python3 carnatic/serve.py
```

**Verification checklist:**

- [ ] Search "Kapi" → sub-label shows `Janya of Harikambhoji` with clickable link
- [ ] Hover over "Kapi" name → tooltip shows notes text
- [ ] Click `Harikambhoji` link → panel updates to show Harikambhoji trail
- [ ] Search "Kharaharapriya" → sub-label shows `Mela 22 · Cakra 4 — Veda`
  (only after ADR-021 Librarian migration; before migration, sub-label is empty)
- [ ] Search "Kharaharapriya" → `▶ Janyas (N)` toggle appears
  (only after ADR-021 migration; N = number of ragas with `parent_raga: "kharaharapriya"`)
- [ ] Click `▶ Janyas` → dropdown expands with janya names
- [ ] Click a janya name in dropdown → panel updates to show that janya's trail
- [ ] Click `▼ Janyas` → dropdown collapses
- [ ] Search "Begada" (no `is_melakarta`, no `parent_raga`) → sub-label is empty;
  aliases shown; no janyas toggle — graceful degradation confirmed
- [ ] Composition search (e.g. "Abhimanamennedu") → composition branch unchanged;
  no aliases row or janyas row visible
- [ ] Clear search → aliases row and janyas row hidden; no stale content
- [ ] `#bani-subject-aliases-row` and `#bani-janyas-row` are hidden on panel clear
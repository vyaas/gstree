# ADR-008: Era and Instrument Legends as Functional Topbar Filters with Transparent Scope

**Status:** Proposed  
**Date:** 2026-04-11  
**Depends on:** ADR-003 (left sidebar), ADR-007 (search bar colocation)

---

## Context

The ERA and INSTRUMENT legend panels currently live at the bottom of the left sidebar,
beneath the Bani Flow panel (per ADR-003). They serve one purpose: a static colour/shape
key for the graph nodes. The user has identified two problems with this arrangement:

### Problem 1: Wrong spatial home

The legends are **conceptually different** from the Bani Flow panel. Bani Flow is a
*listening trail* — a chronological immersion tool that traces a composition's
transmission through the parampara. The ERA and INSTRUMENT legends are *graph-reading
aids* — they decode the visual vocabulary of the node colours and shapes. Placing them
in the same sidebar column as Bani Flow implies they are part of the same conceptual
family. They are not.

The Bani Flow panel is a **filter that operates on the graph** (it highlights a lineage
thread). The legends are **keys that decode the graph** (they explain what colours and
shapes mean). These are different cognitive operations. Mixing them in the same column
creates a **Boundaries** failure: two centres of different character share the same
spatial container without a strong boundary between them.

### Problem 2: Static legends waste their potential

A legend that only decodes is a missed opportunity. Each era chip and each instrument
chip already *names* a subset of nodes. The rasika looking at the legend and thinking
"I want to see all Contemporary musicians" must currently:

1. Read the legend to learn that Contemporary = yellow-green dot
2. Mentally scan the graph for yellow-green nodes
3. Zoom and pan to find them

This is three steps of cognitive work that the interface could collapse to one click.

### Problem 3: The design tension — scope ambiguity

If clicking "Contemporary" grays out all non-Contemporary nodes, the rasika may
reasonably infer that the **search bars** (musician search in the right sidebar, Bani
Flow search in the left sidebar) are now operating on a *filtered subset* — i.e., that
typing in the musician search will only find Contemporary musicians.

This inference is **wrong** — both search bars always operate on the full graph — but
the visual state (most nodes grayed out) makes it feel correct. This is a **false
affordance**: the interface implies a constraint that does not exist.

The design must:
1. Make the filter action clear and inviting
2. Make the filter *scope* (visual only, not search-limiting) unambiguous
3. Provide a frictionless path back to the unfiltered state

### Forces in tension

| Force | Pressure |
|---|---|
| **Immersion** | The rasika should be able to narrow the visual field to a single era or instrument with one click, without losing the ability to search the full graph. |
| **Transparency** | The interface must not imply a constraint that does not exist. If nodes are grayed out, the rasika must know that search still covers all nodes. |
| **Recoverability** | Any filter state must be trivially reversible. The rasika must never feel trapped in a filtered view. |
| **Header cleanliness** | Per ADR-007, the header is being cleaned of search bars. Adding legend chips to the header must not re-clutter it. The chips must be compact and visually subordinate to the title and controls. |
| **Levels of Scale** | The header operates at the graph level. Era and instrument are graph-level properties (they describe every node). Moving the legends to the header is architecturally correct — they belong at the same level as the graph controls (Fit, Reset, Relayout). |
| **Strong Centres** | The left sidebar is a strong centre for the Bani Flow listening trail. Removing the legends from it strengthens that centre — the left sidebar becomes *purely* the Bani Flow surface, with no mixed concerns. |

---

## Pattern

**Levels of Scale** (Alexander, Pattern 5): the header operates at the graph level.
Era and instrument are graph-level properties — they describe the entire node set, not
any individual selection. Moving the legend chips to the header places them at the
correct level of scale.

**Strong Centres** (Pattern 1): removing the legends from the left sidebar allows the
left sidebar to become a single-purpose strong centre: the Bani Flow listening trail.
The header becomes a stronger centre for graph-level controls. Both centres are
strengthened by the separation.

**Boundaries** (Pattern 13): the boundary between "graph-level controls" (header) and
"global listening trail" (left sidebar) must be clear and strong. The legends belong on
the graph-level side of this boundary.

**Positive Space** (Pattern 61): every element must have a clear, active role. A static
legend is passive — it decodes but does not act. Making the chips clickable gives them
positive space: they are now *actors* in the interface, not just labels.

**Gradients** (Pattern 9): the transition from "full graph" to "filtered view" must be
smooth and reversible. The filter chips provide a gradient: click once to narrow, click
again (or click a "show all" affordance) to restore. The gradient must never feel like
a trap.

---

## Decision

### Move ERA and INSTRUMENT legend chips to the header topbar.

Each chip is clickable. Clicking a chip **highlights** all nodes matching that
criterion and **dims** all others — identical in mechanism to the existing node-click
neighbourhood highlight. Clicking a second chip of the same group **adds** to the
selection (multi-select within a group). Clicking an already-active chip **deactivates**
it. When all chips in a group are inactive, the graph returns to its unfiltered state.

**The search bars are never affected by chip filters.** Both the musician search and
the Bani Flow search always operate on the full graph regardless of which chips are
active. This is made explicit by a persistent, unobtrusive scope label.

---

### Before / After layout

#### Before (current state — per ADR-003)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Carnatic · Guru-Shishya Parampara   56 musicians · 42 edges                  │
│                              [Fit] [Reset] [Relayout] [Labels] [Timeline]    │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────────────────────┬──────────────────────────────┐
│ LEFT SIDEBAR │       GRAPH CANVAS            │   RIGHT SIDEBAR              │
│              │                               │                              │
│ BANI FLOW ♩  │                               │  [🔍 Search musician…]       │
│ [search…]    │                               │  ● T. Muktha  1914–2007  ↗   │
│ [trail…]     │                               │  [Filter recordings…]        │
│              │                               │  RECORDINGS                  │
│ ERA          │                               │  [list…]                     │
│ ● Trinity    │                               │                              │
│ ● Bridge     │                               │                              │
│ ● Golden Age │                               │                              │
│ ● Dissem.    │                               │                              │
│ ● Living P.  │                               │                              │
│ ● Contemp.   │                               │                              │
│              │                               │                              │
│ INSTRUMENT   │                               │                              │
│ ○ vocal      │                               │                              │
│ ◆ veena      │                               │                              │
│ □ violin     │                               │                              │
│ △ flute      │                               │                              │
│ ● mridangam  │                               │                              │
└──────────────┴──────────────────────────────┴──────────────────────────────┘
```

#### After (proposed state)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Carnatic · Guru-Shishya Parampara   56 musicians · 42 edges                  │
│ ●Trinity  ●Bridge  ●GoldenAge  ●Dissem  ●LivingP  ●Contemp  │  ○vocal  ◆veena  □violin  △flute  ●mridangam │
│                              [Fit] [Reset] [Relayout] [Labels] [Timeline]    │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────────────────────┬──────────────────────────────┐
│ LEFT SIDEBAR │       GRAPH CANVAS            │   RIGHT SIDEBAR              │
│              │                               │                              │
│ BANI FLOW ♩  │                               │  [🔍 Search musician…]       │
│ [search…]    │                               │  ● T. Muktha  1914–2007  ↗   │
│ [trail…]     │                               │  [Filter recordings…]        │
│              │                               │  RECORDINGS                  │
│              │                               │  [list…]                     │
│              │                               │                              │
└──────────────┴──────────────────────────────┴──────────────────────────────┘
```

The left sidebar is now **purely** the Bani Flow panel. The ERA and INSTRUMENT chips
live in the header, on the same row as the graph controls (or on a dedicated second
row of the header if horizontal space is tight).

---

### Chip interaction model

#### Single-group selection (era OR instrument)

```
State: no chips active → full graph visible (default)

Click "Contemporary":
  → Contemporary nodes: full opacity, normal style
  → All other nodes: dimmed (opacity 0.15, same as .faded class)
  → Edges between non-Contemporary nodes: dimmed
  → Edges connecting Contemporary to non-Contemporary: dimmed
  → "Contemporary" chip: active state (highlighted border, slightly brighter background)

Click "Contemporary" again:
  → Deactivates. Graph returns to full visibility.

Click "Contemporary" then click "Living Pillars":
  → Both Contemporary AND Living Pillars nodes: full opacity
  → All others: dimmed
  → Both chips: active state
  → (Multi-select within the era group)
```

#### Cross-group selection (era AND instrument)

```
Click "Contemporary" (era group):
  → All Contemporary nodes highlighted

Then click "veena" (instrument group):
  → Intersection: Contemporary veena players highlighted
  → All others: dimmed
  → Both chips active
```

The intersection model is the most useful for the rasika: "show me all Contemporary
veena players" is a natural query. The union model (show Contemporary OR veena) would
produce a larger, less focused set and is less useful.

**Cross-group logic: AND (intersection)**  
**Within-group logic: OR (union)**

This matches natural language: "Contemporary OR Living Pillars veena players."

#### Deactivation

Three paths to restore the full graph:

1. **Click an active chip** — deactivates that chip. If no chips remain active, full
   graph restores.
2. **Click the graph background** — clears all chip filters AND node selection (same
   as the existing background-tap handler, extended to also clear chip state).
3. **"Show all" affordance** — a small `✕ Clear filters` text link appears in the
   header *only when at least one chip is active*. Clicking it deactivates all chips
   and restores the full graph. This is the explicit, unambiguous escape hatch.

---

### Scope transparency — resolving the design tension

The core tension: when nodes are dimmed, the rasika may think the search bars are
also limited to the visible subset.

**Resolution: a persistent, unobtrusive scope label adjacent to each search bar.**

When a chip filter is active, a small label appears beneath each search bar:

```
[🔍 Search musician…          ]
  ↳ searching all 56 musicians
```

```
[♩ Search composition / raga…]
  ↳ searching all compositions
```

When no chip filter is active, the label is hidden (it is only needed when the visual
state might imply a constraint).

This label is:
- **Persistent** while any chip is active — it does not disappear after a few seconds
- **Unobtrusive** — small font (0.65rem), muted colour (`var(--gray)`), italic
- **Accurate** — it states the actual scope, not a reassurance ("all 56 musicians",
  not just "all musicians")
- **Positioned adjacent to the search bar** — the rasika's eye is already at the
  search bar when they are about to type; the label is in the same visual region

This resolves the false affordance without adding a modal, a tooltip, or a warning
banner. The label is always true and always visible when relevant.

---

### HTML shape — before / after

#### Header (before — per ADR-007 proposed state)

```html
<header>
  <h1>Carnatic · Guru-Shishya Parampara</h1>
  <span class="stats">{node_count} musicians · {edge_count} lineage edges</span>
  <div class="controls">
    <button id="btn-fit">Fit</button>
    <button id="btn-reset">Reset</button>
    <button id="btn-relayout">Relayout</button>
    <button id="btn-labels">Labels</button>
    <button id="btn-timeline">Timeline</button>
  </div>
</header>
```

#### Header (after)

```html
<header>
  <div class="header-top">
    <h1>Carnatic · Guru-Shishya Parampara</h1>
    <span class="stats">{node_count} musicians · {edge_count} lineage edges</span>
    <div class="controls">
      <button id="btn-fit">Fit</button>
      <button id="btn-reset">Reset</button>
      <button id="btn-relayout">Relayout</button>
      <button id="btn-labels">Labels</button>
      <button id="btn-timeline">Timeline</button>
    </div>
  </div>
  <div class="header-filters" id="header-filters">
    <div class="filter-group" id="era-filter-group" data-group="era">
      <!-- chips injected by JS from ERA_COLOURS map -->
    </div>
    <div class="filter-separator"></div>
    <div class="filter-group" id="instr-filter-group" data-group="instrument">
      <!-- chips injected by JS from INSTRUMENT_SHAPES map -->
    </div>
    <button class="filter-clear" id="filter-clear-all"
            style="display:none" title="Clear all filters">&#10005; Show all</button>
  </div>
</header>
```

The chips are injected by JavaScript at page load, iterating over the same
`ERA_COLOURS` and `INSTRUMENT_SHAPES` lookup objects already used by the renderer.
This ensures the chips are always in sync with the data — no hardcoded chip list that
can drift from the actual era/instrument vocabulary.

#### Scope label (added to each search bar's container)

```html
<!-- In left sidebar, Bani Flow panel -->
<div class="search-wrap" id="bani-search-wrap">
  <input id="bani-search-input" … >
  <div id="bani-search-dropdown" … ></div>
  <div class="search-scope-label" id="bani-scope-label" style="display:none">
    searching all compositions
  </div>
</div>

<!-- In right sidebar, above node-info -->
<div class="search-wrap panel-search-wrap" id="musician-search-wrap">
  <input id="musician-search-input" … >
  <div id="musician-search-dropdown" … ></div>
  <div class="search-scope-label" id="musician-scope-label" style="display:none">
    searching all {node_count} musicians
  </div>
</div>
```

The `{node_count}` value is injected by the Python renderer at build time (same as the
stats span in the header). It is a static count — it does not change when chips are
active, which is precisely the point: it reassures the rasika that the full set is
always searched.

---

### CSS additions

```css
/* ── header layout ── */
header {
  display: flex;
  flex-direction: column;
  padding: 8px 14px 0;
  border-bottom: 1px solid var(--bg2);
  flex-shrink: 0;
}
.header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 6px;
}
.header-filters {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-bottom: 6px;
  flex-wrap: wrap;
}

/* ── filter groups ── */
.filter-group {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}
.filter-separator {
  width: 1px;
  height: 14px;
  background: var(--bg3);
  flex-shrink: 0;
  margin: 0 2px;
}

/* ── individual chips ── */
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 7px;
  border-radius: 2px;
  border: 1px solid var(--bg3);
  background: var(--bg1);
  color: var(--fg3);
  font-size: 0.68rem;
  cursor: pointer;
  user-select: none;
  transition: border-color 0.1s, color 0.1s, background 0.1s;
  white-space: nowrap;
}
.filter-chip:hover {
  border-color: var(--fg3);
  color: var(--fg);
}
.filter-chip.active {
  border-color: var(--yellow);
  color: var(--yellow);
  background: var(--bg2);
}
.filter-chip .chip-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
/* instrument shape variants on chip-dot */
.filter-chip .chip-dot.diamond   { transform: rotate(45deg); border-radius: 1px; }
.filter-chip .chip-dot.rectangle { border-radius: 1px; }
.filter-chip .chip-dot.triangle  {
  width: 0; height: 0; background: none !important;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-bottom: 7px solid var(--gray);
}
.filter-chip.active .chip-dot.triangle { border-bottom-color: var(--yellow); }
.filter-chip .chip-dot.hexagon {
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}

/* ── clear-all button ── */
.filter-clear {
  font-size: 0.65rem;
  color: var(--gray);
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 4px;
  margin-left: 4px;
}
.filter-clear:hover { color: var(--fg); }

/* ── scope label ── */
.search-scope-label {
  font-size: 0.65rem;
  color: var(--gray);
  font-style: italic;
  padding: 2px 0 0 2px;
  line-height: 1.3;
}
```

---

### JavaScript additions

#### Chip injection at page load

```javascript
// Called once after cy is initialised.
// ERA_COLOURS and INSTRUMENT_SHAPES are the same lookup objects
// already used by the renderer to colour/shape nodes.

function buildFilterChips() {
  const eraGroup   = document.getElementById('era-filter-group');
  const instrGroup = document.getElementById('instr-filter-group');

  // Era chips — iterate in display order
  const eraOrder = [
    'trinity', 'bridge', 'golden_age', 'disseminator', 'living_pillars', 'contemporary'
  ];
  const eraLabels = {
    trinity:       'Trinity',
    bridge:        'Bridge',
    golden_age:    'Golden Age',
    disseminator:  'Disseminators',
    living_pillars:'Living Pillars',
    contemporary:  'Contemporary',
  };
  eraOrder.forEach(era => {
    const chip = document.createElement('span');
    chip.className   = 'filter-chip';
    chip.dataset.key = era;
    chip.dataset.group = 'era';

    const dot = document.createElement('span');
    dot.className = 'chip-dot ellipse';
    dot.style.background = ERA_COLOURS[era] || 'var(--gray)';

    const label = document.createElement('span');
    label.textContent = eraLabels[era] || era;

    chip.appendChild(dot);
    chip.appendChild(label);
    chip.addEventListener('click', () => toggleFilterChip(chip));
    eraGroup.appendChild(chip);
  });

  // Instrument chips
  const instrOrder = ['vocal', 'veena', 'violin', 'flute', 'mridangam', 'bharatanatyam'];
  const instrLabels = {
    vocal:          'vocal',
    veena:          'veena',
    violin:         'violin',
    flute:          'flute',
    mridangam:      'mridangam',
    bharatanatyam:  'bharatanatyam',
  };
  instrOrder.forEach(instr => {
    const chip = document.createElement('span');
    chip.className   = 'filter-chip';
    chip.dataset.key = instr;
    chip.dataset.group = 'instrument';

    const dot = document.createElement('span');
    const shapeClass = INSTRUMENT_SHAPES[instr] || 'ellipse';
    dot.className = `chip-dot ${shapeClass}`;
    if (shapeClass !== 'triangle') {
      dot.style.background = 'var(--gray)';
    }

    const label = document.createElement('span');
    label.textContent = instrLabels[instr] || instr;

    chip.appendChild(dot);
    chip.appendChild(label);
    chip.addEventListener('click', () => toggleFilterChip(chip));
    instrGroup.appendChild(chip);
  });
}
```

#### Filter state and application

```javascript
// Active filter state — two sets, one per group
const activeFilters = { era: new Set(), instrument: new Set() };

function toggleFilterChip(chip) {
  const group = chip.dataset.group;   // 'era' | 'instrument'
  const key   = chip.dataset.key;

  if (activeFilters[group].has(key)) {
    activeFilters[group].delete(key);
    chip.classList.remove('active');
  } else {
    activeFilters[group].add(key);
    chip.classList.add('active');
  }

  applyChipFilters();
}

function applyChipFilters() {
  const eraActive   = activeFilters.era;
  const instrActive = activeFilters.instrument;
  const anyActive   = eraActive.size > 0 || instrActive.size > 0;

  if (!anyActive) {
    // Restore full graph — remove all chip-filter fading
    cy.elements().removeClass('chip-faded');
    document.getElementById('filter-clear-all').style.display = 'none';
    setScopeLabels(false);
    return;
  }

  // Determine which nodes pass the filter
  cy.nodes().forEach(node => {
    const d = node.data();
    const eraMatch   = eraActive.size   === 0 || eraActive.has(d.era);
    const instrMatch = instrActive.size === 0 || instrActive.has(d.instrument);
    const passes = eraMatch && instrMatch;   // AND across groups, OR within group

    if (passes) {
      node.removeClass('chip-faded');
    } else {
      node.addClass('chip-faded');
    }
  });

  // Dim edges where both endpoints are faded
  cy.edges().forEach(edge => {
    const srcFaded = edge.source().hasClass('chip-faded');
    const tgtFaded = edge.target().hasClass('chip-faded');
    if (srcFaded && tgtFaded) {
      edge.addClass('chip-faded');
    } else {
      edge.removeClass('chip-faded');
    }
  });

  document.getElementById('filter-clear-all').style.display = 'inline';
  setScopeLabels(true);
}

function clearAllChipFilters() {
  activeFilters.era.clear();
  activeFilters.instrument.clear();
  document.querySelectorAll('.filter-chip.active').forEach(c => c.classList.remove('active'));
  cy.elements().removeClass('chip-faded');
  document.getElementById('filter-clear-all').style.display = 'none';
  setScopeLabels(false);
}

function setScopeLabels(visible) {
  const display = visible ? 'block' : 'none';
  document.getElementById('musician-scope-label').style.display = display;
  document.getElementById('bani-scope-label').style.display     = display;
}
```

#### CSS class for chip-faded nodes

```css
/* chip-faded is applied by JS when a chip filter is active.
   It is separate from .faded (used by node-click neighbourhood highlight)
   so the two systems do not interfere. */
.cy-node.chip-faded,
.cy-edge.chip-faded {
  opacity: 0.12;
}
```

In Cytoscape.js stylesheet terms:

```javascript
{
  selector: '.chip-faded',
  style: { opacity: 0.12 }
}
```

**Critical:** `chip-faded` and `faded` are **separate CSS classes**. The node-click
neighbourhood highlight uses `.faded`; the chip filter uses `.chip-faded`. They can
coexist without interference. When a node is both chip-faded and faded (e.g., the
rasika has clicked a node while a chip filter is active), the lower opacity wins
(Cytoscape applies the last matching rule; both set opacity, so the last one in the
stylesheet wins — set `chip-faded` after `faded` in the stylesheet to ensure
`chip-faded` nodes remain at 0.12 even when also `.faded`).

#### Background-tap handler extension

```javascript
cy.on('tap', evt => {
  if (evt.target !== cy) return;
  // Existing: clear node selection
  cy.elements().removeClass('faded highlighted');
  document.getElementById('node-name').textContent        = '—';
  document.getElementById('node-lifespan').textContent    = '';
  document.getElementById('node-wiki-link').style.display = 'none';
  document.getElementById('rec-filter').style.display     = 'none';
  document.getElementById('rec-filter').value             = '';
  document.getElementById('node-info').style.display      = 'block';
  document.getElementById('recordings-panel').style.display = 'none';
  document.getElementById('edge-info').style.display      = 'none';
  // NEW: also clear chip filters
  clearAllChipFilters();
  applyZoomLabels();
});
```

---

### Interaction with existing node-click highlight

When the rasika clicks a node while a chip filter is active, the node-click
neighbourhood highlight (`.faded` / `.highlighted`) is applied on top of the chip
filter state (`.chip-faded`). The two systems are independent:

- `.chip-faded` = "this node does not match the active era/instrument filter"
- `.faded` = "this node is not in the neighbourhood of the selected node"
- `.highlighted` = "this edge is in the neighbourhood of the selected node"

A node can be `.chip-faded` but not `.faded` (it matches the chip filter but is not
in the selected neighbourhood). A node can be `.faded` but not `.chip-faded` (it is
outside the selected neighbourhood but matches the chip filter). The visual result is
that the selected neighbourhood is always visible at full opacity, regardless of chip
filter state — which is the correct behaviour: the rasika's explicit selection always
takes precedence over the passive chip filter.

---

## Consequences

### What this enables

| Query | Before | After |
|---|---|---|
| "Show me all Contemporary musicians" | Mentally scan graph for yellow-green nodes | Click "Contemporary" chip — all others dim instantly |
| "Show me all Contemporary veena players" | Impossible without manual inspection | Click "Contemporary" + "veena" — intersection highlighted |
| "I'm done filtering, show everything" | No explicit affordance | Click active chip, or click background, or click "✕ Show all" |
| "Is the search bar limited to what I see?" | Ambiguous — no indication | Scope label: "searching all 56 musicians" |
| "What does the teal dot mean?" | Read ERA legend in left sidebar | Read chip label in header (same location as the filter action) |

### What this forecloses

- **Left sidebar as legend home** — the ERA and INSTRUMENT legends are removed from
  the left sidebar entirely. The left sidebar becomes a single-purpose Bani Flow
  surface. This is a gain, not a loss.

- **Chip filter + Bani Flow filter simultaneously** — the chip filter dims nodes by
  era/instrument; the Bani Flow filter highlights nodes by lineage thread. If both are
  active simultaneously, the visual result may be confusing (some nodes are highlighted
  by Bani Flow but also chip-faded). 
  
  **Resolution:** When a Bani Flow filter is applied (`applyBaniFilter()` is called),
  automatically clear all chip filters first. When a chip filter is applied
  (`applyChipFilters()`), automatically clear the Bani Flow filter first. The two
  filters are mutually exclusive. This is the correct semantic: the rasika is either
  exploring a lineage thread (Bani Flow) or exploring a demographic slice (era/instrument
  chips) — not both simultaneously.

  The `clearBaniFilter()` function is called at the start of `applyChipFilters()`.
  The `clearAllChipFilters()` function is called at the start of `applyBaniFilter()`.

- **Narrow viewport** — the header filter row may wrap awkwardly on screens < 1100px.
  The `flex-wrap: wrap` on `.header-filters` handles this gracefully: chips wrap to a
  second line rather than overflowing. On very narrow screens (< 800px), the filter row
  can be collapsed behind a toggle button (future work, consistent with the responsive
  design deferred in ADR-003).

### What the Carnatic Coder must implement

All changes are confined to the HTML template string inside [`render_html()`](carnatic/render.py:342)
in [`carnatic/render.py`](carnatic/render.py).

**Edit 1 — Header HTML:**  
Wrap the existing header content in `.header-top`. Add `.header-filters` div with
`#era-filter-group`, `.filter-separator`, `#instr-filter-group`, and `#filter-clear-all`.

**Edit 2 — Left sidebar HTML:**  
Remove the ERA and INSTRUMENT legend panels entirely from the left sidebar.

**Edit 3 — Search bar HTML:**  
Add `#musician-scope-label` and `#bani-scope-label` `<div>` elements inside their
respective `.search-wrap` containers (per ADR-007 proposed positions).

**Edit 4 — CSS:**
Add the `.header-top`, `.header-filters`, `.filter-group`, `.filter-separator`,
`.filter-chip`, `.filter-clear`, `.search-scope-label`, and `.chip-faded` rules
specified in the CSS section above. Remove the old `#era-legend` and
`#instrument-legend` panel rules (the static legend CSS is no longer needed).

**Edit 5 — JS (Cytoscape stylesheet):**
Add the `.chip-faded` selector to the Cytoscape stylesheet array, after the existing
`.faded` selector:

```javascript
{ selector: '.chip-faded', style: { opacity: 0.12 } }
```

**Edit 6 — JS (page load):**
Call `buildFilterChips()` after `cy` is initialised and the node data is loaded.
Add `clearAllChipFilters()` to the `clearBaniFilter()` call chain and vice versa
(mutual exclusion between chip filters and Bani Flow filter).

**Edit 7 — JS (background-tap handler):**
Add `clearAllChipFilters()` call inside the background-tap handler (per the JS
snippet in the Decision section above).

**No data model changes required.** The `era` and `instrument` fields already exist
on every node in [`musicians.json`](carnatic/data/musicians.json). The chips read
directly from the Cytoscape node data at runtime.

---

### What the Librarian must do

**Nothing.** No data changes required. The `era` and `instrument` fields are already
present on every node. The chip vocabulary is derived at runtime from the same
`ERA_COLOURS` and `INSTRUMENT_SHAPES` lookup objects the renderer already uses.

---

## Alternatives Considered

### Alternative 1: Keep legends static in the left sidebar, add a separate "Filter" button

Add a "Filter by era / instrument" button to the header that opens a dropdown or modal
with checkboxes for each era and instrument.

**Rejected.** A modal or dropdown interrupts the immersive flow. The chip row in the
header is always visible — the rasika can filter with a single click without opening
any overlay. The chip row also serves as the legend (the colour dot and label are
visible at all times), so it replaces the static legend without adding a new UI
element.

### Alternative 2: Keep legends in the left sidebar, make them clickable in place

Keep the ERA and INSTRUMENT panels in the left sidebar but make each legend item a
clickable filter chip.

**Rejected.** This solves Problem 2 (static legends) but not Problem 1 (wrong spatial
home). The legends would still be mixed with the Bani Flow panel, creating the
Boundaries failure described above. The left sidebar would remain a mixed-concern
surface. Moving the chips to the header solves both problems simultaneously.

### Alternative 3: Move legends to the right sidebar footer

Place the ERA and INSTRUMENT legends at the bottom of the right sidebar, below the
recordings panel.

**Rejected.** The right sidebar is a **selection-state surface** (per ADR-003 and
ADR-005) — it shows properties of the currently selected node. Era and instrument
legends are graph-level properties, not selection-state properties. Placing them in
the right sidebar would create the same Boundaries failure as the current left sidebar
placement, just in a different location.

### Alternative 4: Floating filter panel (draggable, like the media player)

Make the era/instrument filter a draggable floating panel that the rasika can position
anywhere on the canvas.

**Rejected.** Floating panels are appropriate for transient content (like a video
player). The filter chips are a **persistent graph-level control** — they should have
a fixed, predictable location. Making them draggable adds interaction complexity
without solving the spatial home problem. The header is the correct fixed location.

### Alternative 5: Union logic across groups (era OR instrument)

When both an era chip and an instrument chip are active, show nodes that match
**either** criterion (union), not both (intersection).

**Rejected.** The intersection model ("Contemporary AND veena") is more useful for the
rasika's actual queries. The union model ("Contemporary OR veena") would highlight a
large, unfocused set — nearly as many nodes as the full graph. The rasika who clicks
"Contemporary" and then "veena" is almost certainly asking "which Contemporary
musicians play veena?", not "which musicians are either Contemporary or play veena?".
The intersection model answers the natural question.

---

## Verification

After implementation, verify:

1. **Chips appear in the header** — ERA chips on the left of the separator, INSTRUMENT
   chips on the right. Both groups visible without scrolling on a 1280px-wide screen.

2. **Chip colours and shapes match the graph** — The colour dot on each era chip
   matches the node colour for that era in the graph. The shape icon on each instrument
   chip matches the node shape for that instrument.

3. **Single-group filter works** — Click "Contemporary". All non-Contemporary nodes
   dim to opacity 0.12. Contemporary nodes remain at full opacity. The "Contemporary"
   chip shows active state (yellow border).

4. **Multi-chip within group works** — Click "Contemporary" then "Living Pillars".
   Both Contemporary and Living Pillars nodes are at full opacity. All others dimmed.
   Both chips show active state.

5. **Cross-group intersection works** — Click "Contemporary" (era) then "veena"
   (instrument). Only Contemporary veena players are at full opacity. All others
   dimmed. Both chips show active state.

6. **Deactivation by re-click** — Click an active chip. It deactivates. If it was the
   last active chip, the full graph restores. If other chips remain active, the filter
   updates to reflect the remaining active chips.

7. **"✕ Show all" button** — Appears only when at least one chip is active. Clicking
   it deactivates all chips and restores the full graph. Disappears after clicking.

8. **Background-tap clears chips** — Click the graph background. All chip filters
   clear. Full graph restores. All chips return to inactive state.

9. **Scope labels appear** — When any chip is active, the scope labels appear beneath
   both search bars: "searching all N musicians" and "searching all compositions".
   When no chips are active, the labels are hidden.

10. **Search bars are unaffected by chip filters** — With "Contemporary" chip active
    (most nodes dimmed), type a non-Contemporary musician name in the musician search
    bar. The autocomplete dropdown shows the musician. Selecting them highlights their
    neighbourhood (overriding the chip-faded state for that neighbourhood).

11. **Chip filter and node-click coexist** — With "Contemporary" chip active, click a
    Contemporary node. The node's neighbourhood highlights (`.highlighted` class).
    Non-neighbourhood nodes are `.faded`. The chip-faded state on non-Contemporary
    nodes is still present but visually dominated by `.faded` (both set opacity; the
    result is the same dim appearance). No console errors.

12. **Bani Flow mutual exclusion** — With "Contemporary" chip active, search for a
    composition in the Bani Flow search bar and select it. The chip filters clear
    automatically. The Bani Flow trail highlights. Conversely, with a Bani Flow filter
    active, click an era chip. The Bani Flow filter clears automatically. The chip
    filter applies.

13. **No left sidebar legend panels** — The ERA and INSTRUMENT panels are gone from
    the left sidebar. The left sidebar contains only the Bani Flow panel.

14. **Narrow viewport** — On a 1100px-wide screen, the chip row wraps to a second
    line. No overflow. No horizontal scrollbar.

---

## Queries This Enables

**Rasika query 1:** "I want to see only the Contemporary musicians in the graph — who
are the active practitioners today?"

**Before:** Mentally scan the graph for yellow-green nodes. No direct affordance.

**After:** Click "Contemporary" chip. All other nodes dim. The Contemporary cluster
is immediately visible. Click again to restore.

---

**Rasika query 2:** "I'm interested in the veena tradition specifically. Who are all
the veena players across all eras?"

**Before:** Mentally scan the graph for diamond-shaped nodes. No direct affordance.

**After:** Click "veena" chip. All non-veena nodes dim. The veena lineage thread
becomes visually prominent — the rasika can trace it from the Trinity era through to
Contemporary without distraction.

---

**Rasika query 3:** "Are there any Contemporary veena players? I want to know who is
carrying the veena tradition forward today."

**Before:** Impossible without manual inspection of every Contemporary node.

**After:** Click "Contemporary" + "veena". The intersection is highlighted
immediately. If no nodes remain visible, the answer is "none currently in the graph."

---

**Rasika query 4:** "I've filtered to Contemporary musicians. Can I still search for
Vina Dhanammal (a Golden Age musician) in the search bar?"

**Before:** N/A (no filter existed).

**After:** Yes. The scope label reads "searching all 56 musicians." Type "Dhanammal"
in the musician search bar. The autocomplete shows her. Selecting her highlights her
neighbourhood at full opacity, overriding the chip-faded state. The chip filter
remains active in the background — clicking the background restores both the chip
filter state and the full graph.

---

## Implementation Priority

**High.** This ADR resolves a structural problem (legends in the wrong spatial home),
a usability problem (static legends that could be interactive), and a design tension
(scope ambiguity when nodes are dimmed). All three are resolved by a single coherent
change: move the legend chips to the header and make them functional.

The scope label is the critical safety mechanism. Without it, the chip filter creates
a false affordance that could mislead the rasika into thinking their search is limited.
The label must be implemented in the same commit as the chip filter — they are a single
design unit, not two separate features.

Recommend implementing after ADR-007 (search bar colocation), since the scope labels
are positioned adjacent to the search bars and share their CSS context.
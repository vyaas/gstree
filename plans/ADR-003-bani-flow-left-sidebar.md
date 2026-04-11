# ADR-003: Move Bani Flow to Left Sidebar for Visual Clarity

**Status:** Proposed  
**Date:** 2026-04-09

---

## Context

The Bani Flow panel currently sits at the bottom of the right sidebar, directly beneath the "Concert Performances" section. This creates three problems:

1. **Visual ambiguity** - It appears to be part of the selected node's properties, when in fact it is a **global graph filter** that operates independently of node selection
2. **Insufficient space** - Compressed at the bottom of a scrollable sidebar, the listening trail is cramped and hard to scan
3. **Cognitive load** - The rasika must mentally separate "properties of this node" from "global filter state" within the same visual container

### Current Layout (Right Sidebar, Top to Bottom)

```
┌─────────────────────────┐
│ SELECTED                │  ← Node properties
│ MS Subbulakshmi         │
│ 1916-2004               │
│ Disseminators           │
│ vocal · dhanammal       │
│ Wikipedia ↗             │
├─────────────────────────┤
│ RECORDINGS ▶            │  ← Node-specific
│ • Track 1               │
│ • Track 2               │
├─────────────────────────┤
│ CONCERT PERFORMANCES 🎧 │  ← Node-specific
│ • Performance 1         │
│ • Performance 2         │
├─────────────────────────┤
│ BANI FLOW ♪             │  ← GLOBAL FILTER (misplaced!)
│ [Search box]            │
│ Listening trail...      │
├─────────────────────────┤
│ ERA                     │  ← Legend (static)
│ • Trinity               │
│ • Bridge                │
│ ...                     │
├─────────────────────────┤
│ INSTRUMENT              │  ← Legend (static)
│ • vocal                 │
│ • veena                 │
│ ...                     │
└─────────────────────────┘
```

The Bani Flow panel is **semantically global** but **visually local** - it looks like it belongs to the selected node, but it actually controls the entire graph's highlighting state.

---

## Pattern

This resolves a **Boundaries** pattern failure. Christopher Alexander teaches that boundaries must be clear and strong where two centres of different character meet. Here we have two distinct centres:

1. **The selected node centre** - transient, changes with every click, shows properties of *one* musician
2. **The Bani Flow centre** - persistent, independent of selection, shows the *lineage* of a composition or raga across the entire parampara

These two centres must be **spatially separated** to avoid confusion. The boundary between them must be architectural, not just a thin dividing line.

Additionally, this resolves a **Strong Centres** failure. The Bani Flow is a **primary immersion tool** - it is how the rasika traces a composition's transmission through the parampara. It deserves its own dedicated space, not a cramped footer position.

---

## Decision

**Create a left sidebar dedicated to global graph controls and legends. Move Bani Flow there.**

### Proposed Three-Column Layout

```
┌──────────────┬─────────────────────────────┬──────────────────────────┐
│              │                             │                          │
│  LEFT        │      GRAPH CANVAS           │    RIGHT SIDEBAR         │
│  SIDEBAR     │                             │                          │
│              │                             │                          │
│  (Global)    │      (Cytoscape)            │    (Node-specific)       │
│              │                             │                          │
└──────────────┴─────────────────────────────┴──────────────────────────┘
```

### Left Sidebar Contents (Top to Bottom)

```
┌─────────────────────────┐
│ BANI FLOW ♪             │  ← MOVED HERE (global filter)
│ [Search composition/    │
│  raga...]               │
│ ✕ Clear filter          │
│                         │
│ Listening Trail:        │
│ Composed by X · Raga Y  │
│ • 1965 Artist A         │
│ • 1972 Artist B         │
│ • 1989 Artist C         │
│ ...                     │
├─────────────────────────┤
│ ERA                     │  ← Legend (static)
│ • Trinity               │
│ • Bridge                │
│ • Golden Age            │
│ • Disseminators         │
│ • Living Pillars        │
│ • Contemporary          │
├─────────────────────────┤
│ INSTRUMENT              │  ← Legend (static)
│ • vocal                 │
│ • veena                 │
│ • violin                │
│ • flute                 │
│ • mridangam             │
└─────────────────────────┘
```

### Right Sidebar Contents (Top to Bottom)

```
┌─────────────────────────┐
│ SELECTED                │  ← Node properties
│ MS Subbulakshmi         │
│ 1916-2004               │
│ Disseminators           │
│ vocal · dhanammal       │
│ Wikipedia ↗             │
├─────────────────────────┤
│ RECORDINGS ▶            │  ← Node-specific
│ • Track 1               │
│ • Track 2               │
├─────────────────────────┤
│ CONCERT PERFORMANCES 🎧 │  ← Node-specific
│ • Performance 1         │
│ • Performance 2         │
├─────────────────────────┤
│ SELECTED EDGE           │  ← Edge properties (when edge clicked)
│ Guru → Shishya          │
│ confidence: 95%         │
│ source ↗                │
└─────────────────────────┘
```

### Visual Hierarchy Achieved

- **Left** = "What am I filtering?" (global state)
- **Centre** = "What am I looking at?" (the graph itself)
- **Right** = "What did I click?" (transient selection)

---

## Consequences

### Positive

1. **Clear semantic separation** - Global controls (Bani Flow, legends) are visually distinct from node-specific properties
2. **More space for listening trail** - The left sidebar can be wider (e.g., 280px vs. current 240px) and dedicated entirely to the chronological listening experience
3. **Persistent visibility** - Legends are always visible without scrolling, even when a node with many recordings is selected
4. **Symmetry** - The graph canvas is now flanked by two sidebars of roughly equal width, creating visual balance
5. **Scalability** - Future global controls (e.g., "Filter by Era", "Filter by Bani", "Timeline Scrubber") have a natural home in the left sidebar

### Negative

1. **Horizontal space cost** - The graph canvas loses ~240px of width (left sidebar). On a 1920px screen, this reduces the canvas from ~1680px to ~1440px
   - **Mitigation**: The canvas is still ample. The graph is zoomable and pannable. The trade-off is worth it for the clarity gained.

2. **Implementation complexity** - Requires restructuring the CSS grid/flexbox layout
   - **Mitigation**: The HTML structure is already modular (panels are independent divs). This is primarily a CSS change, not a data model change.

3. **Mobile/narrow screens** - A three-column layout may not work on screens <1200px wide
   - **Mitigation**: Add a CSS media query to collapse the left sidebar on narrow screens, moving Bani Flow back to the right sidebar (or into a collapsible drawer). This ADR addresses the desktop experience; responsive design is a separate concern.

### What the Carnatic Coder Must Implement

#### 1. HTML Structure Changes ([`carnatic/render.py`](carnatic/render.py:699))

**Current:**
```html
<div id="main">
  <div id="cy"></div>
  <svg id="timeline-ruler">...</svg>
  <div id="hover-popover">...</div>
  <div id="sidebar">...</div>  <!-- Right sidebar -->
</div>
```

**New:**
```html
<div id="main">
  <div id="left-sidebar">
    <div class="panel" id="bani-flow-panel">...</div>
    <div class="panel" id="era-legend">...</div>
    <div class="panel" id="instrument-legend">...</div>
  </div>
  
  <div id="cy"></div>
  <svg id="timeline-ruler">...</svg>
  <div id="hover-popover">...</div>
  
  <div id="right-sidebar">
    <div class="panel" id="node-info">...</div>
    <div class="panel" id="track-panel">...</div>
    <div class="panel" id="perf-panel">...</div>
    <div class="panel" id="edge-info">...</div>
  </div>
</div>
```

#### 2. CSS Changes ([`carnatic/render.py`](carnatic/render.py:420))

**Current:**
```css
#main { display: flex; flex: 1; overflow: hidden; position: relative; }
#cy   { flex: 1; background: var(--bg); }
#sidebar {
  width: 240px; background: var(--bg1);
  border-left: 1px solid var(--bg2);
  display: flex; flex-direction: column;
  overflow-y: auto; font-size: 0.78rem;
}
```

**New:**
```css
#main { 
  display: flex; 
  flex: 1; 
  overflow: hidden; 
  position: relative; 
}

#left-sidebar {
  width: 280px; 
  background: var(--bg1);
  border-right: 1px solid var(--bg2);
  display: flex; 
  flex-direction: column;
  overflow-y: auto; 
  font-size: 0.78rem;
  flex-shrink: 0;
}

#cy { 
  flex: 1; 
  background: var(--bg); 
}

#right-sidebar {
  width: 240px; 
  background: var(--bg1);
  border-left: 1px solid var(--bg2);
  display: flex; 
  flex-direction: column;
  overflow-y: auto; 
  font-size: 0.78rem;
  flex-shrink: 0;
}
```

#### 3. Move Bani Flow Panel HTML

Extract the Bani Flow panel from the right sidebar and place it as the first child of `#left-sidebar`. No changes to the panel's internal HTML structure are needed.

#### 4. Move Legend Panels HTML

Extract the ERA and INSTRUMENT legend panels from the right sidebar and place them in `#left-sidebar` after the Bani Flow panel.

#### 5. Remove Hint Panel

The current "hint" panel at the bottom of the right sidebar can be removed or moved to a footer/tooltip. It is instructional text that does not need persistent visibility once the user is familiar with the interface.

#### 6. Optional: Add Collapsible Sidebar Toggles

Add small toggle buttons (e.g., `◀` / `▶`) to collapse/expand each sidebar independently. This is a nice-to-have for users who want maximum canvas space.

### What the Librarian Must Do

**Nothing.** This is a pure UI restructuring. No data changes required.

---

## Alternatives Considered

### Alternative 1: Keep Bani Flow in Right Sidebar, Add Visual Separator

Add a thick horizontal divider and a background color change to visually separate Bani Flow from node properties.

**Rejected.** This is a cosmetic fix that does not address the semantic confusion. The Bani Flow would still *appear* to be part of the node properties, just with a divider. The spatial separation of a dedicated sidebar is architecturally clearer.

### Alternative 2: Make Bani Flow a Floating Panel

Turn Bani Flow into a draggable floating panel (like the media player) that can be positioned anywhere on the canvas.

**Rejected.** Floating panels are appropriate for transient content (like a video player). Bani Flow is a **persistent control** that should have a fixed, predictable location. Making it draggable would add interaction complexity without solving the core problem.

### Alternative 3: Move Bani Flow to the Header

Place the Bani Flow search box in the header, next to the existing musician/composition search boxes. Show the listening trail in a dropdown or modal.

**Rejected.** The listening trail is a **primary immersion experience** - it is not auxiliary information that should be hidden in a dropdown. The rasika needs to see the chronological flow of performances while navigating the graph. A sidebar provides persistent visibility.

### Alternative 4: Tabbed Right Sidebar

Add tabs to the right sidebar: "Node Properties" | "Bani Flow" | "Legends". Only one tab visible at a time.

**Rejected.** This forces the rasika to choose between seeing node properties and seeing the Bani Flow trail. The whole point of the Bani Flow is to **highlight nodes while you navigate** - hiding the node properties defeats the purpose. Both must be visible simultaneously.

---

## Verification

After implementing this change, verify:

1. **Visual separation is clear** - A new user should immediately understand that the left sidebar controls the graph, while the right sidebar shows details of the current selection
2. **Bani Flow has more space** - The listening trail should be easier to scan, with less vertical scrolling required
3. **Legends are always visible** - Scrolling the right sidebar (e.g., when a node has many recordings) should not hide the ERA/INSTRUMENT legends
4. **No layout breakage** - The graph canvas should remain fully interactive, with no overlapping elements
5. **Responsive behavior** - On screens <1200px wide, the left sidebar should collapse or stack vertically (future work; not required for initial implementation)

---

## Query This Enables

**Rasika query:** "I want to explore the Dhanammal bani's treatment of Kalyani raga across three generations, while also seeing each musician's full biography and recordings."

**Before this fix:** Possible, but cognitively taxing. The rasika must scroll the right sidebar to see the Bani Flow trail, losing sight of the node properties. The visual mixing of global and local state creates friction.

**After this fix:** Natural. The left sidebar shows the Kalyani listening trail (chronological, always visible). The rasika clicks each musician in the trail; the right sidebar updates with that musician's properties. The graph highlights the lineage connections. The three information streams (trail, properties, graph) are spatially distinct and simultaneously visible.

This is the **immersion pattern** working at full strength: the rasika can lose themselves in the music, following a thread from composition to lineage to recording, without fighting the interface.

---

## Implementation Priority

**High.** This is a **core usability fix** that directly serves the rasika's immersion. The current layout creates confusion about what Bani Flow controls. The fix is architecturally clean (no data model changes) and scales forward (future global controls have a natural home).

Recommend implementing before adding new features (e.g., lesson nodes, institutional affiliations) to avoid compounding the layout confusion.

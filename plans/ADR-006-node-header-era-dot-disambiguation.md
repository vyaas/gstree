# ADR-006: Unified Coloured Shape Icon — One Icon Encodes Both Era and Instrument

**Status:** Accepted
**Date:** 2026-04-11

---

## Context

The right sidebar node header and the Bani Flow trail both display a small visual
indicator next to each musician's name. After ADR-004 was implemented, each musician
entry shows **two** icons side by side:

```
● ○  Malladi Brothers    b. 1962
```

- `●` — a filled circle, coloured by era (e.g. olive-green for Contemporary)
- `○` — a grey shape icon, shaped by instrument (e.g. ellipse for vocal)

For vocal musicians (the majority of nodes), both icons are circles. The user cannot
distinguish which circle encodes era and which encodes instrument. The two-icon
vocabulary is internally inconsistent: it uses *two separate visual channels* to
communicate what the Cytoscape node already communicates with *one* — a single shape
whose fill colour is the era colour.

The Cytoscape node for Malladi Brothers in the main panel is:
- **Shape:** ellipse (vocal)
- **Fill colour:** `#98971a` (contemporary)

That single node is unambiguous. The sidebar should mirror it.

The left sidebar legend is already correct and does not need to change:
- The **ERA** section shows coloured circles (one per era) — explaining the colour channel
- The **INSTRUMENT** section shows grey shapes (one per instrument) — explaining the shape channel

These are *reference panels*, not data representations. They correctly separate the two
dimensions for explanation. The data representations (node header, trail entries) should
*combine* them into one icon, as the graph does.

---

## Pattern

**Strong Centres** (Alexander Pattern 1) — each musician entry in the sidebar and trail
is a centre. A strong centre must be self-consistent. Two grey/coloured circles next to
each other are a *weak* centre: the user must decode two separate icons to understand
one musician. A single coloured shape is a *strong* centre: it is the musician's visual
identity, identical to their node in the graph.

**Levels of Scale** (Alexander Pattern 5) — the graph has three scales at which a
musician appears:
1. The **Cytoscape node** in the main panel — coloured shape
2. The **trail entry** in the Bani Flow panel — currently two icons
3. The **node header** in the right sidebar — currently two icons

Good structure at every level reinforces good structure at every other level. Scales 2
and 3 should use the same visual vocabulary as Scale 1.

**Correspondence** — the user's governing question when scanning the sidebar is
*"is this the same musician I see in the graph?"* A single coloured shape answers that
question instantly. Two separate icons require a two-step decode.

---

## Decision

### Replace two icons with one coloured shape icon everywhere a musician is represented
outside the main graph panel.

The single icon:
- **Shape** — determined by `instrument` (ellipse, diamond, rectangle, triangle, hexagon)
- **Fill colour** — determined by `era` (the same hex values as `ERA_COLORS` in
  [`carnatic/render.py`](carnatic/render.py:22))

This is exactly what the Cytoscape node already is.

---

### Change 1 — Right sidebar node header

#### Current HTML structure (lines 793–796 of [`carnatic/render.py`](carnatic/render.py:793))

```html
<span id="node-era-dot"   class="node-era-dot"></span>
<span id="node-instr-icon" class="node-instr-icon ellipse"></span>
<span id="node-name">—</span>
```

#### Proposed HTML structure

```html
<span id="node-shape-icon" class="node-shape-icon ellipse"></span>
<span id="node-name">—</span>
```

One element. Shape class set by instrument. Background colour set by era.

#### Current CSS (lines 460–478 of [`carnatic/render.py`](carnatic/render.py:460))

```css
.node-era-dot {
  width: 8px; height: 8px; border-radius: 50%;
  display: inline-block; flex-shrink: 0;
}
.node-instr-icon {
  width: 8px; height: 8px; display: inline-block;
  background: var(--gray); flex-shrink: 0;
}
.node-instr-icon.ellipse   { border-radius: 50%; }
.node-instr-icon.diamond   { transform: rotate(45deg); border-radius: 1px; }
.node-instr-icon.rectangle { border-radius: 1px; }
.node-instr-icon.triangle  {
  width: 0; height: 0; background: none;
  border-left: 4px solid transparent; border-right: 4px solid transparent;
  border-bottom: 8px solid var(--gray);
}
.node-instr-icon.hexagon {
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}
```

#### Proposed CSS

```css
/* Single coloured shape — shape = instrument, colour = era */
.node-shape-icon {
  width: 10px; height: 10px; display: inline-block;
  flex-shrink: 0;
  /* background-color set dynamically via JS: d.color */
}
.node-shape-icon.ellipse   { border-radius: 50%; }
.node-shape-icon.diamond   { transform: rotate(45deg); border-radius: 1px; }
.node-shape-icon.rectangle { border-radius: 1px; }
.node-shape-icon.triangle  {
  width: 0; height: 0; background: none !important;
  border-left: 5px solid transparent; border-right: 5px solid transparent;
  border-bottom: 10px solid var(--gray); /* overridden by JS for triangle */
}
.node-shape-icon.hexagon {
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}
```

Note: `triangle` uses CSS borders for its shape, so `background-color` has no effect.
The JS must set `border-bottom-color` instead of `background` for triangle nodes.
All other shapes use `background-color`.

#### Current JS in `selectNode()` (lines 1255–1259 of [`carnatic/render.py`](carnatic/render.py:1255))

```javascript
const eraDot = document.getElementById('node-era-dot');
eraDot.style.background = d.color || 'var(--gray)';

const instrIcon = document.getElementById('node-instr-icon');
instrIcon.className = 'node-instr-icon ' + (d.shape || 'ellipse');
```

#### Proposed JS in `selectNode()`

```javascript
const shapeIcon = document.getElementById('node-shape-icon');
shapeIcon.className = 'node-shape-icon ' + (d.shape || 'ellipse');
if (d.shape === 'triangle') {
  shapeIcon.style.borderBottomColor = d.color || 'var(--gray)';
  shapeIcon.style.background = '';
} else {
  shapeIcon.style.background = d.color || 'var(--gray)';
  shapeIcon.style.borderBottomColor = '';
}
```

---

### Change 2 — Bani Flow trail entries

#### Current structure (lines 1690–1701 of [`carnatic/render.py`](carnatic/render.py:1690))

```javascript
if (row.color) {
  const colorDot = document.createElement('span');
  colorDot.className = 'trail-color-dot';
  colorDot.style.background = row.color;
  artistSpan.appendChild(colorDot);
}

if (row.shape) {
  const shapeIcon = document.createElement('span');
  shapeIcon.className = `trail-shape-icon ${row.shape}`;
  artistSpan.appendChild(shapeIcon);
}
```

#### Proposed structure

```javascript
if (row.color || row.shape) {
  const shapeIcon = document.createElement('span');
  shapeIcon.className = `trail-shape-icon ${row.shape || 'ellipse'}`;
  if ((row.shape || 'ellipse') === 'triangle') {
    shapeIcon.style.borderBottomColor = row.color || 'var(--gray)';
  } else {
    shapeIcon.style.background = row.color || 'var(--gray)';
  }
  artistSpan.appendChild(shapeIcon);
}
```

One element appended, not two.

#### CSS — remove `.trail-color-dot`, keep `.trail-shape-icon` unchanged

The `.trail-color-dot` class (lines 670–673 of [`carnatic/render.py`](carnatic/render.py:670))
is no longer needed and should be removed:

```css
/* REMOVE THIS ENTIRE RULE */
.trail-color-dot {
  width: 8px; height: 8px; border-radius: 50%;
  display: inline-block; margin-right: 4px; vertical-align: middle; flex-shrink: 0;
}
```

The `.trail-shape-icon` rules remain exactly as they are. The only change is that the
icon now receives a dynamic `background` (or `border-bottom-color` for triangle) from JS
instead of the static `var(--gray)`.

---

### What does NOT change

| Element | Status | Reason |
|---|---|---|
| Left sidebar ERA legend | **No change** | Coloured circles are correct — they explain the colour channel in isolation |
| Left sidebar INSTRUMENT legend | **No change** | Grey shapes are correct — they explain the shape channel in isolation |
| Cytoscape node styles | **No change** | Already correct |
| Hover popover | **No change** | Text-only, no icons |
| Edge info panel | **No change** | No musician icons |
| Search dropdown results | **No change** | Uses `primaryColor` on text, not shape icons |

---

## Before / After

### Right sidebar node header

**Before:**
```
● ○  Malladi Brothers    b. 1962   ↗
```
Two icons: olive-green circle (era) + grey circle (instrument). For vocal musicians,
indistinguishable.

**After:**
```
●  Malladi Brothers    b. 1962   ↗
```
One olive-green circle. Shape = ellipse (vocal). Colour = `#98971a` (contemporary).
Identical to the Malladi Brothers node in the main graph.

### Bani Flow trail entry

**Before:**
```
● ○  Malladi Brothers              b. 1962
     Entharo Mahanubhavulu          00:00 ↗
```

**After:**
```
●  Malladi Brothers                b. 1962
   Entharo Mahanubhavulu            00:00 ↗
```

For a veena player (Vina Dhanammal):

**Before:**
```
● ◆  Vina Dhanammal               1867–1938
     Intha Chalamu                  00:00 ↗
```

**After:**
```
◆  Vina Dhanammal                 1867–1938
   Intha Chalamu                    00:00 ↗
```

The diamond is now yellow-orange (`#d65d0e`, bridge era) — the same colour as the
Vina Dhanammal node in the graph.

---

## Consequences

### Positive

1. **Visual correspondence** — the icon in the sidebar is the musician's node in
   miniature. The rasika's eye moves from the sidebar to the graph and back without
   re-learning a visual vocabulary.
2. **Reduced clutter** — one icon instead of two. The node header line is less crowded.
3. **Correct information density** — shape and colour are two orthogonal channels; one
   icon can carry both simultaneously. Two icons was redundant encoding.
4. **Consistency with the legend** — the legend already teaches "colour = era, shape =
   instrument". The single icon is the natural application of that lesson to a data point.

### Negative / Costs

1. **Triangle special-casing** — CSS triangles use `border-bottom-color`, not
   `background-color`. The JS must branch on `shape === 'triangle'`. This is a minor
   implementation detail, not a structural cost. Currently there is one triangle
   instrument (`flute`).
2. **Migration** — the HTML template in [`carnatic/render.py`](carnatic/render.py:793)
   must remove `node-era-dot` and rename `node-instr-icon` to `node-shape-icon`. The
   `selectNode()` JS function must be updated. The trail rendering block must be
   collapsed from two `appendChild` calls to one. No data model changes required.

### What the Carnatic Coder must implement

Three surgical edits to [`carnatic/render.py`](carnatic/render.py):

**Edit 1 — HTML template, node header (line ~794):**
Remove `<span id="node-era-dot" ...>` and `<span id="node-instr-icon" ...>`.
Add `<span id="node-shape-icon" class="node-shape-icon ellipse"></span>`.

**Edit 2 — CSS, node header styles (lines ~460–478):**
Remove `.node-era-dot` and `.node-instr-icon` rule blocks.
Add `.node-shape-icon` rule block (shape variants + no default background colour).

**Edit 3 — CSS, trail styles (lines ~670–673):**
Remove `.trail-color-dot` rule block.
`.trail-shape-icon` rules remain; remove the `background: var(--gray)` default from the
base rule (colour is now set dynamically by JS, not by CSS default).

**Edit 4 — JS, `selectNode()` function (lines ~1255–1259):**
Replace the two-element update (eraDot + instrIcon) with the single-element update
(shapeIcon, with triangle branch).

**Edit 5 — JS, `buildListeningTrail()` trail rendering (lines ~1690–1701):**
Collapse the two `if (row.color)` / `if (row.shape)` blocks into one block that creates
a single `trail-shape-icon` element with dynamic colour.

### What the Librarian must do

Nothing. No data model changes. `era` and `instrument` fields are already present on
every node.

---

## Alternatives Considered

### Alternative 1: Keep two icons, change the era dot to a non-circle shape

Make the era dot a small square instead of a circle, so it is visually distinct from the
instrument ellipse for vocal musicians.

**Rejected.** This is a patch on a structural problem. The era dot and instrument icon
are still two separate elements encoding two dimensions that one element can encode. The
result is still more cluttered than the graph node it is supposed to represent.

### Alternative 2: Remove the instrument icon entirely, keep only the era dot

Show only the era colour, drop the instrument shape.

**Rejected.** Instrument is a meaningful dimension — the rasika distinguishes vocalists
from veena players from mridangam players at a glance in the graph. Dropping it from the
sidebar would create an information asymmetry between the graph and the sidebar.

### Alternative 3: Show the era colour as a left border on the node header row

Use a 3px left border on the `#node-info` panel, coloured by era, instead of an icon.

**Rejected.** A border does not encode instrument. It solves the disambiguation problem
for vocal musicians (no more two circles) but loses the instrument dimension entirely.
The single coloured shape is strictly superior: it encodes both dimensions and matches
the graph node.

### Alternative 4: Use a coloured text label ("vocal", "contemporary") instead of an icon

**Rejected.** Text labels are verbose and break the visual scanning rhythm. The rasika
learns the colour/shape vocabulary from the legend once; thereafter the icons are
instantly decoded without reading. Text labels require reading every time.

---

## Query This Enables

**Rasika query:** "I've clicked on a node in the graph — a teal diamond. I look at the
sidebar. Does the sidebar confirm I'm looking at a Golden Age veena player?"

**Before:** The sidebar shows a teal circle (era) and a grey diamond (instrument) — two
separate icons that must be mentally combined.

**After:** The sidebar shows a teal diamond — the same visual object as the node I just
clicked. Confirmation is instant and requires no mental combination.

This is the **correspondence pattern** at its simplest: the miniature in the sidebar is
the node in the graph. One look is enough.

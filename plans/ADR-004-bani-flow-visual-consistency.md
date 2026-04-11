# ADR-004: Bani Flow Visual Consistency, Metadata Display, and Rapid Sharing

**Status:** Accepted
**Date:** 2026-04-11
**Implemented:** 2026-04-11

---

## Context

The Bani Flow listening trail (left sidebar) and the Concert Performances panel (right sidebar) both display recordings, but they present musician metadata inconsistently. This creates three problems that fragment the rasika's immersion:

### Problem 1: Inconsistent Date Display

**In the Bani Flow trail** (screenshot 1, left sidebar):
- Some entries show a year: `1932 Vina Dhanammal`
- Others show no date: `T. Brinda`, `Ramnad Krishnan`

**In the Concert Performances panel** (screenshot 2, right sidebar):
- The recording title shows the event date: `"Srinivasa Farms Concert, Poonamallee 1965"`
- Individual performances show no date metadata

**The inconsistency:** The year shown in Bani Flow is the **recording year** (from `youtube[].year` or `recordings[].date`), which may be absent. But what the rasika actually needs to orient themselves in the parampara is the **musician's lifespan** (birth–death years), which is *always* present in the data model.

### Problem 2: Inconsistent Presentation Between Bani Flow and Recordings

**In the Bani Flow trail:**
```
1932 Vina Dhanammal
     Intha Chalamu
```

**In the Concert Performances panel:**
```
abhimanamemnedu
Begada · adi · Srinivasa Farms Concert, Poonamallee 1965    1:02:50 ↗
```

The Bani Flow shows:
- Year (if available)
- Artist name (clickable)
- Composition title (indented)
- **No direct YouTube link**

The Concert Performances panel shows:
- Composition title (bold)
- Raga · tala · recording title (smaller text)
- **Timestamp link with YouTube icon** (`1:02:50 ↗`)

**The inconsistency:** These are both lists of performances, but they use completely different visual structures. More critically, the Bani Flow trail lacks the **direct YouTube link** that appears in the Concert Performances panel. This creates a workflow friction:

**Current workflow to share a Bani Flow result:**
1. Search for a raga/composition in Bani Flow
2. See the listening trail with multiple performances
3. Click an artist name to select them
4. Scroll the right sidebar to find the same composition in "Concert Performances"
5. Right-click the YouTube link to copy/share

**This is a two-step process** when it should be one step. The rasika must navigate away from the trail to get the shareable link, breaking immersion and making rapid sharing impossible.

### Problem 3: Insufficient Metadata in Musician List

**In the Bani Flow trail** (screenshot 1, left sidebar), the musician names appear as plain text:
```
Vina Dhanammal
Intha Chalamu
T. Brinda
Vala Padare
Ramnad Krishnan
abhimanamemnedu
```

**What's missing:**
- No visual indication of **era** (color)
- No visual indication of **instrument** (shape)
- No lifespan to orient the musician in time

When a musician name appears in the trail, the rasika cannot tell at a glance:
- Is this a Trinity-era figure or a contemporary artist?
- Are they a vocalist or an instrumentalist?
- When did they live?

This forces the rasika to click each name to see the full node metadata in the right sidebar, breaking the flow of exploration.

---

## Pattern

This resolves three Alexander patterns:

### 1. **Strong Centres** (Pattern 1)

Each musician entry in the Bani Flow trail is a **centre** in the graph. A strong centre must carry enough information to be meaningful on its own, without requiring the rasika to click through to another view.

Currently, the musician name is a **weak centre** - it is just a label, with no visual or temporal context. The rasika must leave the trail to understand who this person is.

### 2. **Levels of Scale** (Pattern 5)

The graph has multiple levels of scale:
- The **parampara as a whole** (the full graph)
- The **bani or raga lineage** (the Bani Flow trail)
- The **individual musician** (the right sidebar)
- The **individual recording** (the performance entry)

Good structure at every level reinforces good structure at every other level. Currently, the **recording level** has two different structures (Bani Flow vs. Concert Performances), which creates dissonance. The rasika must learn two different visual languages for the same data.

### 3. **Gradients** (Pattern 9)

A gradient is a smooth transition between two states. The transition from "browsing the Bani Flow trail" to "selecting a musician" should be seamless - the metadata shown in the trail should be a **subset** of the metadata shown in the full node view, not a completely different presentation.

Currently, there is a **discontinuity**: the trail shows only the name, while the node view shows lifespan, era, instrument, and bani. The rasika experiences a jarring shift when clicking a name.

### 4. **Accessibility** (Pattern 51)

Every important action should be accessible from every relevant context. The action "share this recording on YouTube" is important (it enables collaborative listening, research, and teaching). It should be accessible from the Bani Flow trail, not just from the Concert Performances panel.

Currently, the YouTube link is **hidden behind a selection step**. The rasika must click the artist, then find the performance again in a different panel. This violates the accessibility pattern.

---

## Decision

### Change 1: Always Show Lifespan in Bani Flow Trail

**Replace the recording year with the musician's lifespan.**

#### Current Rendering (lines 1501-1507 in [`carnatic/render.py`](carnatic/render.py:1501))

```javascript
const yearSpan = document.createElement('span');
yearSpan.className = 'trail-year';
yearSpan.textContent = row.track.year || '';

const artistSpan = document.createElement('span');
artistSpan.className = 'trail-artist';
artistSpan.textContent = row.artistLabel;
```

#### Proposed Rendering

```javascript
const lifespanSpan = document.createElement('span');
lifespanSpan.className = 'trail-lifespan';
lifespanSpan.textContent = row.lifespan || '';  // e.g. "1916–2004" or "b. 1984"

const artistSpan = document.createElement('span');
artistSpan.className = 'trail-artist';
artistSpan.textContent = row.artistLabel;
```

#### Data Model Change

The `buildListeningTrail` function (line 1397) must pass the musician's `lifespan` field (already computed in `build_elements`, line 272) to each row:

```javascript
rows.push({ 
  nodeId: nid, 
  artistLabel: d.label, 
  born: d.born, 
  lifespan: d.lifespan,  // ADD THIS
  track: t, 
  isStructured: false 
});
```

For structured recordings where the musician is matched:

```javascript
rows.push({
  nodeId,
  artistLabel,
  born,
  lifespan: pNode ? pNode.data('lifespan') : null,  // ADD THIS
  track: { ... },
  isStructured: true,
});
```

#### CSS Change (line 637)

```css
/* OLD */
.trail-year { flex-shrink: 0; color: var(--gray); font-size: 0.68rem; min-width: 30px; margin-top: 2px; }

/* NEW */
.trail-lifespan { flex-shrink: 0; color: var(--gray); font-size: 0.68rem; min-width: 80px; margin-top: 2px; }
```

The `min-width` increases from `30px` (enough for a 4-digit year) to `80px` (enough for `"1916–2004"`).

#### Visual Result

**Before:**
```
1932 Vina Dhanammal
     Intha Chalamu
     T. Brinda
     Vala Padare
1965 Ramnad Krishnan
     abhimanamemnedu
```

**After:**
```
1867–1938  Vina Dhanammal
           Intha Chalamu
1896–1996  T. Brinda
           Vala Padare
1918–1973  Ramnad Krishnan
           abhimanamemnedu
```

Every entry now has a temporal anchor. The rasika can immediately see that Vina Dhanammal and T. Brinda span a century, while Ramnad Krishnan is mid-20th century.

---

### Change 2: Add Era Color and Instrument Shape to Bani Flow Trail

**Show the musician's era color and instrument shape next to their name.**

#### Proposed Rendering (line 1505)

```javascript
const artistSpan = document.createElement('span');
artistSpan.className = 'trail-artist';

// Add era color dot
const colorDot = document.createElement('span');
colorDot.className = 'trail-color-dot';
colorDot.style.background = row.color || 'var(--gray)';

// Add instrument shape icon
const shapeIcon = document.createElement('span');
shapeIcon.className = `trail-shape-icon ${row.shape || 'ellipse'}`;

artistSpan.appendChild(colorDot);
artistSpan.appendChild(shapeIcon);
artistSpan.appendChild(document.createTextNode(row.artistLabel));
```

#### Data Model Change

The `buildListeningTrail` function must pass `color` and `shape` from the node data:

```javascript
rows.push({ 
  nodeId: nid, 
  artistLabel: d.label, 
  born: d.born, 
  lifespan: d.lifespan,
  color: d.color,      // ADD THIS
  shape: d.shape,      // ADD THIS
  track: t, 
  isStructured: false 
});
```

For structured recordings:

```javascript
rows.push({
  nodeId,
  artistLabel,
  born,
  lifespan: pNode ? pNode.data('lifespan') : null,
  color: pNode ? pNode.data('color') : null,      // ADD THIS
  shape: pNode ? pNode.data('shape') : null,      // ADD THIS
  track: { ... },
  isStructured: true,
});
```

#### CSS Addition (after line 640)

```css
.trail-color-dot {
  width: 8px; 
  height: 8px; 
  border-radius: 50%; 
  display: inline-block; 
  margin-right: 4px;
  vertical-align: middle;
}

.trail-shape-icon {
  width: 8px; 
  height: 8px; 
  display: inline-block; 
  background: var(--gray); 
  margin-right: 6px;
  vertical-align: middle;
}

.trail-shape-icon.ellipse   { border-radius: 50%; }
.trail-shape-icon.diamond   { transform: rotate(45deg); border-radius: 1px; }
.trail-shape-icon.rectangle { border-radius: 1px; }
.trail-shape-icon.triangle  {
  width: 0; height: 0; background: none;
  border-left: 4px solid transparent; 
  border-right: 4px solid transparent;
  border-bottom: 8px solid var(--gray);
}
.trail-shape-icon.hexagon { 
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%); 
}
```

#### Visual Result

**Before:**
```
1918–1973  Ramnad Krishnan
           abhimanamemnedu
```

**After:**
```
1918–1973  ● ◆ Ramnad Krishnan
           abhimanamemnedu
```

Where `●` is the era color (e.g., teal for Disseminators) and `◆` is the instrument shape (e.g., diamond for veena, ellipse for vocal).

The rasika can now scan the trail and immediately see:
- "This is a Golden Age vocalist" (blue circle)
- "This is a contemporary veena player" (green diamond)
- "This is a Disseminator-era vocalist" (teal circle)

---

### Change 3: Add YouTube Link to Bani Flow Trail

**Show a direct YouTube link next to each performance in the trail, matching the Concert Performances panel.**

#### Current Rendering (lines 1518-1525 in [`carnatic/render.py`](carnatic/render.py:1518))

```javascript
const labelSpan = document.createElement('span');
labelSpan.className = 'trail-label';
labelSpan.textContent = row.track.label;

li.appendChild(yearSpan);
li.appendChild(artistSpan);
li.appendChild(labelSpan);
trailList.appendChild(li);
```

#### Proposed Rendering

```javascript
const labelSpan = document.createElement('span');
labelSpan.className = 'trail-label';
labelSpan.textContent = row.track.label;

// Add YouTube link (same pattern as Concert Performances panel)
const linkA = document.createElement('a');
linkA.className = 'trail-link';
linkA.href = ytDirectUrl(row.track.vid, row.isStructured ? row.track.offset_seconds : undefined);
linkA.target = '_blank';
linkA.textContent = row.isStructured && row.track.offset_seconds
  ? `${formatTimestamp(row.track.offset_seconds)} ↗`
  : '↗';
linkA.title = 'Open in YouTube' + (row.isStructured ? ' at this timestamp' : '');
linkA.addEventListener('click', e => e.stopPropagation());

li.appendChild(lifespanSpan);
li.appendChild(artistSpan);
li.appendChild(labelSpan);
li.appendChild(linkA);  // ADD THIS
trailList.appendChild(li);
```

#### Helper Function Addition

Add a `formatTimestamp` helper function to convert seconds to `MM:SS` or `HH:MM:SS`:

```javascript
function formatTimestamp(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}
```

This function should be placed near the `ytDirectUrl` function (line 934).

#### CSS Addition (after line 640)

```css
.trail-link {
  flex-shrink: 0;
  color: var(--blue);
  font-size: 0.70rem;
  text-decoration: none;
  white-space: nowrap;
  margin-left: auto;  /* Push to the right edge */
}

.trail-link:hover {
  text-decoration: underline;
}
```

#### Visual Result

**Before:**
```
1918–1973  ● ○ Ramnad Krishnan
           abhimanamemnedu
```

**After:**
```
1918–1973  ● ○ Ramnad Krishnan
           abhimanamemnedu                                    1:02:50 ↗
```

The YouTube link appears at the right edge of the trail entry, matching the Concert Performances panel layout. The rasika can now:
- **Right-click the link** to copy the URL for sharing
- **Click the link** to open YouTube at the exact timestamp
- **Do this directly from the trail** without selecting the artist first

#### Workflow Improvement

**New workflow to share a Bani Flow result:**
1. Search for a raga/composition in Bani Flow
2. See the listening trail with multiple performances
3. **Right-click the YouTube link** to copy/share

**This is a one-step process.** The rasika can share a recording without leaving the trail, enabling rapid collaborative listening and research workflows.

---

### Change 4: Unify Concert Performances Display with Bani Flow (Lower Priority)

**Make the Concert Performances panel use the same visual structure as the Bani Flow trail.**

#### Current Rendering (lines 1059-1083 in [`carnatic/render.py`](carnatic/render.py:1059))

```javascript
const titleSpan = document.createElement('span');
titleSpan.className = 'perf-title';
titleSpan.textContent = p.display_title;

const ragaSpan = document.createElement('span');
ragaSpan.className = 'perf-raga';
const ragaText = [ragaName, p.tala, p.title].filter(Boolean).join(' · ');
ragaSpan.appendChild(document.createTextNode(ragaText));
```

#### Proposed Rendering

```javascript
// Show lifespan (if this is a multi-artist recording, show the primary performer's lifespan)
const lifespanSpan = document.createElement('span');
lifespanSpan.className = 'perf-lifespan';
lifespanSpan.textContent = ''; // Computed from primary performer's node data

// Show artist name with color/shape (for multi-artist recordings)
const artistSpan = document.createElement('span');
artistSpan.className = 'perf-artist';
// (color dot + shape icon + name, same as Bani Flow)

const titleSpan = document.createElement('span');
titleSpan.className = 'perf-title';
titleSpan.textContent = p.display_title;

const ragaSpan = document.createElement('span');
ragaSpan.className = 'perf-raga';
const ragaText = [ragaName, p.tala].filter(Boolean).join(' · ');
ragaSpan.appendChild(document.createTextNode(ragaText));
```

**Rationale:** The Concert Performances panel currently shows the **recording title** (e.g., "Srinivasa Farms Concert, Poonamallee 1965") in the metadata line. This is redundant - the recording title is already shown in the "SELECTED" panel above. What the rasika needs here is the **same metadata as the Bani Flow trail**: lifespan, era, instrument.

However, this change is **lower priority** than Changes 1, 2, and 3, because the Concert Performances panel is node-specific (the musician is already selected), while the Bani Flow trail is global (the musician is not yet selected). The metadata gap is more severe in the Bani Flow trail.

---

## Consequences

### Positive

1. **Temporal orientation** - Every musician in the Bani Flow trail now has a lifespan, allowing the rasika to immediately place them in the parampara's timeline
2. **Visual consistency** - The same metadata (lifespan, era color, instrument shape) appears in both the trail and the node selection view, creating a smooth gradient
3. **Reduced cognitive load** - The rasika no longer needs to click each name to understand who they are; the trail itself is informative
4. **Scalability** - As more recordings are added, the trail remains scannable because each entry carries its own context
5. **Immersion** - The rasika can lose themselves in the listening trail without breaking flow to check node metadata
6. **Rapid sharing** - The YouTube link in the trail enables one-click sharing of recordings, supporting collaborative listening and research workflows
7. **Workflow efficiency** - The rasika no longer needs to select an artist to get a shareable link; the link is available directly in the trail

### Negative

1. **Horizontal space cost** - Adding lifespan, color dot, and shape icon increases the width of each trail entry by ~100px
   - **Mitigation:** The left sidebar is already 280px wide (per ADR-003). This is sufficient. The lifespan can wrap to a second line on very narrow screens.

2. **Visual density** - The trail becomes more visually dense, with more elements per line
   - **Mitigation:** The color dot and shape icon are small (8px) and use muted colors. They add information without overwhelming the text.

3. **Implementation complexity** - Requires passing additional fields (`lifespan`, `color`, `shape`) through the `buildListeningTrail` function, and adding YouTube link rendering
   - **Mitigation:** These fields are already computed in `build_elements` and stored in the Cytoscape node data. The YouTube link uses the existing `ytDirectUrl` helper. This is a data-passing and rendering change, not a data-model change.

4. **Horizontal space cost (YouTube link)** - Adding the YouTube link increases the width of each trail entry
   - **Mitigation:** The link is right-aligned using `margin-left: auto`, so it floats to the right edge without pushing other elements. On narrow screens, it wraps to a new line below the composition title.

### What the Carnatic Coder Must Implement

#### 1. Modify `buildListeningTrail` Function (line 1397)

**For legacy youtube[] entries (line 1436):**
```javascript
rows.push({ 
  nodeId: nid, 
  artistLabel: d.label, 
  born: d.born,
  lifespan: d.lifespan,  // ADD
  color: d.color,        // ADD
  shape: d.shape,        // ADD
  track: t, 
  isStructured: false 
});
```

**For structured recordings (line 1459):**
```javascript
rows.push({
  nodeId,
  artistLabel,
  born,
  lifespan: pNode ? pNode.data('lifespan') : null,  // ADD
  color: pNode ? pNode.data('color') : null,        // ADD
  shape: pNode ? pNode.data('shape') : null,        // ADD
  track: { ... },
  isStructured: true,
});
```

#### 2. Modify Trail Rendering (line 1501)

**Replace:**
```javascript
const yearSpan = document.createElement('span');
yearSpan.className = 'trail-year';
yearSpan.textContent = row.track.year || '';
```

**With:**
```javascript
const lifespanSpan = document.createElement('span');
lifespanSpan.className = 'trail-lifespan';
lifespanSpan.textContent = row.lifespan || '';
```

**Modify artist span (line 1505):**
```javascript
const artistSpan = document.createElement('span');
artistSpan.className = 'trail-artist';

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

artistSpan.appendChild(document.createTextNode(row.artistLabel));
```

**Add YouTube link (after line 1520):**
```javascript
const linkA = document.createElement('a');
linkA.className = 'trail-link';
linkA.href = ytDirectUrl(row.track.vid, row.isStructured ? row.track.offset_seconds : undefined);
linkA.target = '_blank';
linkA.textContent = row.isStructured && row.track.offset_seconds
  ? `${formatTimestamp(row.track.offset_seconds)} ↗`
  : '↗';
linkA.title = 'Open in YouTube' + (row.isStructured ? ' at this timestamp' : '');
linkA.addEventListener('click', e => e.stopPropagation());
```

**Update appendChild calls (line 1522):**
```javascript
li.appendChild(lifespanSpan);  // CHANGED from yearSpan
li.appendChild(artistSpan);
li.appendChild(labelSpan);
li.appendChild(linkA);  // ADD THIS
trailList.appendChild(li);
```

#### 3. Add formatTimestamp Helper Function (near line 934)

```javascript
function formatTimestamp(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}
```

#### 4. Update CSS (line 637)

**Replace:**
```css
.trail-year { flex-shrink: 0; color: var(--gray); font-size: 0.68rem; min-width: 30px; margin-top: 2px; }
```

**With:**
```css
.trail-lifespan { flex-shrink: 0; color: var(--gray); font-size: 0.68rem; min-width: 80px; margin-top: 2px; }

.trail-color-dot {
  width: 8px; height: 8px; border-radius: 50%; 
  display: inline-block; margin-right: 4px; vertical-align: middle;
}

.trail-shape-icon {
  width: 8px; height: 8px; display: inline-block; 
  background: var(--gray); margin-right: 6px; vertical-align: middle;
}

.trail-shape-icon.ellipse   { border-radius: 50%; }
.trail-shape-icon.diamond   { transform: rotate(45deg); border-radius: 1px; }
.trail-shape-icon.rectangle { border-radius: 1px; }
.trail-shape-icon.triangle  {
  width: 0; height: 0; background: none;
  border-left: 4px solid transparent; border-right: 4px solid transparent;
  border-bottom: 8px solid var(--gray);
}
.trail-shape-icon.hexagon {
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}

.trail-link {
  flex-shrink: 0;
  color: var(--blue);
  font-size: 0.70rem;
  text-decoration: none;
  white-space: nowrap;
  margin-left: auto;
}

.trail-link:hover {
  text-decoration: underline;
}
```

### What the Librarian Must Do

**Nothing.** This is a pure rendering change. The data model already contains all required fields (`born`, `died`, `era`, `instrument`). The `lifespan` field is computed at render time (line 272).

---

## Alternatives Considered

### Alternative 1: Keep Recording Year, Add Lifespan as Secondary Text

Show both the recording year and the lifespan:
```
1965 Ramnad Krishnan (1918–1973)
     abhimanamemnedu
```

**Rejected.** This is visually cluttered. The recording year is less important than the musician's lifespan for orienting the rasika in the parampara. If the rasika wants to know when a specific recording was made, they can see it in the recording title or the Concert Performances panel.

### Alternative 2: Show Era Label Instead of Color Dot

Replace the color dot with a text label:
```
1918–1973  [Disseminators] Ramnad Krishnan
```

**Rejected.** This is too verbose. The color dot is a **visual mnemonic** that the rasika learns quickly (the same colors appear in the graph nodes and the legend). Adding text labels would make the trail harder to scan.

### Alternative 3: Show Instrument Icon Only (No Color Dot)

Show only the instrument shape, not the era color.

**Rejected.** Both era and instrument are important for understanding the musician's place in the parampara. The era tells you *when* they lived; the instrument tells you *what* they played. Both are needed for full context.

### Alternative 4: Make Metadata Optional (User Toggle)

Add a toggle button to show/hide the metadata (lifespan, color, shape).

**Rejected.** This adds UI complexity without solving the core problem. The metadata is not "extra information" - it is **essential context** for understanding the trail. Hiding it by default would defeat the purpose.

---

## Verification

After implementing this change, verify:

1. **Every trail entry has a lifespan** - No blank lifespan fields (unless the musician is unmatched, in which case the field should show `"—"` or be hidden)
2. **Color dots match graph nodes** - The color dot next to "Ramnad Krishnan" in the trail should be the same color as the Ramnad Krishnan node in the graph
3. **Shape icons match graph nodes** - The shape icon should match the node's instrument shape
4. **Visual alignment** - The lifespan, color dot, shape icon, and artist name should align horizontally without overlapping
5. **Clickability preserved** - Clicking the artist name should still select the node in the graph; clicking the YouTube link should open YouTube (the two click targets should not interfere)
6. **YouTube link functionality** - Right-clicking the link should allow copying the URL; the link should include the timestamp for structured recordings

---

## Query This Enables

**Rasika query:** "I want to explore how the treatment of Kalyani raga evolved from the Dhanammal bani (late 19th century) through the Disseminators (mid-20th century) to contemporary artists, and I want to see at a glance which era each musician belongs to without clicking through to their full profile."

**Before this fix:** Impossible without clicking each name. The trail shows only names and (sometimes) recording years. The rasika must click each name to see the lifespan and era.

**After this fix:** Natural. The trail shows:
```
1867–1938  ● ◆ Vina Dhanammal
           Kalyani varnam                                     ↗
1918–1973  ● ○ Ramnad Krishnan
           Kalyani alapana                                    1:02:50 ↗
b. 1984    ● ○ Abhishek Raghuram
           Kalyani kriti                                      0:45 ↗
```

The rasika can immediately see:
- Vina Dhanammal (Bridge era, veena) → Ramnad Krishnan (Disseminators, vocal) → Abhishek Raghuram (Contemporary, vocal)
- The century-long arc from the bani's origin to its modern expression
- The shift from veena to vocal as the primary medium

This is the **immersion pattern** at full strength: the rasika can trace a lineage without leaving the trail, and can share any recording with a single right-click.

**Additional query enabled by Change 3 (YouTube link):**

**Rasika query:** "I'm teaching a class on Kalyani raga and I need to quickly share three different interpretations (Dhanammal bani, Disseminators, Contemporary) with my students via email."

**Before this fix:** The rasika must:
1. Search for Kalyani in Bani Flow
2. Click Vina Dhanammal → find the recording in Concert Performances → copy link
3. Click Ramnad Krishnan → find the recording in Concert Performances → copy link
4. Click Abhishek Raghuram → find the recording in Concert Performances → copy link

**After this fix:** The rasika:
1. Searches for Kalyani in Bani Flow
2. Right-clicks the three YouTube links in the trail → copies all three URLs in 10 seconds

This enables **rapid collaborative workflows** - sharing recordings for teaching, research, or casual listening becomes frictionless.

---

## Implementation Priority

**High.** This is a **core usability fix** that directly serves the rasika's immersion and enables rapid sharing workflows. The current trail is informationally sparse - it shows names without context, forcing the rasika to click through to understand who each musician is. It also lacks direct YouTube links, forcing a two-step workflow to share recordings.

Recommend implementing immediately after ADR-003 (left sidebar restructuring), as all three changes work together to make the Bani Flow trail a **strong centre** in the interface:
- ADR-003: Spatial separation (left sidebar for global controls)
- ADR-004 Changes 1-2: Contextual metadata (lifespan, era, instrument)
- ADR-004 Change 3: Direct action (YouTube link for sharing)

Together, these changes transform the Bani Flow trail from a sparse list of names into a **rich, self-contained listening guide** that supports both immersive exploration and rapid collaborative workflows.

---

## Implementation Notes (2026-04-11)

### Bugs Discovered During Implementation

#### 1. **`pNode` ReferenceError in structured recording forEach loop**

**Symptom:** Raga and composition searches (e.g., "Begada", "Parulanna Matta") produced empty trails even though structured recordings existed with correct `raga_id` and `composition_id` tags.

**Root cause:** In `buildListeningTrail()` line 1483, `const pNode = cy.getElementById(...)` was declared inside the `if (primaryPerformer && primaryPerformer.musician_id)` block. The `rows.push()` call at line 1493 referenced `pNode` outside that block scope, causing a `ReferenceError` that silently killed the entire `structuredPerfs.forEach()` loop.

**Fix:** Hoisted `pNode` to the outer `let` declaration at line 1482: `let artistLabel, nodeId, born, pNode;`. Set `pNode = null` in the `else` branch.

**Impact:** This bug prevented **all** structured recording entries from appearing in the trail for any raga or composition search. The fix restored the entire structured recordings path.

#### 2. **Legacy track labels showing full metadata string**

**Symptom:** Legacy `youtube[]` tracks displayed as `"abhimānamenneḍu · Begada · Adi - Musiri Subramania Iyer"` instead of just the composition title.

**Root cause:** The `track.label` field in `musicians.json → youtube[]` contains the full human-readable label string (composition · raga · tala - artist). The trail rendering used `row.track.label` directly without resolving the composition title.

**Fix:** Added composition title resolution at line 1576:
```javascript
let compTitle = row.track.label;
if (!row.isStructured && row.track.composition_id) {
  const comp = compositions.find(c => c.id === row.track.composition_id);
  if (comp) compTitle = comp.title;
}
labelSpan.textContent = compTitle;
```

For structured recordings, `row.track.label` is already the clean `display_title` from the performance object.

**Impact:** Trail entries now show only the composition title (e.g., `"Abhimānamenneḍu"`), not the full metadata string. The raga/tala/artist information is redundant in the trail context (the user already searched by raga or composition, and the artist name appears in the row above).

#### 3. **Non-timestamped links showing bare "↗"**

**Symptom:** Legacy `youtube[]` tracks (which have no `offset_seconds`) showed a bare `"↗"` link, while structured recordings showed `"1:02:50 ↗"`.

**Fix:** Changed link text logic at line 1589 to always show a timestamp:
```javascript
linkA.textContent = (offsetSecs > 0)
  ? `${formatTimestamp(offsetSecs)} ↗`
  : `00:00 ↗`;
```

**Impact:** Uniform appearance across all trail entries. Non-timestamped links now show `"00:00 ↗"`.

### Final Layout Structure

The initial implementation placed all four elements (artist, lifespan, label, link) as direct children of the `li` with `flex-wrap: wrap`. This caused the composition title and timestamp link to wrap to separate lines when the label text was long.

**Final structure (two-row layout):**

```html
<li>
  <div class="trail-header">   <!-- Row 1: artist + lifespan -->
    <span class="trail-artist">
      <span class="trail-color-dot"></span>
      <span class="trail-shape-icon"></span>
      Artist Name
    </span>
    <span class="trail-lifespan">1918–1973</span>
  </div>
  <div class="trail-row2">      <!-- Row 2: composition + link -->
    <span class="trail-label">Abhimānamenneḍu</span>
    <a class="trail-link">4:00 ↗</a>
  </div>
</li>
```

**CSS:**
- `#trail-list li` — `display: flex; flex-direction: column; gap: 2px`
- `.trail-header` — `display: flex; width: 100%; gap: 4px`
- `.trail-lifespan` — `margin-left: auto` (pushes to right edge of header row)
- `.trail-row2` — `display: flex; width: 100%; gap: 4px`
- `.trail-label` — `flex: 1; min-width: 0` (grows to fill row2)
- `.trail-link` — `flex-shrink: 0` (stays at right edge)

This ensures the composition title and timestamp link always share the same line, with the link right-aligned.

### Verification Checklist (Completed)

- [x] Every trail entry has a lifespan (or blank if unmatched musician)
- [x] Color dots match graph node colors
- [x] Shape icons match graph node instrument shapes
- [x] Visual alignment: artist row and composition row are distinct, no overlap
- [x] Clickability: artist name selects node; YouTube link opens in new tab; both click targets work independently
- [x] YouTube link functionality: right-click copies URL; timestamped links include `?t=` parameter
- [x] Composition title resolution: legacy tracks show clean title, not full label string
- [x] Uniform timestamp display: all links show `"HH:MM:SS ↗"` or `"00:00 ↗"`
- [x] Two-row layout: composition title and link share the same line

### Files Modified

- `carnatic/render.py` — all changes (CSS, JS, helper functions)
- `carnatic/graph.html` — regenerated (derived artifact)

# ADR-026: Concert-Anchored Player Title and In-Player Track Selector

**Status:** Proposed  
**Date:** 2026-04-12

---

## Context

### The two symptoms

The screenshot shows the floating media player open with the title:

```
Lalgudi Jayaraman — Tuning (in Sri Rag…
```

This title was set by [`openOrFocusPlayer()`](../carnatic/render/templates/media_player.js:117) at the moment the user clicked the ▶ button on the "Tuning (in Sri Ragam)" track. Two problems follow from this:

**Problem 1 — The title names the track, not the concert.**

The user clicked a track from the *Music Academy 1965 — Lalgudi* concert. The player title tells them what they clicked — which they already know — but not *which concert this video belongs to*. As the YouTube video continues playing, the next track begins automatically (YouTube does not stop at timestamps). The title now reads "Tuning (in Sri Ragam)" while the audio has moved on to "Sami Ninne Kori". The title is wrong.

The concert is the correct identity for the player window. The concert is the stable, bounded object. The track is a position within it. The player title should name the concert, not the track.

**Problem 2 — The user cannot switch tracks without leaving the player.**

Once the player is open, the user may navigate away from the right panel — to the Bani Flow, to the graph, to the Raga Wheel. The right panel now shows a different musician or raga. To return to a different track in the *same concert*, the user must:

1. Re-navigate to the musician in the right panel
2. Re-expand the concert bracket
3. Click the ▶ button on the desired track

This is three steps to do what should be one. The player is a floating, persistent object — it should carry its own navigation affordance for the concert it is playing.

### Why this matters architecturally

ADR-012 established that the concert is the primary centre and the track is a position within it. ADR-018 established the concert bracket as the visual expression of that centre in the right panel. ADR-025 established the ▶ button as the explicit play affordance, freeing row clicks for cross-navigation.

This ADR completes the concert-as-centre pattern: the floating player must itself embody the concert's identity and provide navigation within it, independent of the right panel's current state.

### The oral tradition dimension

A Carnatic concert is not a playlist of independent compositions. It is a continuous musical event with an internal logic — the sequence of ragas, the building of mood, the tani avartanam as a structural pivot, the mangalam as a close. The rasika who opens the Wesleyan 1967 concert and then navigates to explore Ramnad Krishnan's lineage in the graph has not stopped listening to the concert. The concert continues. The player must honour this continuity by remaining a self-contained concert object, not a track-level widget.

---

## Forces in tension

| Force | Description |
|---|---|
| **Immersion** | The rasika must be able to listen to a concert continuously while navigating the graph. The player must not require the rasika to return to the right panel to change tracks. |
| **Fidelity to the oral tradition** | The concert is the primary unit of the live performance tradition. The player title must name the concert, not the track. |
| **Clarity of affordance** | The in-player track selector must be immediately discoverable but not visually dominant. It must not obscure the video. |
| **Scalability** | The selector must work for concerts with 2 tracks and concerts with 20 tracks. It must not overflow the player's fixed width. |
| **Registry invariant** | The `playerRegistry` keys by `video_id`. One window per concert video. This invariant must be preserved. The track selector navigates *within* the existing window; it does not open new windows. |
| **Independence from the right panel** | The player must carry its own concert data. If the right panel has navigated away from the musician who owns this concert, the player must still be able to list and jump to all tracks. |
| **Minimal DOM footprint** | The player is a floating overlay. It must not grow so large that it obscures the graph. The track selector must be compact — a dropdown or a collapsible list, not a full panel. |

---

## Pattern

### **Strong Centres** (Alexander, *The Nature of Order*, Book 1)

The concert recording is a strong centre. The floating player window is the visual expression of that centre. A strong centre must be *self-sufficient* — it must carry its own identity and its own internal navigation. Currently the player is not self-sufficient: it depends on the right panel to provide track navigation. This ADR makes the player a complete, self-contained concert object.

### **Levels of Scale** (Alexander, *A Pattern Language*, Pattern 26)

The player operates at two levels of scale simultaneously:

```
Level 1: The concert (title bar — always visible)
Level 2: The track list (dropdown — visible on demand)
```

The title bar names the concert (level 1). The dropdown reveals the tracks (level 2). This is the correct gradient: the concert identity is always present; the track detail is available on demand without dominating the interface.

### **Gradients** (Alexander, *A Pattern Language*, Pattern 9)

The transition from "concert title only" to "concert title + track list" is a gradient of disclosure. The rasika sees the concert name at all times. When they want to navigate within the concert, they open the dropdown. When they are done, they close it. The gradient is controlled by the rasika, not imposed by the interface.

### **Boundaries** (Alexander, *A Pattern Language*, Pattern 101)

The player title bar is a boundary between the concert identity (above) and the video content (below). The track selector lives in this boundary zone — it is part of the concert identity, not part of the video. Placing the selector in the title bar (or immediately below it, above the iframe) respects this boundary.

---

## Decision

### Change 1 — Player title names the concert, not the track

**Scope:** [`carnatic/render/templates/media_player.js`](../carnatic/render/templates/media_player.js) — `createPlayer()` and `openOrFocusPlayer()`

The `mp-title` element in the player title bar is set to the **concert title** (or `short_title`) when the player is created, and does **not** change when the user switches tracks within the same concert.

For structured concert recordings, the concert title is available on every `PerformanceRef` as `p.title` and `p.short_title`. The call site in `buildConcertBracket` already has access to the full `concert` object.

For legacy `youtube[]` tracks (non-structured), the title remains the track label — there is no concert object to name.

#### Before (title set to track label)

```javascript
// In buildConcertBracket — play button click handler:
openOrFocusPlayer(p.video_id, p.display_title, artistLabel,
                  p.offset_seconds > 0 ? p.offset_seconds : undefined);

// In openOrFocusPlayer — update branch:
existing.titleEl.textContent =
  (artistName ? artistName + ' \u2014 ' : '') + label;
```

#### After (title set to concert title; does not change on track switch)

```javascript
// In buildConcertBracket — play button click handler:
// Pass concertTitle as a new 5th argument
openOrFocusPlayer(
  p.video_id,
  p.display_title,          // trackLabel — used only for aria/tooltip
  artistLabel,
  p.offset_seconds > 0 ? p.offset_seconds : undefined,
  concert.short_title || concert.title   // concertTitle — NEW
);

// In openOrFocusPlayer — signature change:
function openOrFocusPlayer(vid, trackLabel, artistName, startSeconds, concertTitle) {
  const displayTitle = concertTitle
    ? (artistName ? artistName + ' \u2014 ' : '') + concertTitle
    : (artistName ? artistName + ' \u2014 ' : '') + trackLabel;

  if (playerRegistry.has(vid)) {
    const existing = playerRegistry.get(vid);
    existing.iframe.src = ytEmbedUrl(vid, startSeconds);
    // Title does NOT change — concert identity is stable
    bringToFront(existing);
    refreshPlayingIndicators();
    return;
  }
  const p = createPlayer(vid, trackLabel, artistName, startSeconds, concertTitle);
  playerRegistry.set(vid, p);
  refreshPlayingIndicators();
}

// In createPlayer — signature change:
function createPlayer(vid, trackLabel, artistName, startSeconds, concertTitle) {
  const displayTitle = concertTitle
    ? (artistName ? artistName + ' \u2014 ' : '') + concertTitle
    : (artistName ? artistName + ' \u2014 ' : '') + trackLabel;
  // ...
  // mp-title uses displayTitle (concert name), not trackLabel
}
```

**Consequence:** The title bar reads, e.g., `Lalgudi Jayaraman — Music Academy 1965` for the entire duration of the concert, regardless of which track is currently playing. This is correct: the concert is the stable identity.

---

### Change 2 — In-player track selector (dropdown)

**Scope:** [`carnatic/render/templates/media_player.js`](../carnatic/render/templates/media_player.js) — `createPlayer()`, new `buildPlayerTrackList()` helper

A compact track selector is embedded in the player, between the title bar and the iframe. It is hidden by default and revealed by a small `⋮` (or `≡`) button in the title bar.

#### Structure

```
┌─────────────────────────────────────────────────────┐
│ Lalgudi Jayaraman — Music Academy 1965    [≡] [✕]   │  ← mp-bar
├─────────────────────────────────────────────────────┤
│ ▼ Tuning (in Sri Ragam)          Sri · 00:00        │  ← mp-tracklist (open)
│   Sami Ninne Kori                Sri · 0:03         │
│   Sri Maha Ganapathim            Gowla · 8:15       │
│   Begada — Ragam                 Begada · 12:33      │
│   Sankari Nive                   Begada · 17:31      │
│   Sriranjini — Ragam             Sriranjini · 20:48  │
│   Brochevarevare                 Sriranjini · 32:48  │
│   …                                                  │
├─────────────────────────────────────────────────────┤
│  [YouTube iframe]                                    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

When collapsed (default):

```
┌─────────────────────────────────────────────────────┐
│ Lalgudi Jayaraman — Music Academy 1965    [≡] [✕]   │  ← mp-bar
├─────────────────────────────────────────────────────┤
│  [YouTube iframe]                                    │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### HTML shape

```html
<div class="media-player">
  <div class="mp-bar">
    <span class="mp-title">Lalgudi Jayaraman — Music Academy 1965</span>
    <button class="mp-tracklist-toggle" title="Track list">≡</button>
    <button class="mp-close" title="Close">✕</button>
  </div>

  <!-- Track list — hidden by default, shown when ≡ is clicked -->
  <div class="mp-tracklist" style="display:none">
    <ul class="mp-track-items">
      <li class="mp-track-item mp-track-active" data-offset="0">
        <span class="mp-track-label">Tuning (in Sri Ragam)</span>
        <span class="mp-track-meta">Sri · 00:00</span>
      </li>
      <li class="mp-track-item" data-offset="183">
        <span class="mp-track-label">Sami Ninne Kori</span>
        <span class="mp-track-meta">Sri · 3:03</span>
      </li>
      <!-- … -->
    </ul>
  </div>

  <div class="mp-video-wrap">
    <iframe class="mp-iframe" …></iframe>
  </div>
  <div class="mp-resize" title="Drag to resize"></div>
</div>
```

#### Data flow — how the track list reaches the player

The `concert` object is already available in `buildConcertBracket()` at the moment the ▶ button is clicked. The track list must be passed to `createPlayer()` so the player can render it without depending on the right panel's DOM.

A new `tracks` parameter is added to `createPlayer()` and `openOrFocusPlayer()`:

```javascript
// Shape of a track entry passed to the player:
{
  offset_seconds: 0,
  display_title:  "Tuning (in Sri Ragam)",
  raga_id:        "sri",
  raga_name:      "Sri",    // resolved at call site from ragas[]
  tala:           null,
  timestamp:      "00:00"
}
```

The call site in `buildConcertBracket` assembles this array from the `concert.sessions` data already in scope:

```javascript
// Assemble track list for the player
const playerTracks = [];
concert.sessions.forEach(session => {
  const sortedPerfs = session.perfs.slice().sort(
    (a, b) => (a.offset_seconds || 0) - (b.offset_seconds || 0)
  );
  sortedPerfs.forEach(p => {
    const ragaObj = p.raga_id ? ragas.find(r => r.id === p.raga_id) : null;
    playerTracks.push({
      offset_seconds: p.offset_seconds || 0,
      display_title:  p.display_title || '',
      raga_id:        p.raga_id || null,
      raga_name:      ragaObj ? ragaObj.name : (p.raga_id || ''),
      tala:           p.tala || null,
      timestamp:      p.timestamp || '00:00',
    });
  });
});
// Sort globally by offset_seconds (across sessions)
playerTracks.sort((a, b) => a.offset_seconds - b.offset_seconds);

// Pass to openOrFocusPlayer
openOrFocusPlayer(
  p.video_id,
  p.display_title,
  artistLabel,
  p.offset_seconds > 0 ? p.offset_seconds : undefined,
  concert.short_title || concert.title,
  playerTracks                              // NEW
);
```

#### Track item click behaviour

Clicking a track item in the `mp-tracklist`:

1. Updates `existing.iframe.src` to `ytEmbedUrl(vid, offset_seconds)` — jumps to the timestamp.
2. Removes `mp-track-active` from all items; adds it to the clicked item.
3. Does **not** close the track list — the rasika may want to click another track immediately.
4. Does **not** change the title bar — the concert title remains.

```javascript
function buildPlayerTrackList(vid, tracks) {
  const ul = document.createElement('ul');
  ul.className = 'mp-track-items';

  tracks.forEach(t => {
    const li = document.createElement('li');
    li.className = 'mp-track-item';
    li.dataset.offset = t.offset_seconds;

    const labelSpan = document.createElement('span');
    labelSpan.className = 'mp-track-label';
    labelSpan.textContent = t.display_title;

    const metaSpan = document.createElement('span');
    metaSpan.className = 'mp-track-meta';
    const parts = [t.raga_name, t.tala].filter(Boolean);
    metaSpan.textContent = (parts.length ? parts.join(' · ') + ' · ' : '') + t.timestamp;

    li.appendChild(labelSpan);
    li.appendChild(metaSpan);

    li.addEventListener('click', () => {
      const player = playerRegistry.get(vid);
      if (!player) return;
      player.iframe.src = ytEmbedUrl(vid, t.offset_seconds > 0 ? t.offset_seconds : undefined);
      // Update active indicator
      ul.querySelectorAll('.mp-track-item').forEach(el => el.classList.remove('mp-track-active'));
      li.classList.add('mp-track-active');
      refreshPlayingIndicators();
    });

    ul.appendChild(li);
  });

  return ul;
}
```

#### Toggle button behaviour

```javascript
// In createPlayer — wire the ≡ toggle button:
const toggleBtn = el.querySelector('.mp-tracklist-toggle');
const tracklistEl = el.querySelector('.mp-tracklist');
toggleBtn.addEventListener('click', e => {
  e.stopPropagation();
  const isOpen = tracklistEl.style.display !== 'none';
  tracklistEl.style.display = isOpen ? 'none' : 'block';
  toggleBtn.classList.toggle('mp-tracklist-open', !isOpen);
});
```

#### Active track indicator on open

When the track list is first opened, the item whose `offset_seconds` is closest to (but not greater than) the current playback position should be marked `mp-track-active`. Since the YouTube iframe API is not available without OAuth, the active item is set heuristically: the item whose `offset_seconds` matches the `startSeconds` passed to `openOrFocusPlayer` at the time of the most recent track click. This is stored on the player instance as `instance.currentOffset`.

```javascript
// On player instance:
instance.currentOffset = startSeconds || 0;

// When a track item is clicked:
instance.currentOffset = t.offset_seconds;
```

When the track list is opened, the item with `dataset.offset == instance.currentOffset` receives `mp-track-active`.

---

### Change 3 — Legacy tracks: no track selector, title unchanged

Legacy `youtube[]` tracks (non-structured, from `musicians.json`) do not have a concert object. For these:

- `concertTitle` is `undefined` → `openOrFocusPlayer` falls back to `trackLabel` as the title (existing behaviour).
- `tracks` is `undefined` → `createPlayer` does not render the `mp-tracklist` or the `≡` button.
- The `mp-tracklist-toggle` button is only rendered when `tracks` is a non-empty array.

This preserves full backward compatibility for legacy tracks.

---

## Before / After JSON shape

No data schema change is required. All fields needed by the track selector (`display_title`, `offset_seconds`, `timestamp`, `raga_id`, `tala`) are already present on every `PerformanceRef` in `musicianToPerformances`. The change is entirely in the rendering layer.

### `openOrFocusPlayer` — signature change

#### Before

```javascript
function openOrFocusPlayer(vid, label, artistName, startSeconds)
```

#### After

```javascript
function openOrFocusPlayer(vid, trackLabel, artistName, startSeconds, concertTitle, tracks)
// concertTitle: string | undefined — concert short_title or title; undefined for legacy tracks
// tracks: Array<TrackEntry> | undefined — ordered track list; undefined for legacy tracks
```

### `createPlayer` — signature change

#### Before

```javascript
function createPlayer(vid, label, artistName, startSeconds)
```

#### After

```javascript
function createPlayer(vid, trackLabel, artistName, startSeconds, concertTitle, tracks)
```

### Player instance — new fields

#### Before

```javascript
const instance = {
  el,
  iframe:  el.querySelector('.mp-iframe'),
  titleEl: el.querySelector('.mp-title'),
  vid,
};
```

#### After

```javascript
const instance = {
  el,
  iframe:        el.querySelector('.mp-iframe'),
  titleEl:       el.querySelector('.mp-title'),
  tracklistEl:   el.querySelector('.mp-tracklist'),   // null for legacy tracks
  vid,
  currentOffset: startSeconds || 0,
};
```

---

## CSS additions

```css
/* ── in-player track list ── */
.mp-tracklist-toggle {
  background: none;
  border: none;
  color: var(--gray);
  font-size: 0.85rem;
  padding: 0 4px;
  cursor: pointer;
  flex-shrink: 0;
  line-height: 1;
}
.mp-tracklist-toggle:hover,
.mp-tracklist-toggle.mp-tracklist-open {
  color: var(--yellow);
}

.mp-tracklist {
  max-height: 180px;
  overflow-y: auto;
  background: var(--bg1);
  border-bottom: 1px solid var(--bg3);
}

.mp-track-items {
  list-style: none;
  margin: 0;
  padding: 0;
}

.mp-track-item {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 6px;
  padding: 3px 8px;
  cursor: pointer;
  font-size: 0.70rem;
  border-bottom: 1px solid var(--bg2);
}
.mp-track-item:last-child { border-bottom: none; }
.mp-track-item:hover .mp-track-label { color: var(--yellow); }

.mp-track-label {
  color: var(--fg2);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mp-track-meta {
  color: var(--gray);
  flex-shrink: 0;
  font-size: 0.65rem;
}

.mp-track-item.mp-track-active .mp-track-label {
  color: var(--aqua);
}
.mp-track-item.mp-track-active .mp-track-meta {
  color: var(--teal);
}
```

---

## Interaction model after this ADR

```
FLOATING PLAYER (concert video open)
  Title bar                → concert name (stable; does not change on track switch)
  ≡ button click           → toggle mp-tracklist open/closed
  Track item click         → jump to offset_seconds in iframe; mark item active
  ✕ button click           → close player (unchanged)
  Drag title bar           → reposition (unchanged)
  Drag resize grip         → resize (unchanged)

RIGHT PANEL (concert bracket, expanded)
  ▶ button click           → openOrFocusPlayer(vid, trackLabel, artist, offset,
                               concertTitle, playerTracks)
                             → if player already open: jump to offset only (title unchanged)
                             → if player not open: create player with concert title + track list
  Row click                → triggerBaniSearch (ADR-025 Change 1; unchanged)
```

---

## Consequences

### Queries this enables

| Rasika scenario | Before | After |
|---|---|---|
| "I'm listening to Music Academy 1965. What concert is this?" | Title reads "Tuning (in Sri Ragam)" — no concert context | Title reads "Lalgudi Jayaraman — Music Academy 1965" — concert identity always visible |
| "The video has moved on to the next piece. What is the player title?" | Title still reads "Tuning (in Sri Ragam)" — wrong | Title still reads "Lalgudi Jayaraman — Music Academy 1965" — correct; concert is stable |
| "I'm listening to Music Academy 1965 and have navigated to the Bani Flow. I want to jump to Begada — Ragam." | Must re-navigate to Lalgudi in right panel, re-expand bracket, click ▶ on Begada | Click ≡ in player → track list opens → click "Begada — Ragam" → player jumps to 12:33 |
| "I want to see all tracks in this concert without leaving the player" | Impossible | Click ≡ → full ordered track list with raga names and timestamps |
| "I want to jump to the tani avartanam" | Must re-navigate to right panel | Click ≡ → click "Tani Avartanam" in track list |

### What this enables beyond the current data

- **Active track highlighting** — as the rasika clicks tracks, the `mp-track-active` class marks the current position. A future enhancement using the YouTube iframe API could update this automatically as the video plays.
- **Concert-level play button on the bracket header** — ADR-018 noted this as a future enhancement. With the track list now embedded in the player, the bracket header's "play from beginning" button becomes trivial: it calls `openOrFocusPlayer` with `offset_seconds: 0` and the full `playerTracks` array.
- **Keyboard navigation** — the `mp-tracklist` is a standard `<ul>` and can receive keyboard focus and arrow-key navigation in a future enhancement.

### What this forecloses

- **Title as "now playing" indicator** — the title no longer tells the user which track is currently playing. This is a deliberate trade-off: the concert identity is more stable and more useful than the track name, which changes as the video plays. The track list (when open) shows the active track via `mp-track-active`.
- **Per-track title updates on same-concert switches** — ADR-012 established that `openOrFocusPlayer` updates the title on same-concert track switches. This ADR reverses that decision for structured concerts: the title is set once (to the concert name) and does not change. The `openOrFocusPlayer` update branch no longer touches `titleEl` for structured concerts.

### Interaction with ADR-012 (same-concert track switching)

ADR-012 fixed the bug where clicking a second track from the same concert produced no visible response. The fix updated both `iframe.src` and `titleEl.textContent`. This ADR retains the `iframe.src` update but removes the `titleEl.textContent` update for structured concerts. The player still responds visibly to track clicks (the video jumps to the new timestamp); only the title is now stable.

### Interaction with ADR-018 (concert-bracketed recording groups)

The `concert` object assembled in `buildConcertBracket` already contains all sessions and performances. The `playerTracks` array is assembled from this object at the call site. No new data is required; the assembly is a client-side transform of existing data.

### Interaction with ADR-025 (cross-panel coupling)

ADR-025 Change 0 added the ▶ button to `buildConcertBracket`. This ADR extends the ▶ button's click handler to pass `concertTitle` and `playerTracks` to `openOrFocusPlayer`. The row click (cross-navigation) is unchanged.

---

## Implementation

**Agent:** Carnatic Coder  
**Files to modify:**

| File | Changes |
|---|---|
| [`carnatic/render/templates/media_player.js`](../carnatic/render/templates/media_player.js) | Change 1 (concert title in `createPlayer` + `openOrFocusPlayer`); Change 2 (`mp-tracklist` DOM, `buildPlayerTrackList`, toggle wiring, `currentOffset` tracking); Change 3 (legacy track guard) |
| [`carnatic/render/templates/base.html`](../carnatic/render/templates/base.html) | CSS for `.mp-tracklist`, `.mp-track-items`, `.mp-track-item`, `.mp-track-label`, `.mp-track-meta`, `.mp-tracklist-toggle` |

**No Python changes. No data schema changes. No changes to `graph_api.py` or `cli.py`.**

**Suggested implementation order:**

1. Update `createPlayer` and `openOrFocusPlayer` signatures (Change 1 + Change 3 guard).
2. Add `buildPlayerTrackList` helper and wire it into `createPlayer` (Change 2).
3. Add CSS to `base.html`.
4. Update the ▶ button call site in `buildConcertBracket` to pass `concertTitle` and `playerTracks`.

**Verification:**

```bash
# Regenerate graph.html
python3 -m carnatic.render._main

# Open in browser
python3 carnatic/serve.py

# Test 1: Click ▶ on any track in Music Academy 1965 (Lalgudi)
#   → Player title reads "Lalgudi Jayaraman — Music Academy 1965"
#   → NOT "Lalgudi Jayaraman — Tuning (in Sri Ragam)"

# Test 2: Click ▶ on a second track from the same concert
#   → Player title does NOT change
#   → Video jumps to new timestamp

# Test 3: Navigate away from Lalgudi in the right panel
#   → Player remains open with concert title
#   → Click ≡ → track list opens with all Music Academy 1965 tracks
#   → Click "Begada — Ragam" → video jumps to 12:33

# Test 4: Click ▶ on a legacy youtube[] track (non-structured)
#   → Player title reads "Artist — Track Label" (unchanged behaviour)
#   → No ≡ button visible
```

---

## ADR references

| ADR | Relationship |
|---|---|
| ADR-012 | Same-concert track switching — established `openOrFocusPlayer` update branch; this ADR modifies the title update behaviour within that branch |
| ADR-018 | Concert-bracketed recording groups — defines the `concert` object and `buildConcertBracket`; this ADR extends the ▶ button call site |
| ADR-025 | Cross-panel coupling — Change 0 added the ▶ button; this ADR extends its click handler |

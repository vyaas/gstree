# ADR-012: Same-Concert Track Switching — Replace, Don't Ignore

**Status:** Implemented
**Date:** 2026-04-11

---

## Context

The multi-window player (ADR-004, now implemented) keys [`playerRegistry`](../carnatic/render.py:1198) by `vid` — the 11-character YouTube video ID. This is correct for the cross-concert case: if the rasika has already opened the Poonamallee 1965 concert and clicks it again from a different node, the existing window is brought to the front rather than spawning a duplicate.

However, a structured concert recording is a **single YouTube video** that contains many compositions at different timestamps. Every track in `music_academy_1973_kvn.json`, for example, shares the same `video_id`. When the rasika clicks *Akshaya Linga Vibho* (offset 3329 s) and then clicks *Alarśara Paritāpam* (offset 7871 s) from the same right-sidebar recording list, [`openOrFocusPlayer()`](../carnatic/render.py:1312) finds the `vid` already in the registry, calls [`bringToFront()`](../carnatic/render.py:1228), and returns — without updating the iframe `src`. The player window does not change. The rasika sees no response to their click.

This is the bug shown in the screenshot: clicking another track from the same concert in the right sidebar produces no visible effect.

**Forces in tension:**

1. **Immersion** — the rasika must be able to move freely between compositions within a concert. Clicking a track must always produce an audible response.
2. **Registry invariant** — the registry's "one window per `vid`" rule exists to prevent duplicate windows of the *same video*. This invariant is correct and must be preserved.
3. **Timestamp fidelity** — the new track must start at its own `offset_seconds`, not at the beginning of the video or at the previous track's position.
4. **No data-schema changes** — the structured recording schema (`video_id`, `offset_seconds`) already carries everything needed. This is a pure UI/rendering fix.
5. **User preference (stated)** — the user prefers *replace* over *new window* for same-concert track switching. This is the simplest resolution of the tension between forces 1 and 2.

---

## Pattern

**Gradients** (Alexander) — the distinction between *same concert, different track* and *different concert* is a gradient of identity, not a binary. The registry correctly treats different concerts as different centres. Within a single concert, the compositions are not independent centres — they are moments within one continuous musical event. The player window for a concert is the centre; the track is a position within it.

**Strong Centres** — the concert recording is the centre, not the individual composition. Switching tracks within a concert is navigation *within* a centre, not the creation of a new one. The window should persist; only its content (the iframe `src`) should change.

---

## Decision

### The fix: distinguish same-`vid` track switches from cross-`vid` opens

[`openOrFocusPlayer()`](../carnatic/render.py:1312) currently has two branches:

```
if registry has vid → bringToFront, return
else               → createPlayer, register
```

The fix adds a third case: **same `vid`, different `startSeconds`** → update the existing player's iframe `src` to the new timestamp, bring to front, update the title.

### Before

```javascript
function openOrFocusPlayer(vid, label, artistName, startSeconds) {
  if (playerRegistry.has(vid)) {
    bringToFront(playerRegistry.get(vid));
    return;                                    // ← bug: ignores new startSeconds
  }
  const p = createPlayer(vid, label, artistName, startSeconds);
  playerRegistry.set(vid, p);
  refreshPlayingIndicators();
}
```

### After

```javascript
function openOrFocusPlayer(vid, label, artistName, startSeconds) {
  if (playerRegistry.has(vid)) {
    const existing = playerRegistry.get(vid);
    // Always update: new track in same concert → replace iframe src + title
    existing.iframe.src = ytEmbedUrl(vid, startSeconds);
    existing.titleEl.textContent =
      (artistName ? artistName + ' \u2014 ' : '') + label;
    bringToFront(existing);
    refreshPlayingIndicators();
    return;
  }
  const p = createPlayer(vid, label, artistName, startSeconds);
  playerRegistry.set(vid, p);
  refreshPlayingIndicators();
}
```

**Why always update, not only when `startSeconds` differs?**

- The user clicked a track. They expect something to happen. Even if the offset is identical (e.g. two entries both at 0 s), updating the `src` restarts the video from the beginning — which is the correct response to a deliberate click.
- Comparing `startSeconds` to the current iframe position is not reliably possible without the YouTube iframe API. The simpler rule (always update on click) is correct and predictable.
- The title update ensures the window header reflects the newly selected track, not the previously loaded one.

### Registry key remains `vid`

The registry key does **not** change. The invariant "one window per `video_id`" is preserved. The fix is entirely within the `openOrFocusPlayer` function body — no structural change to the registry, no new data fields, no new DOM elements.

### `refreshPlayingIndicators()` in the update branch

The existing branch did not call `refreshPlayingIndicators()` because it assumed nothing changed. After the fix, the title and src change, but the registry membership does not — so the `playing` class on sidebar items is already correct. The call is included for consistency and to handle any future indicator logic that may depend on the update path.

---

## Consequences

### Queries this enables

| Scenario | Before | After |
|---|---|---|
| Click *Akshaya Linga Vibho*, then click *Alarśara Paritāpam* from the same concert | Second click: silent, no response | Second click: player jumps to new timestamp, title updates |
| Click a track from Concert A, then click a different track from Concert A | No change | Player replaces content with new track |
| Click a track from Concert A, then click a track from Concert B | New window opens (correct) | Unchanged — new window opens |
| Click the same track twice | Second click: silent (correct — already playing) | Second click: restarts from beginning (acceptable; user clicked deliberately) |

### What this does not change

- The registry structure — `vid → instance` — is unchanged.
- The `createPlayer()` function is unchanged.
- The data schema (`video_id`, `offset_seconds`) is unchanged.
- Cross-concert behaviour (different `vid`) is unchanged.
- The Bani Flow trail call site at line 1944 is unchanged — it already passes `offset_seconds` correctly; the fix in `openOrFocusPlayer` handles it transparently.

### Edge case: `startSeconds` is `undefined` for legacy (non-structured) tracks

Legacy `youtube[]` entries in `musicians.json` do not have `offset_seconds`. They pass `startSeconds = undefined` to `openOrFocusPlayer`. The `ytEmbedUrl()` function already handles `undefined` gracefully (no `&start=` parameter). The fix does not change this behaviour.

### Edge case: two musicians share the same concert video

The Poonamallee 1965 concert (`video_id: _rj8fHJiSLA`) appears in the sidebar of multiple musicians (Ramnad Krishnan, Semmangudi Srinivasa Iyer, etc.). If the rasika has the concert open from Ramnad Krishnan's sidebar and then clicks a track from Semmangudi's sidebar for the same concert, the existing window will update to the new track and timestamp. This is correct: there is one concert, one window, one video. The title will update to reflect the newly selected track's artist and label.

---

## Implementation

**Agent:** Carnatic Coder  
**File:** [`carnatic/render.py`](../carnatic/render.py) — JavaScript section only  
**Scope:** Replace the body of `openOrFocusPlayer()` (lines 1312–1320) with the after-shape above.  
**No Python changes.** No data file changes. No CSS changes.  
**Verification:** Run `python3 carnatic/render.py`, open `serve.py`, click a track from a structured concert, then click a second track from the same concert — the player should update immediately to the new timestamp.

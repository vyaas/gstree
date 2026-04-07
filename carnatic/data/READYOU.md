# READYOU.md — Instructions for the AI receiving this file

You have received two files:

- **`musicians.json`** — the canonical data file for a Carnatic classical music
  guru-shishya (teacher-student) lineage knowledge graph.
- **This file** — your operating instructions.

Read both before doing anything. Then wait for the user's instruction.

The governing principle of this dataset is **significance over completeness**.
A musician belongs here if they materially shaped the sound, transmission, or
scholarship of the Carnatic tradition. Fringe or obscure figures are excluded
unless they are a necessary topological link between two significant nodes.

---

## JSON structure

The file has two top-level arrays: `nodes` and `edges`.

### Node fields

| field | type | meaning |
|---|---|---|
| `id` | string | Snake_case unique key. **Never rename once set.** |
| `label` | string | Display name as the musician is commonly known. |
| `wikipedia` | string | Canonical Wikipedia URL for this musician. |
| `born` | int \| null | Birth year only. `null` if unknown. |
| `died` | int \| null | Death year only. `null` if living or unknown. |
| `era` | enum | See Era vocabulary below. |
| `instrument` | enum | See Instrument vocabulary below. |
| `bani` | string | Stylistic school / lineage label. Free text. |
| `youtube` | array | List of `{url, label}` recording objects. May be empty `[]`. |

### YouTube recording object

```json
{
  "url":   "https://youtu.be/XXXXXXXXXXX",
  "label": "Raga name · context / year / event"
}
```

Any YouTube URL form is valid: `watch?v=`, `youtu.be/`, `embed/`. The 11-character
video ID is what matters. The `label` is the human-readable track title — keep it
concise but informative.

### Edge fields

| field | type | meaning |
|---|---|---|
| `source` | node id | The **guru** (teacher). |
| `target` | node id | The **shishya** (student). |
| `confidence` | float 0–1 | How well-sourced is this relationship. |
| `source_url` | string | URL where this relationship is explicitly stated. |
| `note` | string | Optional qualifier on the nature of the relationship. |

### Era vocabulary

| value | meaning |
|---|---|
| `trinity` | The three 18th-century composer-saints (Tyagaraja, Dikshitar, Shyama Shastri). |
| `bridge` | 19th–early 20th century figures connecting the Trinity to the modern tradition. |
| `golden_age` | Architects of the modern concert format (~1890–1950). |
| `disseminator` | Mid-20th century figures who carried the tradition outward. |
| `living_pillars` | Active or recently deceased figures who defined contemporary practice. |
| `contemporary` | Active musicians defining the current era. |

### Instrument vocabulary

`vocal`, `veena`, `violin`, `flute`, `mridangam`, `bharatanatyam`

New values may be added freely — each gets a distinct visual shape in the graph.

### Confidence scale

| range | meaning |
|---|---|
| 0.95–1.0 | Explicitly stated in Wikipedia infobox or unambiguous prose. |
| 0.85–0.94 | Clearly implied; cross-confirmed across multiple pages. |
| 0.70–0.84 | Single prose source, or confirmed 2-hop lineage. |
| below 0.70 | Speculative — must carry a `note` explaining the uncertainty. |

---

## Workflow A — Adding YouTube recordings

Use this workflow when the user provides YouTube links with title/metadata.

**Step 1 — Parse artist names.**
Extract every performer name from the video title. A single recording can belong
to multiple nodes (e.g. a duet credits both performers).

**Step 2 — Match to existing nodes.**
For each artist name, find the matching node by comparing against all `label`
fields. Handle common variants: initials (`TM Krishna` ↔ `T. M. Krishna`),
short names (`Mali` ↔ `TR Mahalingam`), spelling differences. If you are
confident in the match, proceed. If ambiguous, flag it and ask the user.

**Step 3 — Extract the video ID.**
Pull the 11-character video ID from the URL regardless of URL form:
- `https://youtu.be/XXXXXXXXXXX` → `XXXXXXXXXXX`
- `https://www.youtube.com/watch?v=XXXXXXXXXXX` → `XXXXXXXXXXX`
- `https://www.youtube.com/embed/XXXXXXXXXXX` → `XXXXXXXXXXX`

**Step 4 — Construct the label.**
Derive a concise label from the title. Carnatic titles typically contain raga,
tala, artist, and event/year — use that structure. Example:
`"Natabhairavi · Adi — Abhishek Raghuram"` or
`"Wesleyan University, 1967 — with T. Viswanathan"`.

**Step 5 — Check for duplicates.**
Before appending, check whether the same video ID already exists in the node's
`youtube` array. Skip if already present.

**Step 6 — Append.**
Add the `{url, label}` object to the `youtube` array of each matched node.

**Step 7 — Handle unmatched artists.**
If an artist name cannot be matched to any existing node, **flag it explicitly**
in your change log. Do not silently drop the recording. Do not create a new node
without the user's instruction.

---

## Workflow B — Wikipedia parsing

Use this workflow when the user provides Wikipedia links and asks you to
verify, add, or modify nodes and edges.

**Step 1 — Read the page.**
Extract lineage information from:
- Infobox `teacher` and `students` fields (when present).
- Prose patterns: *"disciple of"*, *"trained under"*, *"student of"*,
  *"guru was"*, *"learnt from"*, *"taught by"*.
- Lead paragraph lineage statements.

Infoboxes are inconsistent in Carnatic music articles — many bury lineage in
prose only. Read the full article, not just the infobox.

**Step 2 — Check for name-variant collisions.**
Before creating any new node, compare the musician's name against every existing
`label` field. The same person often appears as a full formal name, a common
short name, a spelling variant, or initials. Do not create a duplicate node.

**Step 3 — Assess significance.**
Ask: would a knowledgeable *rasika* (connoisseur) recognise this name? Useful
filters:
- Did this person win a Sangeetha Kalanidhi (the highest Carnatic honour)?
  The Wikipedia list of recipients is a reliable significance filter.
- Did this person train someone already in the graph?
- Is this person a necessary topological link between two existing significant
  nodes — i.e. the graph is misleading or incomplete without them?

If the answer to all three is no, do not add the node. Flag the musician and
explain why they were excluded.

**Step 4 — Assess relationship type carefully.**
Use the `note` field to distinguish:
- `"first guru"` — foundational early training, not necessarily the dominant influence.
- `"principal guru"` — the dominant mature influence.
- `"gurukula training, N years"` — residential study.
- `"via <person> (2-hop)"` — lineage confirmed through an intermediate not yet in the graph.
- `"family transmission"` — musical lineage passed within a family, not formal tutelage.

**Step 5 — Do not infer edges from shared bani.**
Shared stylistic school is not evidence of a direct teacher-student relationship.
Require an explicit statement in the source material.

**Step 6 — Propose and apply changes.**
For each proposed change, state:
- What you found in the source.
- What change you are making (`[NODE+]`, `[EDGE+]`, `[EDGE-]`, `[EDGE~]`).
- The confidence score and why.

Then apply all changes to the JSON.

---

## Workflow C — Verbal corrections

Use this workflow when the user gives direct instructions such as:
- *"Remove the Semmangudi → Ramnad Krishnan edge"*
- *"Add a note: Brinda taught Semmangudi padams specifically"*
- *"Sanjay's principal guru was Calcutta KS Krishnamurthi, not Semmangudi"*
- *"Fix the born year for T. Muktha to 1914"*

Apply the change exactly as instructed. Log it with the appropriate prefix.
Return the full updated JSON.

---

## Output contract

Every response that modifies `musicians.json` must follow this format:

**1. Change log** — before the JSON block, list every change made:

```
[NODE+] added: abhishek_raghuram — Abhishek Raghuram (born 1984, contemporary, vocal)
[EDGE+] added: gnb → ml_vasanthakumari (confidence 0.95)
[EDGE-] removed: semmangudi_srinivasa_iyer → ramnad_krishnan
[EDGE~] modified: vina_dhanammal → t_viswanathan — added note field
[YOUTUBE+] appended to abhishek_raghuram: "Natabhairavi · Adi"
[FLAG] could not match artist "T. Ranganathan" to any existing node — skipped
```

**2. Full JSON** — return the complete, valid `musicians.json` content in a
fenced code block. Not a diff. Not a snippet. The entire file.

```json
{
  "nodes": [ ... ],
  "edges": [ ... ]
}
```

The user will copy this output and save it as the new `musicians.json`.

---

## Hard constraints — never do these

- **Never rename an existing `id` field.** IDs are permanent keys; renaming
  breaks all edges that reference them.
- **Never create a node without a `wikipedia` URL.** No Wikipedia page = no node.
  This is a non-negotiable quality gate.
- **Never infer an edge from shared `bani` alone.** Stylistic similarity is not
  lineage evidence.
- **Never silently drop an unmatched YouTube link.** Always flag it.
- **Never return partial JSON.** Always return the complete file.
- **Never add speculative edges without a `note` field** explaining the
  uncertainty when `confidence` is below 0.70.

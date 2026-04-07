# READYOU_SPEC.md — How to write a READYOU.md for any dataset

## What is a READYOU.md?

A `READYOU.md` is a **machine-addressed instruction file** that travels alongside
a structured data file (JSON, CSV, YAML, …) and tells an LLM exactly what to do
when both files are dropped into a chat session together.

It is the no-code equivalent of a developer README. Where a README tells a human
how to work with a codebase, a READYOU.md tells an LLM how to work with a data
file — without the human needing to write any code or craft any prompts.

The pattern is:

```
your_data.json    ← the data
READYOU.md        ← the LLM's operating instructions
```

Drop both into any chat-capable LLM. The LLM reads the instructions, then waits
for the user's query. The user's query can be as simple as pasting a link or
saying "add this entry".

---

## When to use this pattern

Use a READYOU.md when:

- Your data file has a non-obvious schema that an LLM would otherwise have to
  guess at.
- You want consistent, rule-governed edits across many sessions and many users.
- You want to enforce data quality constraints (required fields, controlled
  vocabularies, significance thresholds, duplicate checks) without writing code.
- You want non-technical collaborators to contribute to a structured dataset
  using only a chat interface.

---

## Anatomy of a READYOU.md

A well-formed READYOU.md has six sections. All are required.

---

### 1. Preamble

Tell the LLM what it is holding and what the governing principle of the dataset
is. Be explicit that this file is addressed to the LLM, not to a human reader.

```markdown
# READYOU.md — Instructions for the AI receiving this file

You have received two files:
- `your_data.json` — [one-sentence description of what the data represents]
- This file — your operating instructions.

Read both before doing anything. Then wait for the user's instruction.

The governing principle of this dataset is [state it clearly — e.g.
"significance over completeness", "one entry per verified source",
"no duplicates across any key field"].
```

**Why this matters:** LLMs will attempt to be helpful immediately. The explicit
"wait for the user's instruction" prevents premature action.

---

### 2. Schema reference

Document every field in the data file. For each field, state:

- **Name** — exactly as it appears in the file.
- **Type** — string, integer, float, boolean, array, object, null.
- **Meaning** — what the field represents in the domain.
- **Constraints** — required vs optional, controlled vocabulary, range, format.

For controlled vocabularies (enums), list every valid value and its meaning.
For numeric fields with a semantic scale (e.g. a confidence score), document
the scale explicitly.

```markdown
### Field: `status`
| value | meaning |
|---|---|
| `draft` | Not yet reviewed |
| `verified` | Confirmed against primary source |
| `disputed` | Conflicting sources exist |
```

**Why this matters:** Without an explicit schema, the LLM will infer field
meanings from names and existing values — which works until it doesn't.
Explicit documentation eliminates ambiguity and prevents invented values.

---

### 3. Workflows

Define one named workflow per type of user request. Each workflow is a numbered
sequence of steps the LLM must follow in order.

Structure each workflow as:

```markdown
## Workflow [Letter] — [Short name]

Use this workflow when [describe the trigger condition].

**Step 1 — [Action name].**
[Detailed instruction. Be specific about edge cases.]

**Step 2 — [Action name].**
[...]
```

Common workflow types:

| Workflow type | Trigger |
|---|---|
| **Append** | User provides new data to add (links, entries, records). |
| **Parse** | User provides a source (URL, document) to extract data from. |
| **Correct** | User gives a verbal instruction to modify existing data. |
| **Query** | User asks a question about the data (read-only). |
| **Validate** | User asks the LLM to check the data for errors or inconsistencies. |

You do not need all five. Define only the workflows your dataset actually needs.

**Step granularity:** Each step should be one atomic action. If a step requires
a decision, state the decision criteria explicitly. If a step can fail, state
what the LLM should do on failure (flag, skip, ask the user).

---

### 4. Output contract

Specify exactly what the LLM must return. Be precise. Ambiguity here causes
the most common failure mode: the LLM returns a helpful summary instead of
the updated data file.

Minimum required elements:

**a) Change log** — a structured list of every modification made, using
consistent prefixes so the user can scan it quickly. Define your prefix
vocabulary:

```markdown
[ENTRY+]   new entry added
[ENTRY-]   entry removed
[FIELD~]   field value modified
[FLAG]     something the LLM could not resolve — requires user decision
```

**b) Full data file** — the complete updated file in a fenced code block.
Not a diff. Not a snippet. The entire file. The user should be able to
copy-paste it directly and save it.

```markdown
## Output contract

Every response that modifies the data must:

1. List every change made using the prefixes above.
2. Return the complete updated `your_data.json` in a fenced code block.
   Not a diff. Not a snippet. The entire file.
```

**Why full file, not diff:** Non-technical users cannot apply diffs. A complete
file is always safe to save. The cost of returning a larger response is lower
than the cost of a user corrupting their data by misapplying a patch.

---

### 5. Hard constraints

List the things the LLM must never do, stated as explicit prohibitions. These
are your data quality guardrails.

```markdown
## Hard constraints — never do these

- **Never rename an existing `id` field.** IDs are permanent keys.
- **Never create an entry without a [required field].**
- **Never infer [relationship X] from [indirect evidence Y].**
- **Never return partial data.** Always return the complete file.
- **Never silently drop unresolved items.** Always flag them.
```

State each constraint as a bold prohibition followed by a one-sentence
explanation of why it exists. The explanation helps the LLM understand the
intent, not just the rule — which improves compliance on edge cases.

---

### 6. (Optional) Domain glossary

If your dataset uses domain-specific terminology that an LLM might
misinterpret, add a short glossary. This is especially important for:

- Terms that have a general meaning and a domain-specific meaning.
- Abbreviations or initialisms.
- Proper nouns that are also common words.

```markdown
## Glossary

| term | meaning in this dataset |
|---|---|
| `bani` | Stylistic school/lineage in Carnatic music — not a person's name. |
| `rasika` | A knowledgeable connoisseur of Carnatic music. |
| `confidence` | Sourcing quality of a relationship claim, not statistical confidence. |
```

---

## Design principles

### Address the LLM directly

Write in the second person imperative: "You have received…", "When given X,
do the following…", "Never do Y." Do not write for a human reader. The human
will not read this file — the LLM will.

### Be explicit about failure modes

For every step that can fail, state what failure looks like and what to do.
The two most common failure modes are:

1. **Unresolvable match** — the LLM cannot match an input to an existing entry.
   Instruction: flag it, do not silently drop it, do not invent an entry.
2. **Ambiguous instruction** — the user's request could be interpreted multiple
   ways. Instruction: state the ambiguity, propose the most likely interpretation,
   ask for confirmation before acting.

### Separate schema from workflow

The schema section tells the LLM what the data means. The workflow sections
tell the LLM what to do. Keep them separate. A LLM that understands the schema
but has no workflow instructions will improvise — which is unpredictable. A LLM
that has workflow instructions but no schema will apply them mechanically without
understanding — which produces plausible-looking but wrong output.

### Version your READYOU.md

If your dataset evolves, your READYOU.md must evolve with it. Add a version
line at the top:

```markdown
<!-- READYOU version: 1.2 — last updated 2025-04 -->
```

This helps you track which sessions used which version of the instructions,
and helps collaborators know whether their copy is current.

### Keep it short enough to fit in context

A READYOU.md that is too long will be truncated or deprioritised by the LLM.
Aim for under 500 lines. If your schema is very large, consider splitting it:
keep the most-used fields in the main READYOU.md and put the full reference in
a separate `SCHEMA.md` that the user can optionally include.

---

## Checklist — before you ship your READYOU.md

- [ ] Preamble states what the data file is and what the governing principle is.
- [ ] Every field in the data file is documented with type, meaning, and constraints.
- [ ] Every controlled vocabulary is listed with all valid values.
- [ ] Every workflow the user will need is defined as a numbered step sequence.
- [ ] Each workflow step handles its failure mode explicitly.
- [ ] The output contract specifies a change log format and requires the full file.
- [ ] Hard constraints are stated as explicit prohibitions with explanations.
- [ ] The file is addressed to the LLM in second-person imperative.
- [ ] The file fits comfortably in a single context window (< 500 lines).

---

## Example instances

| dataset | READYOU.md location | notes |
|---|---|---|
| Carnatic guru-shishya graph | `carnatic/data/READYOU.md` | Reference implementation. Nodes + edges + YouTube recordings. Three workflows: YouTube append, Wikipedia parse, verbal correction. |

To add your own instance to this table, open a pull request.

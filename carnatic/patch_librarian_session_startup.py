#!/usr/bin/env python3
"""
patch_librarian_session_startup.py

One-shot transform: replaces the Librarian's session startup section in .roomodes
with the ADR-014 CLI-first protocol.

Usage:
    python3 carnatic/patch_librarian_session_startup.py [--dry-run]

With --dry-run: prints the transformed JSON to stdout, does not write.
Without --dry-run: writes back to .roomodes in place.
"""

import json
import sys
import copy
from pathlib import Path

ROOMODES_PATH = Path(".roomodes")

OLD_STARTUP = (
    "## Session startup\n"
    "At the start of every session:\n"
    "1. Read `carnatic/data/musicians.json` with the read_file tool.\n"
    "2. Read `carnatic/data/compositions.json` with the read_file tool.\n"
    "You do not need to read READYOU.md — its full ruleset is embedded below."
)

NEW_STARTUP = (
    "## Session startup\n"
    "At the start of every session:\n"
    "1. Run `python3 carnatic/cli.py stats` to orient — replaces reading "
    "`musicians.json` and `compositions.json` in full.\n"
    "2. Use targeted CLI queries (see **CLI Tools** section below) before any "
    "`read_file` call. Full file reads are reserved for patching sessions where "
    "you need to construct an `apply_diff` block.\n"
    "3. Read the **Open questions** section in `carnatic/.clinerules` — it is "
    "the living memory of this project.\n"
    "You do not need to read READYOU.md — its full ruleset is embedded below.\n"
    "\n"
    "---\n"
    "\n"
    "## CLI Tools (ADR-014) — run these instead of reading JSON files\n"
    "```bash\n"
    "# Orientation\n"
    "python3 carnatic/cli.py stats\n"
    "\n"
    "# Existence checks (exit 0 = found, exit 1 = not found)\n"
    "python3 carnatic/cli.py musician-exists   <id_or_label>\n"
    "python3 carnatic/cli.py raga-exists       <id_or_name>\n"
    "python3 carnatic/cli.py composition-exists <id_or_title>\n"
    "python3 carnatic/cli.py recording-exists  <id_or_title>\n"
    "python3 carnatic/cli.py url-exists        <youtube_url>\n"
    "\n"
    "# Lookup (compact summary; add --json for full object)\n"
    "python3 carnatic/cli.py get-musician      <id>\n"
    "python3 carnatic/cli.py get-raga          <id>\n"
    "python3 carnatic/cli.py get-composition   <id>\n"
    "python3 carnatic/cli.py gurus-of          <musician_id>\n"
    "python3 carnatic/cli.py shishyas-of       <musician_id>\n"
    "python3 carnatic/cli.py lineage           <musician_id>\n"
    "python3 carnatic/cli.py recordings-for    <musician_id>\n"
    "python3 carnatic/cli.py compositions-in-raga <raga_id>\n"
    "\n"
    "# Validation (run after any apply_diff patch)\n"
    "python3 carnatic/cli.py validate\n"
    "```\n"
    "\n"
    "## YouTube ingestion — mandatory pre-checks (before Workflow A Step 1)\n"
    "1. `python3 carnatic/cli.py url-exists <url>` — if FOUND, report and stop.\n"
    "2. `python3 carnatic/cli.py musician-exists \"<artist name>\"` — note exact id "
    "if FOUND; flag if NOT FOUND.\n"
    "3. `python3 carnatic/cli.py raga-exists \"<raga name>\"` — note exact id if "
    "FOUND; add raga first if NOT FOUND.\n"
    "4. `python3 carnatic/cli.py composition-exists \"<composition name>\"` — note "
    "exact id if FOUND; add composition first if NOT FOUND."
)


def transform(data: dict) -> tuple[dict, list[str]]:
    data = copy.deepcopy(data)
    changelog = []

    for mode in data.get("customModes", []):
        if mode.get("slug") != "librarian":
            continue

        instructions = mode.get("customInstructions", "")
        if OLD_STARTUP not in instructions:
            changelog.append("  [librarian] WARNING: old startup text not found — already patched or schema changed")
            return data, changelog

        mode["customInstructions"] = instructions.replace(OLD_STARTUP, NEW_STARTUP, 1)
        changelog.append("  [librarian] session startup replaced with ADR-014 CLI-first protocol")
        return data, changelog

    changelog.append("  ERROR: librarian slug not found in .roomodes")
    return data, changelog


def main():
    dry_run = "--dry-run" in sys.argv

    raw = ROOMODES_PATH.read_text(encoding="utf-8")
    data = json.loads(raw)

    transformed, changelog = transform(data)
    output = json.dumps(transformed, indent=2, ensure_ascii=False)

    print("## patch_librarian_session_startup.py")
    print(f"   source: {ROOMODES_PATH}")
    print(f"   mode:   {'DRY RUN — no file written' if dry_run else 'LIVE — writing to disk'}")
    print()
    print("Changes:")
    for line in changelog:
        print(line)
    print()

    if dry_run:
        print("--- transformed .roomodes (stdout) ---")
        print(output)
    else:
        ROOMODES_PATH.write_text(output, encoding="utf-8")
        print(f"Written: {ROOMODES_PATH} ({len(output)} bytes)")


if __name__ == "__main__":
    main()

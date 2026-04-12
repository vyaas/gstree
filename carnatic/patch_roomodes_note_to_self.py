#!/usr/bin/env python3
"""
patch_roomodes_note_to_self.py — append a dated learning log entry to an
agent's subsection in carnatic/.clinerules.

The learning logs have moved from .roomodes to carnatic/.clinerules so that
agent character (.roomodes) and agent memory (.clinerules) are cleanly
separated.

Usage:
    python3 carnatic/patch_roomodes_note_to_self.py \\
        --slug <agent-slug> \\
        --entry "YYYY-MM-DD: <one plain-prose sentence>" \\
        [--dry-run]

Agent slugs:
    librarian        → ### 📚 Librarian
    carnatic-coder   → ### 🎵 Carnatic Coder
    graph-architect  → ### 🏛️ Graph Architect
    orchestrator     → ### 🪃 Orchestrator

With --dry-run: prints the transformed file to stdout, does not write.
Without --dry-run: writes back to carnatic/.clinerules in place.
"""

import sys
from pathlib import Path

CLINERULES_PATH = Path("carnatic/.clinerules")

# Maps agent slug → the exact subsection header in .clinerules
SLUG_TO_HEADER = {
    "librarian":       "### 📚 Librarian",
    "carnatic-coder":  "### 🎵 Carnatic Coder",
    "graph-architect": "### 🏛️ Graph Architect",
    "orchestrator":    "### 🪃 Orchestrator",
}

# The section that contains all agent logs
SECTION_HEADER = "## Agent learning logs"


def append_log_entry(text: str, slug: str, entry: str) -> tuple[str, list[str]]:
    """
    Append a dated entry under the agent's subsection in .clinerules.
    Returns (modified_text, changelog).
    """
    changelog = []

    header = SLUG_TO_HEADER.get(slug)
    if header is None:
        changelog.append(f"ERROR: unknown slug '{slug}'. Valid slugs: {list(SLUG_TO_HEADER)}")
        return text, changelog

    if SECTION_HEADER not in text:
        changelog.append(f"ERROR: '{SECTION_HEADER}' section not found in {CLINERULES_PATH}")
        return text, changelog

    if header not in text:
        changelog.append(f"ERROR: subsection '{header}' not found in {CLINERULES_PATH}")
        return text, changelog

    # Find the subsection header and insert the entry after the last existing entry
    # (or directly after the header if no entries yet)
    lines = text.splitlines(keepends=True)
    header_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == header:
            header_idx = i
            break

    if header_idx is None:
        changelog.append(f"ERROR: could not locate '{header}' line")
        return text, changelog

    # Find the insertion point: last '- 20' entry line within this subsection,
    # or the blank line immediately after the header if no entries yet.
    # Stop at the next '###' header or end of file.
    insert_after = header_idx  # default: right after the header
    for i in range(header_idx + 1, len(lines)):
        stripped = lines[i].rstrip()
        if stripped.startswith("### ") and i != header_idx:
            break  # next subsection — stop
        if stripped.startswith("- 20"):
            insert_after = i  # keep advancing to the last entry

    # Build the new entry line
    entry_line = f"- {entry}\n" if not entry.startswith("- ") else f"{entry}\n"

    lines.insert(insert_after + 1, entry_line)
    changelog.append(f"[{slug}] appended: {entry_line.rstrip()}")

    return "".join(lines), changelog


def parse_args():
    """Minimal arg parser — avoids argparse dependency."""
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    slug = None
    entry = None
    i = 0
    while i < len(args):
        if args[i] == "--slug" and i + 1 < len(args):
            slug = args[i + 1]; i += 2
        elif args[i] == "--entry" and i + 1 < len(args):
            entry = args[i + 1]; i += 2
        else:
            i += 1
    return dry_run, slug, entry


def main():
    dry_run, slug, entry = parse_args()

    if not slug or not entry:
        print(__doc__)
        sys.exit(1)

    text = CLINERULES_PATH.read_text(encoding="utf-8")
    transformed, changelog = append_log_entry(text, slug, entry)

    print("## patch_roomodes_note_to_self.py")
    print(f"   target: {CLINERULES_PATH}")
    print(f"   mode:   {'DRY RUN — no file written' if dry_run else 'LIVE — writing to disk'}")
    print()
    print("Changes:")
    for line in changelog:
        print(line)
    print()

    if dry_run:
        print(f"--- transformed {CLINERULES_PATH} (stdout) ---")
        print(transformed)
    else:
        CLINERULES_PATH.write_text(transformed, encoding="utf-8")
        print(f"Written: {CLINERULES_PATH} ({len(transformed)} bytes)")


if __name__ == "__main__":
    main()

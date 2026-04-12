#!/usr/bin/env python3
"""
Add Akkarai Subbulakshmi's 69 co-performer youtube entries.
Run: python3 carnatic/playlists/ingest_akkarai_youtube.py [--dry-run]
"""
import subprocess, sys, json

DRY_RUN = "--dry-run" in sys.argv

def run(cmd):
    if DRY_RUN:
        print(f"[DRY-RUN] {' '.join(str(c) for c in cmd)}")
        return True
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(f"  {out}")
    return r.returncode == 0

def wc(*args):
    run(["python3", "carnatic/write_cli.py"] + list(args))

# Build the 69 entries by cross-referencing TMK's youtube array with playlist_metadata.json
playlist = json.load(open("playlist_metadata.json"))
musicians = json.load(open("carnatic/data/musicians.json"))
tmk = next(n for n in musicians["nodes"] if n["id"] == "tm_krishna")

tmk_by_vid = {}
for e in tmk.get("youtube", []):
    u = e["url"]
    if "youtu.be/" in u:
        vid = u.split("youtu.be/")[-1].split("?")[0]
    elif "watch?v=" in u:
        vid = u.split("watch?v=")[-1].split("&")[0]
    else:
        continue
    tmk_by_vid[vid] = e

akkarai_items = []
for item in playlist:
    desc = item.get("description", "")
    if "Akkarai Subhalakshmi" in desc or "Akkarai Subbulakshmi" in desc:
        akkarai_items.append(item)

print(f"\n=== ADD YOUTUBE ENTRIES TO akkarai_subbulakshmi ({len(akkarai_items)} tracks) ===\n")

for item in akkarai_items:
    url = item.get("url", "")
    title = item.get("title", "")
    if "watch?v=" in url:
        vid = url.split("watch?v=")[-1].split("&")[0]
    else:
        continue

    if vid in tmk_by_vid:
        e = tmk_by_vid[vid]
        cmd = ["add-youtube",
               "--musician-id", "akkarai_subbulakshmi",
               "--url", url,
               "--label", e["label"]]
        if e.get("composition_id"):
            cmd += ["--composition-id", e["composition_id"]]
        if e.get("raga_id"):
            cmd += ["--raga-id", e["raga_id"]]
        if e.get("year"):
            cmd += ["--year", str(e["year"])]
    else:
        # Not yet in TMK's array — use playlist title as label
        cmd = ["add-youtube",
               "--musician-id", "akkarai_subbulakshmi",
               "--url", url,
               "--label", title]

    wc(*cmd)

print("\nDone.\n")

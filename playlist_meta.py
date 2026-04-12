#!/usr/bin/env python3
"""
Extract metadata (title, description, clean URL) for every video in a YouTube playlist.
Outputs a JSON file and a human-readable text summary.

Usage:
    python playlist_meta.py <playlist_url> [--out results.json]

Requires:
    pip install yt-dlp
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yt_dlp


def extract_playlist_metadata(
    playlist_url: str,
    quiet: bool = True,
) -> list[dict[str, Any]]:
    """
    Extract metadata for every video in a YouTube playlist.

    Parameters
    ----------
    playlist_url : str
        Full URL of the YouTube playlist.
    quiet : bool
        Suppress yt-dlp console output.

    Returns
    -------
    list[dict[str, Any]]
        List of dicts, each containing:
            - index     : 1-based position in the playlist
            - id        : YouTube video ID
            - url       : Clean video URL (no playlist parameters)
            - title     : Full video title
            - description : Full video description
            - uploader  : Channel name
            - duration  : Duration in seconds
            - upload_date : YYYYMMDD string
    """
    ydl_opts: dict[str, Any] = {
        "quiet": quiet,
        "extract_flat": False,       # fetch full metadata per video
        "skip_download": True,       # never touch the video stream
        "ignoreerrors": True,        # skip deleted / private videos gracefully
        "no_warnings": quiet,
    }

    results: list[dict[str, Any]] = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info: dict[str, Any] | None = ydl.extract_info(playlist_url, download=False)

        if info is None:
            raise RuntimeError("yt-dlp returned no data. Check the URL.")

        entries: list[dict[str, Any]] = info.get("entries", [])

        for idx, entry in enumerate(entries, start=1):
            if entry is None:
                # Deleted or private video placeholder
                continue

            video_id: str = entry.get("id", "")
            clean_url: str = f"https://www.youtube.com/watch?v={video_id}"

            results.append(
                {
                    "index": idx,
                    "id": video_id,
                    "url": clean_url,
                    "title": entry.get("title", ""),
                    "description": entry.get("description", ""),
                    "uploader": entry.get("uploader", ""),
                    "duration": entry.get("duration"),          # seconds, int
                    "upload_date": entry.get("upload_date", ""), # YYYYMMDD
                }
            )

    return results


def write_text_summary(
    records: list[dict[str, Any]],
    path: Path,
) -> None:
    """Write a human-readable summary file alongside the JSON."""
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(f"[{rec['index']:>3}] {rec['title']}\n")
            f.write(f"      URL     : {rec['url']}\n")
            f.write(f"      Uploader: {rec['uploader']}\n")
            f.write(f"      Date    : {rec['upload_date']}\n")
            f.write(f"      Duration: {rec['duration']}s\n")
            desc_preview: str = (rec["description"] or "")[:200].replace("\n", " ")
            f.write(f"      Desc    : {desc_preview}...\n\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dump YouTube playlist metadata to JSON (no download)."
    )
    parser.add_argument("url", help="YouTube playlist URL")
    parser.add_argument(
        "--out",
        default="playlist_metadata.json",
        help="Output JSON file path (default: playlist_metadata.json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show yt-dlp progress output",
    )
    args = parser.parse_args()

    print(f"Fetching playlist metadata from:\n  {args.url}\n")

    try:
        records = extract_playlist_metadata(
            playlist_url=args.url,
            quiet=not args.verbose,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not records:
        print("No videos found. Check the playlist URL or privacy settings.")
        sys.exit(1)

    # Write JSON
    out_path = Path(args.out)
    out_path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(records)} videos → {out_path}")

    # Write human-readable summary alongside the JSON
    summary_path = out_path.with_suffix(".txt")
    write_text_summary(records, summary_path)
    print(f"Summary        → {summary_path}")

    # Quick preview
    print(f"\nFirst 3 titles:")
    for rec in records[:3]:
        print(f"  [{rec['index']}] {rec['title']}")


if __name__ == "__main__":
    main()
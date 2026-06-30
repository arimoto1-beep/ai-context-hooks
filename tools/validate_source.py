"""Validate that each context hook can trace back to a raw source file."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_time_seconds(value: str) -> int | None:
    """Return total seconds for HH:MM:SS, or None if the format is invalid."""
    m = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})", value.strip())
    if m is None:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))


def _strip_backticks(value: str) -> str:
    return value.strip().strip("`").strip()


def parse_structured_source(text: str) -> dict | None:
    """
    Parse ## source section with "- ref:" and "- ranges:" entries.
    Returns {"file": str|None, "ranges": list[dict]|None} or None if section not found.
    """
    in_source = False
    in_ranges = False
    found_source_heading = False
    source_file = None
    ranges: list[dict] = []

    for line in text.splitlines():
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if heading:
            if heading.group(1).strip().lower() == "source":
                in_source = True
                in_ranges = False
                found_source_heading = True
            elif in_source:
                break
            continue

        if not in_source:
            continue

        ref_match = re.match(r"\s*-\s+ref\s*:\s*(.+?)\s*$", line)
        if ref_match:
            source_file = _strip_backticks(ref_match.group(1))
            continue

        if re.match(r"\s*-\s+ranges\s*:\s*$", line):
            in_ranges = True
            continue

        if in_ranges:
            range_match = re.match(r"\s+-\s+(.+?)\s*$", line)
            if range_match:
                range_str = _strip_backticks(range_match.group(1))
                parts = range_str.split("-", 1)
                if len(parts) == 2:
                    ranges.append({"start": parts[0].strip(), "end": parts[1].strip()})
                else:
                    ranges.append({"_raw": range_str})
            elif line.strip() and not line.strip().startswith("-"):
                in_ranges = False

    if not found_source_heading:
        return None
    return {"file": source_file, "ranges": ranges if ranges else None}


def parse_inline_source(text: str) -> dict | None:
    """
    Parse old table-format source: | **source** | file（start〜end） |
    Returns {"file": str|None, "ranges": list[dict]|None} or None if not found.
    """
    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = re.sub(r"\*\*|__", "", cells[0]).strip().casefold()
        if key == "source":
            cell_value = cells[1].strip()
            m = re.match(
                r"(.+?)（(\d{1,2}:\d{2}:\d{2})[〜~](\d{1,2}:\d{2}:\d{2})）",
                cell_value,
            )
            if m:
                return {
                    "file": m.group(1).strip(),
                    "ranges": [{"start": m.group(2).strip(), "end": m.group(3).strip()}],
                }
            return {"file": cell_value or None, "ranges": None}
    return None


def parse_hook_source(text: str) -> dict:
    """Extract source.file and source.ranges from a hook file."""
    structured = parse_structured_source(text)
    if structured is not None:
        return structured
    inline = parse_inline_source(text)
    if inline is not None:
        return inline
    return {"file": None, "ranges": None}


def resolve_raw_file(source_file: str, raw_dir: Path) -> Path | None:
    """Return the resolved raw file path, or None if not found."""
    candidate = raw_dir / Path(source_file).name
    if candidate.exists():
        return candidate
    candidate2 = raw_dir / source_file
    if candidate2.exists():
        return candidate2
    return None


def validate_hook(hook_path: Path, raw_dir: Path) -> list[str]:
    errors: list[str] = []

    try:
        text = hook_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"could not read file: {exc}, file={hook_path}"]

    source = parse_hook_source(text)

    if source["file"] is None:
        errors.append(f"missing source.file: {hook_path}")
    else:
        if resolve_raw_file(source["file"], raw_dir) is None:
            errors.append(f"raw file not found: {raw_dir / Path(source['file']).name}")

    if source["ranges"] is None:
        errors.append(f"missing source.ranges: {hook_path}")
    else:
        for r in source["ranges"]:
            if "_raw" in r:
                errors.append(f"missing range.start: {hook_path}")
                errors.append(f"missing range.end: {hook_path}")
                continue

            has_start = "start" in r
            has_end = "end" in r

            if not has_start:
                errors.append(f"missing range.start: {hook_path}")
            if not has_end:
                errors.append(f"missing range.end: {hook_path}")

            if has_start and has_end:
                start_sec = parse_time_seconds(r["start"])
                end_sec = parse_time_seconds(r["end"])

                if start_sec is None:
                    errors.append(f"invalid time format: {hook_path}, value={r['start']}")
                if end_sec is None:
                    errors.append(f"invalid time format: {hook_path}, value={r['end']}")
                if start_sec is not None and end_sec is not None and start_sec > end_sec:
                    errors.append(f"invalid range: start > end, file={hook_path}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that each context hook can trace back to a raw source file."
    )
    parser.add_argument("hook_dir", help="Directory containing hook files (ctx-*.md)")
    parser.add_argument("raw_dir", help="Directory containing raw source files")
    args = parser.parse_args()

    hook_dir = Path(args.hook_dir)
    raw_dir = Path(args.raw_dir)

    all_errors: list[str] = []
    for hook_path in sorted(hook_dir.glob("ctx-*.md")):
        all_errors.extend(validate_hook(hook_path, raw_dir))

    if all_errors:
        print("NG: source references")
        for error in all_errors:
            print(f"- {error}")
        return 1

    print("OK: source references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

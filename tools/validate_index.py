"""Validate consistency between an index.md and individual hook files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_index_rows(text: str) -> list[dict[str, str]]:
    """Parse table rows from index.md, returning one dict per data row."""
    rows: list[dict[str, str]] = []
    header: list[str] | None = None

    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        # Skip separator rows (only - and : characters)
        if all(re.fullmatch(r"[-:]+", c) for c in cells if c):
            continue
        lower = [c.lower() for c in cells]
        if header is None:
            if "id" in lower and "hook" in lower:
                header = lower
            continue
        if len(cells) < len(header):
            continue
        rows.append({header[i]: cells[i] for i in range(len(header))})

    return rows


def hook_path_from_cell(hook_cell: str, hook_dir: Path) -> Path | None:
    """Extract the hook file Path from a Markdown link cell."""
    m = re.search(r"\[([^\]]*)\]\(([^)]+)\)", hook_cell)
    if m:
        return hook_dir / m.group(2)
    return None


def parse_hook_field(text: str, field: str) -> str | None:
    """Return the value of a named key-value row from a hook file's Markdown table."""
    target = field.lower()
    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = re.sub(r"\*\*|__", "", cells[0]).strip().lower()
        if key == target:
            return cells[1].strip()
    return None


def normalize_labels(raw: str) -> set[str]:
    return {lbl.strip() for lbl in raw.split(",") if lbl.strip()}


def validate_index(index_path: Path, hook_dir: Path) -> list[str]:
    errors: list[str] = []

    index_text = index_path.read_text(encoding="utf-8")
    rows = parse_index_rows(index_text)

    referenced: set[Path] = set()

    for row in rows:
        index_id = row.get("id", "").strip()
        hook_path = hook_path_from_cell(row.get("hook", ""), hook_dir)

        if hook_path is None:
            continue

        referenced.add(hook_path.resolve())

        # Check 1: referenced hook file exists
        if not hook_path.exists():
            errors.append(f"missing hook file: {hook_path}")
            continue

        hook_text = hook_path.read_text(encoding="utf-8")

        # Check 3: id match
        hook_id = parse_hook_field(hook_text, "id")
        if hook_id is not None and hook_id != index_id:
            errors.append(
                f"id mismatch: index={index_id}, hook={hook_id}, file={hook_path}"
            )

        # Check 4: topic match
        index_topic = row.get("topic", "").strip()
        hook_topic = parse_hook_field(hook_text, "topic")
        if hook_topic is not None and hook_topic != index_topic:
            errors.append(
                f"topic mismatch: id={index_id}, "
                f"index={index_topic!r}, hook={hook_topic!r}"
            )

        # Check 5: confidence match
        index_conf = row.get("confidence", "").strip().lower()
        hook_conf_raw = parse_hook_field(hook_text, "confidence")
        if hook_conf_raw is not None:
            hook_conf = hook_conf_raw.strip().lower()
            if hook_conf != index_conf:
                errors.append(
                    f"confidence mismatch: id={index_id}, "
                    f"index={index_conf}, hook={hook_conf}"
                )

        # Check 6: labels match (order-insensitive, whitespace-insensitive)
        index_labels = normalize_labels(row.get("labels", ""))
        hook_labels_raw = parse_hook_field(hook_text, "labels")
        if hook_labels_raw is not None:
            hook_labels = normalize_labels(hook_labels_raw)
            if hook_labels != index_labels:
                errors.append(
                    f"labels mismatch: id={index_id}, "
                    f"index={sorted(index_labels)}, hook={sorted(hook_labels)}"
                )

    # Check 2: every ctx-*.md in hook_dir is listed in the index
    for hook_file in sorted(hook_dir.glob("ctx-*.md")):
        if hook_file.resolve() not in referenced:
            errors.append(f"hook not listed in index: {hook_file}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate consistency between index.md and hook files."
    )
    parser.add_argument("index", help="Path to the index Markdown file")
    parser.add_argument("hook_dir", help="Directory containing hook files")
    args = parser.parse_args()

    index_path = Path(args.index)
    hook_dir = Path(args.hook_dir)

    try:
        errors = validate_index(index_path, hook_dir)
    except (OSError, UnicodeError) as exc:
        print(f"NG: {args.index}")
        print(f"- could not read file: {exc}")
        return 1

    if errors:
        print(f"NG: {args.index}")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: {args.index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

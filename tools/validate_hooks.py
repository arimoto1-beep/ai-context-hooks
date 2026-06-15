"""Validate the minimum structure of a Markdown context hook."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_SECTIONS = {
    "id": ("id", "識別子"),
    "source": ("source", "原文参照", "出どころ"),
    "topic": ("topic", "topics", "話題", "トピック"),
    "labels": ("labels", "ラベル", "扱い"),
    "confidence": ("confidence", "確度", "確信度"),
    "hook_note": ("hook_note", "hook note", "フックメモ", "索引メモ", "メモ"),
    "ai_usage": ("ai_usage", "AIへの指示", "AIでの扱い", "AI用途"),
    "cautions": ("cautions", "注意事項", "誤用防止", "注意"),
}
CONFIDENCE_VALUES = ("high", "medium", "low")


def normalize_label(value: str) -> str:
    """Remove common Markdown decoration and normalize a field label."""
    value = value.strip().strip("#").strip()
    value = value.replace("**", "").replace("__", "").replace("`", "")
    value = value.rstrip(":：").strip()
    return " ".join(value.casefold().split())


ALIASES = {
    normalize_label(alias): section
    for section, aliases in REQUIRED_SECTIONS.items()
    for alias in aliases
}


def section_for(label: str) -> str | None:
    return ALIASES.get(normalize_label(label))


def find_sections(text: str) -> dict[str, list[str]]:
    """Find fields expressed as headings, table rows, or key-value lines."""
    found: dict[str, list[str]] = {}
    active_heading: str | None = None

    for line in text.splitlines():
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if heading:
            active_heading = section_for(heading.group(1))
            if active_heading:
                found.setdefault(active_heading, [])
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if "|" in line and len(cells) >= 2:
            section = section_for(cells[0])
            if section:
                found.setdefault(section, []).append(" ".join(cells[1:]))
                continue

        key_value = re.match(
            r"^\s*(?:[-*+]\s+)?(.+?)\s*[:：]\s*(.*)$", line
        )
        if key_value:
            section = section_for(key_value.group(1))
            if section:
                found.setdefault(section, []).append(key_value.group(2))
                continue

        if active_heading:
            found[active_heading].append(line)

    return found


def validate(text: str) -> list[str]:
    found = find_sections(text)
    errors = [
        f"missing required section: {section}"
        for section in REQUIRED_SECTIONS
        if section not in found
    ]

    if "confidence" in found:
        confidence_text = "\n".join(found["confidence"]).casefold()
        if not any(
            re.search(rf"\b{value}\b", confidence_text)
            for value in CONFIDENCE_VALUES
        ):
            errors.append("invalid confidence: expected high, medium, or low")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the minimum structure of a Markdown context hook."
    )
    parser.add_argument("path", help="Markdown context hook to validate")
    args = parser.parse_args()
    path = Path(args.path)

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"NG: {args.path}")
        print(f"- could not read UTF-8 file: {exc}")
        return 1

    errors = validate(text)
    if errors:
        print(f"NG: {args.path}")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

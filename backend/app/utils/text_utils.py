from __future__ import annotations


def humanize_code(value: str) -> str:
    return value.replace("_", " ").strip()


def titleize_label(value: str) -> str:
    return humanize_code(value).title()

"""Strict, offline pairing checks for normalized tool event traces."""

import json
from pathlib import Path
from typing import Any


class InvalidTrace(Exception):
    """Raised when any input row is outside the frozen trace format."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise InvalidTrace
        obj[key] = value
    return obj


def _reject_constant(_: str) -> None:
    raise InvalidTrace


def validate_text(text: str) -> dict[str, Any]:
    """Validate complete JSONL text and return the contract result."""
    calls: dict[str, list[int]] = {}
    results: dict[str, list[int]] = {}
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    rows = normalized.split("\n")
    if rows and rows[-1] == "":
        rows.pop()  # A final line terminator does not create an extra record.
    for line, raw in enumerate(rows, 1):
        if not raw.strip():
            raise InvalidTrace
        try:
            row = json.loads(raw, object_pairs_hook=_unique_object,
                             parse_constant=_reject_constant)
        except (ValueError, TypeError, RecursionError):
            raise InvalidTrace from None
        if (not isinstance(row, dict) or set(row) != {"id", "type"}
                or not isinstance(row["id"], str) or not row["id"]
                or row["type"] not in ("call", "result")):
            raise InvalidTrace
        target = calls if row["type"] == "call" else results
        target.setdefault(row["id"], []).append(line)

    findings: list[dict[str, Any]] = []
    for event_map, kind in ((calls, "duplicate_call"), (results, "duplicate_result")):
        for positions in event_map.values():
            findings.extend({"line": line, "kind": kind} for line in positions[1:])
    for ident, positions in results.items():
        earlier_calls = calls.get(ident, [])
        for line in positions:
            if not any(call_line < line for call_line in earlier_calls):
                findings.append({"line": line, "kind": "orphan_result"})
    for ident, positions in calls.items():
        first_call = positions[0]
        if not any(result_line > first_call for result_line in results.get(ident, [])):
            findings.append({"line": first_call, "kind": "missing_result"})
    findings.sort(key=lambda item: (item["line"], item["kind"]))
    return {"status": "violations" if findings else "valid",
            "record_count": len(rows), "findings": findings}


def validate_file(path: str | Path) -> dict[str, Any]:
    """Read strict UTF-8 input and validate it without exposing failures."""
    try:
        text = Path(path).read_text(encoding="utf-8", errors="strict")
        return validate_text(text)
    except (OSError, UnicodeError, InvalidTrace, ValueError, RecursionError):
        raise InvalidTrace from None

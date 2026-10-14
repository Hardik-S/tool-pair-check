# tool-pair-check

`tool-pair-check` is a small offline Python CLI that reports structural pairing anomalies in **normalized** tool-event JSONL traces. It uses only the Python standard library at runtime and supports Python 3.10+.

It does not validate providers or MCP, execute tools, verify result meaning or provenance, assess security, or repair traces. Normalize events into the documented `{ "id": string, "type": "call" | "result" }` format before checking. Findings say only what the event order shows.

## Install and run

```console
python -m pip install .
tool-pair-check examples/valid.jsonl
```

The CLI prints one compact JSON report. Exit codes are `0` for a clean trace, `1` when pairing findings exist, and `2` for invalid input. Invalid input always prints exactly `{"status":"invalid_input"}` to stdout and nothing to stderr; IDs, paths, trace contents, and exceptions are not disclosed.

## Examples

Clean trace:

```console
tool-pair-check examples/valid.jsonl
{"status":"valid","record_count":2,"findings":[]}
```

Pairing violations:

```console
tool-pair-check examples/violations.jsonl
{"status":"violations","record_count":3,"findings":[{"line":1,"kind":"orphan_result"},{"line":3,"kind":"duplicate_result"}]}
```

Adversarial duplicate/orphan/missing mix:

```console
tool-pair-check examples/adversarial.jsonl
{"status":"violations","record_count":5,"findings":[{"line":2,"kind":"orphan_result"},{"line":3,"kind":"duplicate_call"},{"line":4,"kind":"missing_result"}]}
```

Invalid UTF-8, malformed JSON, duplicate JSON keys, blank rows, non-finite numbers, or rows with any extra/missing/wrong fields produce exit 2 and the fixed invalid-input response. Empty input is a valid empty trace. The full file is validated before a report is emitted.

## Findings

`duplicate_call` marks every call after an ID's first call. `duplicate_result` marks every result after its first result. `orphan_result` marks each result with no earlier call of the same ID, including a result that precedes a later call. `missing_result` marks the first call when there is no result for that ID after it. Duplicate calls do not create additional response requirements. Findings are sorted by line and then kind. IDs compare exactly; no normalization is performed.

## Development

```console
python -m pip install -e ".[test]"
python -m pytest
```

CI tests Ubuntu and Windows with Python 3.10 and 3.13. Synthetic fixtures contain no provider or customer traces.

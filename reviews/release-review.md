# Independent release review

**Verdict: PASS** for the frozen contract reviewed at source commit `83f6dd164fd93c4602b859bd7a478bd0790b9973` (`83f6dd1`). This is an independent validation of that commit, not a release approval or claim that a public release exists.

## Evidence

- Fresh isolated Python 3.13.1 virtual environment: `py -3 -m venv <temp>`; `python -m pip install --disable-pip-version-check ".[test]"` from the repository; package wheel built and installed, with pytest installed as the test extra.
- `python -m pytest -q`: **17 passed**, no skips.
- Installed `tool-pair-check` examples: `valid.jsonl` returned documented valid JSON and exit 0; `violations.jsonl` and `adversarial.jsonl` returned the documented findings and exit 1. A temporary malformed-suffix input returned exactly `{"status":"invalid_input"}` (one JSON line) and exit 2, with empty stderr.
- Additional installed-CLI contract probes: **16 cases passed**. Covered empty input; interleaved and out-of-order distinct IDs; duplicate calls without extra missing requirements; duplicate results; result before a call both with and without a later result; sorted simultaneous findings; exact Unicode IDs (composed/decomposed distinction); CR, LF, and CRLF; invalid UTF-8; malformed suffix; duplicate JSON keys; NaN and Infinity; blank lines; extra fields; and absence of IDs/paths/content from invalid-input output.
- Current GitHub Actions evidence for the reviewed SHA: latest push run [38568625010](https://github.com/Hardik-S/tool-pair-check/actions/runs/38568625010) has all four matrix jobs successful (Ubuntu/Windows × Python 3.10/3.13, zero skips). The associated pull-request run [38568624177](https://github.com/Hardik-S/tool-pair-check/actions/runs/38568624177) also has all four jobs successful.
- Read `README.md` and `LAUNCH.md`: scope boundaries, normalized-input requirement, synthetic-only fixtures, status/exit mapping, and the no-release-before-public-tag gate are accurately stated. The three checked-in examples match their documented output. Invalid-input behavior was verified with a temporary synthetic file, not a checked-in invalid fixture.

## Contract review

Code inspection and CLI probes agree with `CONTRACT.md`: calls/results are matched by exact ID; each later call/result is reported as a duplicate; every result without an earlier call is orphaned; only the first call can be missing, based on whether any result follows it; multiple findings can share a line; and sorting is by line then kind. Parsing rejects non-UTF-8, malformed or duplicate-key JSON, non-finite constants, blank records, and any wrong object shape before producing a report. Output does not include input IDs or paths.

## Commands and record

Commands run from the repository root:

```powershell
py -3 -m venv <fresh-temp-venv>
<fresh-temp-venv>\Scripts\python.exe -m pip install --disable-pip-version-check ".[test]"
<fresh-temp-venv>\Scripts\python.exe -m pytest -q
<fresh-temp-venv>\Scripts\tool-pair-check.exe examples\valid.jsonl
<fresh-temp-venv>\Scripts\tool-pair-check.exe examples\violations.jsonl
<fresh-temp-venv>\Scripts\tool-pair-check.exe examples\adversarial.jsonl
```

Reviewed branch: `issue-1-tool-pair-check`. This report is the only file changed by the review.

## Limits

The local fresh install and additional probes ran on Windows/Python 3.13.1; Python 3.10 and Ubuntu coverage is from the linked successful CI matrix. The tests use synthetic input only. No code repair, merge, tag, publication, or external outreach was performed.

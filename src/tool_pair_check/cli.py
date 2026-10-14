"""Command line interface for tool-pair-check."""

import argparse
import json
import sys

from .core import InvalidTrace, validate_file


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="tool-pair-check",
        description="Check call/result pairing in a normalized JSONL trace.")
    parser.add_argument("trace", help="path to a UTF-8 JSONL trace")
    args = parser.parse_args()
    try:
        report = validate_file(args.trace)
    except InvalidTrace:
        print('{"status":"invalid_input"}')
        return 2
    print(json.dumps(report, ensure_ascii=True, separators=(",", ":")))
    return 1 if report["status"] == "violations" else 0


if __name__ == "__main__":
    sys.exit(main())

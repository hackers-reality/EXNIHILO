#!/usr/bin/env python3
"""Summarize an EXNIHILO experiment without changing the raw data."""

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify and summarize a result")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    data = args.file.read_bytes()
    lines = data.count(b"\n")
    digest = hashlib.sha256(data).hexdigest()

    print(json.dumps({
        "file": str(args.file),
        "bytes": len(data),
        "lines": lines,
        "sha256": digest,
    }, indent=2))


if __name__ == "__main__":
    main()

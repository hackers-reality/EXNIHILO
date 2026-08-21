#!/usr/bin/env python3
"""Reproducible first-pass scan of a raw EXNIHILO dataset.

This intentionally uses no third-party packages and does not modify the dataset.
It searches caller-supplied UTF-8 patterns after generation and reports exact
byte offsets. The generator never receives the patterns.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("patterns", type=Path)
    args = parser.parse_args()

    data = args.dataset.read_bytes()
    digest = hashlib.sha256(data).hexdigest()

    patterns = []
    for line in args.patterns.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text:
            patterns.append(text)

    print(f"Dataset:   {args.dataset}")
    print(f"Bytes:     {len(data):,}")
    print(f"SHA-256:   {digest}")
    print(f"Patterns:  {len(patterns)}")
    print()

    total = 0
    for text in patterns:
        needle = text.encode("utf-8")
        hits = []
        start = 0
        while True:
            pos = data.find(needle, start)
            if pos < 0:
                break
            hits.append(pos)
            start = pos + 1
        total += len(hits)
        if hits:
            preview = ", ".join(str(x) for x in hits[:10])
            suffix = " ..." if len(hits) > 10 else ""
            print(f"{text!r:20} length={len(needle):2} hits={len(hits):4} offsets={preview}{suffix}")
        else:
            print(f"{text!r:20} length={len(needle):2} hits=0")

    print(f"\nTotal hits: {total}")


if __name__ == "__main__":
    main()

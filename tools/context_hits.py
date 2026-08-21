#!/usr/bin/env python3
"""Inspect bytes surrounding selected exact matches without modifying the dataset."""
from __future__ import annotations
import argparse
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("words", nargs="+", help="ASCII/UTF-8 strings to inspect")
    p.add_argument("--context", type=int, default=24)
    p.add_argument("--max-hits", type=int, default=10)
    args = p.parse_args()

    data = args.dataset.read_bytes()
    for word in args.words:
        needle = word.encode("utf-8")
        print(f"\n=== {word!r} ({len(needle)} bytes) ===")
        start = 0
        count = 0
        while count < args.max_hits:
            pos = data.find(needle, start)
            if pos < 0:
                break
            lo = max(0, pos - args.context)
            hi = min(len(data), pos + len(needle) + args.context)
            chunk = data[lo:hi]
            print(f"offset={pos} context=[{lo}:{hi}]")
            print("hex:  " + chunk.hex(" "))
            print("ascii:" + "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk))
            start = pos + 1
            count += 1
        print(f"hits shown: {count}")


if __name__ == "__main__":
    main()

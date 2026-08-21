#!/usr/bin/env python3
"""Measure exact byte-sequence frequencies against the uniform-byte null model."""
from __future__ import annotations
import argparse
import math
from pathlib import Path


def poisson_zero_probability(expected: float) -> float:
    return math.exp(-expected) if expected < 745 else 0.0


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("sequences", type=Path)
    args = p.parse_args()

    data = args.dataset.read_bytes()
    n = len(data)
    print(f"Dataset bytes: {n:,}")

    total = 0
    for line in args.sequences.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text:
            continue
        needle = text.encode("utf-8")
        L = len(needle)
        if L == 0 or L > n:
            continue
        observed = 0
        start = 0
        while True:
            pos = data.find(needle, start)
            if pos < 0:
                break
            observed += 1
            total += 1
            start = pos + 1
        expected = (n - L + 1) / (256 ** L)
        p_zero = poisson_zero_probability(expected)
        print(f"{text!r:20} bytes={L:2} observed={observed:6} expected={expected:.9g} P(zero)≈{p_zero:.6g}")

    print(f"Total observed hits: {total}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Report wordfreq matches grouped by UTF-8 byte length.

This is a post-hoc analysis only; it never modifies the raw dataset.
"""
from __future__ import annotations
import argparse
import hashlib
from collections import Counter
from pathlib import Path
from wordfreq import iter_wordlist, zipf_frequency


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("dataset", type=Path)
    p.add_argument("--lang", default="en")
    p.add_argument("--wordlist", choices=["small", "large", "best"], default="small")
    p.add_argument("--min-length", type=int, default=3)
    p.add_argument("--max-words", type=int, default=50000)
    p.add_argument("--min-zipf", type=float, default=3.0)
    args = p.parse_args()

    data = args.dataset.read_bytes()
    print(f"Dataset bytes: {len(data):,}")
    print(f"SHA-256:       {hashlib.sha256(data).hexdigest()}")
    print(f"Language:      {args.lang}")
    print(f"Wordlist:      {args.wordlist}")

    candidates: dict[bytes, tuple[str, float]] = {}
    for word in iter_wordlist(args.lang, wordlist=args.wordlist):
        if len(candidates) >= args.max_words:
            break
        if len(word) < args.min_length:
            continue
        z = zipf_frequency(word, args.lang)
        if z < args.min_zipf:
            continue
        needle = word.encode("utf-8")
        candidates.setdefault(needle, (word, z))

    # For each byte length, use the candidates of that length and scan once.
    by_len: dict[int, dict[bytes, tuple[str, float]]] = {}
    for needle, meta in candidates.items():
        by_len.setdefault(len(needle), {})[needle] = meta

    print(f"Candidates:     {len(candidates)}")
    print("\nLength  Candidates  Words-with-hit")
    for length in sorted(by_len):
        pool = by_len[length]
        found: set[bytes] = set()
        for i in range(0, len(data) - length + 1):
            needle = data[i:i + length]
            if needle in pool:
                found.add(needle)
        print(f"{length:6}  {len(pool):10}  {len(found):14}")
        if found and length >= 4:
            ranked = sorted(found, key=lambda x: (-pool[x][1], pool[x][0]))
            print("  ", ", ".join(repr(pool[x][0]) for x in ranked[:20]))


if __name__ == "__main__":
    main()

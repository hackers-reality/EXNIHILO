#!/usr/bin/env python3
"""Count word matches and compare them with the uniform-byte null model."""
from __future__ import annotations
import argparse
import hashlib
import math
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
    p.add_argument("--top", type=int, default=100)
    args = p.parse_args()

    data = args.dataset.read_bytes()
    n = len(data)
    print(f"Dataset bytes: {n:,}")
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

    counts: dict[bytes, int] = {k: 0 for k in candidates}
    by_first: dict[int, list[bytes]] = {}
    for needle in candidates:
        by_first.setdefault(needle[0], []).append(needle)

    # Scan once; only inspect candidate lengths beginning at the current byte.
    max_len = max((len(k) for k in candidates), default=0)
    for i, first in enumerate(data):
        for needle in by_first.get(first, ()):
            L = len(needle)
            if i + L <= n and data[i:i + L] == needle:
                counts[needle] += 1

    rows = []
    for needle, observed in counts.items():
        word, z = candidates[needle]
        L = len(needle)
        expected = max(0, n - L + 1) / (256 ** L)
        rows.append((observed, expected, L, z, word))

    hits = [r for r in rows if r[0] > 0]
    hits.sort(key=lambda r: (-r[2], -r[0], -r[3], r[4]))
    print(f"Candidates:     {len(candidates)}")
    print(f"Words with hit: {len(hits)}")
    print("\nword                     bytes observed expected")
    for observed, expected, L, z, word in hits[:args.top]:
        print(f"{word!r:24} {L:5} {observed:8} {expected:.9g}")

    for L in sorted({len(k) for k in candidates}):
        pool = [r for r in rows if r[2] == L]
        observed_words = sum(r[0] > 0 for r in pool)
        expected_hits = sum(r[1] for r in pool)
        print(f"length={L:2} candidates={len(pool):5} words_with_hit={observed_words:5} total_expected_hits={expected_hits:.9g}")


if __name__ == "__main__":
    main()

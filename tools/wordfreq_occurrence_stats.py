#!/usr/bin/env python3
"""Fast wordfreq occurrence counts vs the uniform-byte null model."""
from __future__ import annotations
import argparse
import hashlib
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

    # Trie node: byte -> child node, with terminal bytes stored as key 256.
    root: dict[int, dict] = {}
    meta: dict[bytes, tuple[str, float]] = {}
    for word in iter_wordlist(args.lang, wordlist=args.wordlist):
        if len(meta) >= args.max_words:
            break
        if len(word) < args.min_length:
            continue
        z = zipf_frequency(word, args.lang)
        if z < args.min_zipf:
            continue
        needle = word.encode("utf-8")
        node = root
        for b in needle:
            node = node.setdefault(b, {})
        node[256] = needle
        meta[needle] = (word, z)

    counts: dict[bytes, int] = {k: 0 for k in meta}

    # Scan each starting position once. This replaces one full 100 MB search
    # per word with a shared prefix walk through the trie.
    for i in range(n):
        node = root
        j = i
        while j < n:
            child = node.get(data[j])
            if child is None:
                break
            node = child
            j += 1
            terminal = node.get(256)
            if terminal is not None:
                counts[terminal] += 1

    rows = []
    for needle, observed in counts.items():
        word, z = meta[needle]
        L = len(needle)
        expected = (n - L + 1) / (256 ** L)
        rows.append((observed, expected, L, z, word))

    hits = [r for r in rows if r[0] > 0]
    hits.sort(key=lambda r: (-r[2], -r[0], -r[3], r[4]))
    print(f"Candidates:     {len(meta)}")
    print(f"Words with hit: {len(hits)}")
    print("\nword                     bytes observed expected")
    for observed, expected, L, z, word in hits[:args.top]:
        print(f"{word!r:24} {L:5} {observed:8} {expected:.9g}")

    for L in sorted({len(k) for k in meta}):
        pool = [r for r in rows if r[2] == L]
        observed_words = sum(r[0] > 0 for r in pool)
        expected_hits = sum(r[1] for r in pool)
        print(f"length={L:2} candidates={len(pool):5} words_with_hit={observed_words:5} total_expected_hits={expected_hits:.9g}")


if __name__ == "__main__":
    main()

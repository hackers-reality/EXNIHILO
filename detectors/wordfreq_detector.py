#!/usr/bin/env python3
"""Fast post-hoc wordfreq detector.

The generator never imports this module. Linguistic data is used only after a
raw dataset has been generated and hashed.
"""
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
    args = p.parse_args()

    data = args.dataset.read_bytes()
    print(f"Dataset bytes: {len(data):,}")
    print(f"SHA-256:       {hashlib.sha256(data).hexdigest()}")
    print(f"Language:      {args.lang}")
    print(f"Wordlist:      {args.wordlist}")

    # Build a trie from the candidate words. We then scan the dataset once,
    # instead of calling bytes.find() once for every dictionary entry.
    root: dict[int | None, object] = {}
    checked = 0
    frequencies: dict[bytes, tuple[str, float]] = {}

    for word in iter_wordlist(args.lang, wordlist=args.wordlist):
        if checked >= args.max_words:
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
        node[None] = True
        frequencies[needle] = (word, z)
        checked += 1

    hits: list[tuple[int, float, str, int]] = []
    n = len(data)
    for i in range(n):
        node = root
        j = i
        while j < n and data[j] in node:
            node = node[data[j]]  # type: ignore[index]
            j += 1
            if None in node:
                needle = data[i:j]
                word, z = frequencies[needle]
                hits.append((len(needle), z, word, i))

    hits.sort(key=lambda x: (-x[0], -x[1], x[3]))
    print(f"Patterns checked: {checked}")
    print(f"Words with hits:  {len(hits)}")
    for length, z, word, pos in hits[:50]:
        print(f"{word!r:24} bytes={length:3} zipf={z:5.2f} first_offset={pos}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Post-hoc language detector backed by wordfreq.

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

    checked = 0
    hits = []
    for word in iter_wordlist(args.lang, wordlist=args.wordlist):
        if checked >= args.max_words:
            break
        if len(word) < args.min_length or zipf_frequency(word, args.lang) < args.min_zipf:
            continue
        checked += 1
        needle = word.encode("utf-8")
        pos = data.find(needle)
        if pos >= 0:
            hits.append((len(needle), zipf_frequency(word, args.lang), word, pos))

    hits.sort(key=lambda x: (-x[0], -x[1], x[3]))
    print(f"Patterns checked: {checked}")
    print(f"Words with hits:  {len(hits)}")
    for length, z, word, pos in hits[:50]:
        print(f"{word!r:24} bytes={length:3} zipf={z:5.2f} first_offset={pos}")


if __name__ == "__main__":
    main()

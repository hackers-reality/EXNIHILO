#!/usr/bin/env python3
"""Find the longest exact wordfreq matches in a frozen random-byte dataset."""
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
    p.add_argument("--min-zipf", type=float, default=0.0)
    p.add_argument("--top", type=int, default=50)
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
        if needle:
            candidates.setdefault(needle, (word, z))

    # Trie: one scan of the data, sharing prefixes between candidate words.
    root: dict[int | None, dict] = {}
    for needle in candidates:
        node = root
        for b in needle:
            node = node.setdefault(b, {})
        node[None] = True

    hits: list[tuple[int, int, str, float]] = []
    n = len(data)
    for i in range(n):
        node = root
        j = i
        while j < n and data[j] in node:
            node = node[data[j]]
            j += 1
            if None in node:
                needle = data[i:j]
                word, z = candidates[needle]
                hits.append((len(needle), i, word, z))

    hits.sort(key=lambda x: (-x[0], x[1]))
    print(f"Candidates:     {len(candidates)}")
    print(f"Total hits:     {len(hits)}")
    print("\nlength chars bytes offset     zipf word")
    for byte_len, offset, word, z in hits[:args.top]:
        print(f"{len(word):6} {len(word):5} {byte_len:5} {offset:8} {z:8.2f} {word!r}")

    if hits:
        max_len = hits[0][0]
        longest = [h for h in hits if h[0] == max_len]
        print(f"\nLongest byte length: {max_len}")
        print(f"Longest hits:       {len(longest)}")
    else:
        print("\nNo matches found.")


if __name__ == "__main__":
    main()

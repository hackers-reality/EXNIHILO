#!/usr/bin/env python3
"""Rank long recognizable sequences in already-generated EXNIHILO output.

This module is analysis-only. It never supplies information back to the
random generator.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

TOKEN_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+)?")


def load_words(path: str) -> set[str]:
    words: set[str] = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        word = line.strip().lower()
        if word.isalpha():
            words.add(word)
    return words


def rank_sequences(text: str, vocabulary: set[str], minimum: int = 2) -> list[tuple[int, int, str]]:
    tokens = TOKEN_RE.findall(text.lower())
    hits: list[tuple[int, int, str]] = []
    start = None

    for i, token in enumerate(tokens + ["__END__"]):
        if token in vocabulary:
            if start is None:
                start = i
        elif start is not None:
            length = i - start
            if length >= minimum:
                sequence = " ".join(tokens[start:i])
                hits.append((length, start, sequence))
            start = None

    hits.sort(key=lambda item: (-item[0], item[1]))
    return hits


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank recognizable word runs in EXNIHILO output")
    parser.add_argument("input")
    parser.add_argument("--dictionary", required=True)
    parser.add_argument("--minimum", type=int, default=2)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8", errors="replace")
    vocabulary = load_words(args.dictionary)
    results = rank_sequences(text, vocabulary, max(1, args.minimum))

    print(f"candidate sequences: {len(results):,}")
    for rank, (length, position, sequence) in enumerate(results[: args.top], 1):
        print(f"{rank:>3}. length={length:<4} token={position:<10} {sequence}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""EXNIHILO independent detector.

This detector is deliberately separate from the generator. It does not feed
any information back into EXNIHILO's random generation process.

It uses a user-supplied word list only for analysis of already-generated text.
"""

import argparse
import re
from pathlib import Path

TOKEN_RE = re.compile(r"[a-zA-Z]+(?:'[a-zA-Z]+)?")


def load_words(path):
    words = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        word = line.strip().lower()
        if word and word.isalpha():
            words.add(word)
    return words


def detect(text, vocabulary):
    tokens = TOKEN_RE.findall(text.lower())
    hits = [(i, token) for i, token in enumerate(tokens) if token in vocabulary]
    runs = []
    current = []
    for i, token in enumerate(tokens):
        if token in vocabulary:
            current.append((i, token))
        else:
            if current:
                runs.append(current)
                current = []
    if current:
        runs.append(current)
    longest = max(runs, key=len, default=[])
    return tokens, hits, longest


def main():
    parser = argparse.ArgumentParser(description="Detect English-like words in existing EXNIHILO output")
    parser.add_argument("input", help="generated text file")
    parser.add_argument("--dictionary", required=True, help="plain newline-separated word list")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8", errors="replace")
    vocabulary = load_words(args.dictionary)
    tokens, hits, longest = detect(text, vocabulary)

    print(f"tokens: {len(tokens):,}")
    print(f"recognized words: {len(hits):,}")
    print(f"recognized-word rate: {len(hits) / len(tokens):.8f}" if tokens else "recognized-word rate: 0")
    if longest:
        print(f"longest consecutive recognized run: {len(longest)} words")
        print("sequence: " + " ".join(word for _, word in longest))
    else:
        print("longest consecutive recognized run: 0 words")


if __name__ == "__main__":
    main()

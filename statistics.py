#!/usr/bin/env python3
"""Statistical analysis for EXNIHILO detector output.

The generator is never consulted here. This module evaluates observed hits
against a simple null model: independent uniform lowercase characters with
uniform random token lengths.
"""

import argparse
import math
from pathlib import Path

ALPHABET = 26
MIN_LENGTH = 1
MAX_LENGTH = 35


def word_probability(word: str) -> float:
    """Probability of an exact lowercase word under EXNIHILO's letter model."""
    n = len(word)
    if not 1 <= n <= MAX_LENGTH or not word.isalpha() or not word.islower():
        return 0.0
    # Length is uniform over 1..35; every character is uniform over 26 letters.
    return (1.0 / MAX_LENGTH) * (1.0 / ALPHABET) ** n


def poisson_tail(lam: float, observed: int) -> float:
    """P(X >= observed) for a Poisson(lambda), computed stably enough for counts."""
    if observed <= 0:
        return 1.0
    if lam <= 0:
        return 0.0
    # P(X >= k) = 1 - P(X <= k-1). For very large lambda this direct sum
    # can be expensive, so use a recurrence only up to the observed count.
    term = math.exp(-lam)
    cumulative = term
    for i in range(1, observed):
        term *= lam / i
        cumulative += term
        if term == 0:
            break
    return max(0.0, min(1.0, 1.0 - cumulative))


def expected_exact_word_occurrences(word: str, token_count: int) -> float:
    return token_count * word_probability(word)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an observed EXNIHILO word hit")
    parser.add_argument("word")
    parser.add_argument("--tokens", type=int, required=True)
    parser.add_argument("--observed", type=int, default=1)
    args = parser.parse_args()
    if args.tokens < 0 or args.observed < 0:
        parser.error("--tokens and --observed must be non-negative")
    word = args.word.lower()
    p = word_probability(word)
    expected = expected_exact_word_occurrences(word, args.tokens)
    tail = poisson_tail(expected, args.observed)
    print(f"word: {word}")
    print(f"token_count: {args.tokens:,}")
    print(f"single-token probability: {p:.6e}")
    print(f"expected occurrences: {expected:.6e}")
    print(f"observed occurrences: {args.observed:,}")
    print(f"poisson upper-tail estimate: {tail:.6e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""EXNIHILO controlled random-text experiments.

Three deliberately simple null controls:
A: IID letters only.
B: IID letters plus uniformly random spaces.
C: random word boundaries with 1-35 letter tokens.

No English vocabulary, corpus, grammar, or detector is used here.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

from exnihilo import random_byte_stream

ALPHABET = b"abcdefghijklmnopqrstuvwxyz"


def uniform_index(source, n):
    if not 1 <= n <= 256:
        raise ValueError("n must be in 1..256")
    limit = 256 - (256 % n)
    while True:
        value = next(source)
        if value < limit:
            return value % n


def random_letters(source, count):
    return bytes(ALPHABET[uniform_index(source, 26)] for _ in range(count)).decode()


def mode_a(source, count):
    return random_letters(source, count)


def mode_b(source, count):
    out = []
    for _ in range(count):
        if uniform_index(source, 8) == 0:
            out.append(" ")
        else:
            out.append(chr(ALPHABET[uniform_index(source, 26)]))
    return "".join(out)


def mode_c(source, words):
    out = []
    for _ in range(words):
        length = 1 + uniform_index(source, 35)
        out.append(random_letters(source, length))
    return " ".join(out)


def run(mode, samples, size, output):
    source = random_byte_stream()
    started = time.perf_counter()
    digest = hashlib.sha256()
    total = 0
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for _ in range(samples):
            if mode == "a":
                text = mode_a(source, size)
            elif mode == "b":
                text = mode_b(source, size)
            else:
                text = mode_c(source, size)
            handle.write(text + "\n")
            digest.update((text + "\n").encode())
            total += len(text)
    elapsed = time.perf_counter() - started
    report = {
        "mode": mode,
        "samples": samples,
        "requested_size": size,
        "characters": total,
        "elapsed_seconds": elapsed,
        "characters_per_second": total / elapsed if elapsed else None,
        "sha256": digest.hexdigest(),
        "english_knowledge_in_generator": False,
    }
    output.with_suffix(output.suffix + ".json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["a", "b", "c"])
    parser.add_argument("--samples", type=int, default=10000)
    parser.add_argument("--size", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("results/control.txt"))
    args = parser.parse_args()
    if args.samples < 1 or args.size < 1:
        parser.error("samples and size must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    run(args.mode, args.samples, args.size, args.output)


if __name__ == "__main__":
    main()

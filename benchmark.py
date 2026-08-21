#!/usr/bin/env python3
"""High-throughput EXNIHILO benchmark.

Measures generation without printing every result. The generator remains
completely vocabulary-free; this file only measures throughput.
"""

import argparse
import time

from exnihilo import generate_sentence, random_byte_stream


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark EXNIHILO generation")
    parser.add_argument("--seconds", type=float, default=10.0)
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error("--seconds must be > 0")

    source = random_byte_stream()
    sentences = 0
    characters = 0
    started = time.perf_counter()
    deadline = started + args.seconds

    while time.perf_counter() < deadline:
        text = generate_sentence(source)
        sentences += 1
        characters += len(text)

    elapsed = time.perf_counter() - started
    print(f"seconds={elapsed:.6f}")
    print(f"sentences={sentences}")
    print(f"characters={characters}")
    print(f"sentences_per_second={sentences / elapsed:.2f}")
    print(f"characters_per_second={characters / elapsed:.2f}")


if __name__ == "__main__":
    main()

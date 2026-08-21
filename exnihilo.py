#!/usr/bin/env python3
"""EXNIHILO: generate text from OS-provided random bytes.

The generator has no vocabulary, language model, grammar, or English input.
Random bytes come from the operating system via os.urandom().
"""

import argparse
import os
import string
import sys
import time

LETTERS = string.ascii_lowercase
ALPHABET_SIZE = len(LETTERS)


def uniform_index(byte_stream, upper):
    """Return a uniform integer in [0, upper) using rejection sampling."""
    limit = 256 - (256 % upper)
    while True:
        b = next(byte_stream)
        if b < limit:
            return b % upper


def random_byte_stream(chunk_size=65536):
    """Yield bytes supplied by the OS randomness source."""
    while True:
        for b in os.urandom(chunk_size):
            yield b


def random_word(byte_stream):
    length = uniform_index(byte_stream, 35) + 1
    return ''.join(LETTERS[uniform_index(byte_stream, ALPHABET_SIZE)] for _ in range(length))


def generate_sentence(byte_stream):
    # 1..20 words; no linguistic constraints are used.
    count = uniform_index(byte_stream, 20) + 1
    words = [random_word(byte_stream) for _ in range(count)]
    return ' '.join(words) + ('.' if uniform_index(byte_stream, 4) == 0 else '')


def main():
    parser = argparse.ArgumentParser(description='EXNIHILO — language from randomness')
    parser.add_argument('--sentences', type=int, default=0, help='generate this many sentences; 0 means continuous')
    parser.add_argument('--benchmark', type=float, default=0, help='run for N seconds and report throughput')
    args = parser.parse_args()

    source = random_byte_stream()
    generated = 0
    started = time.perf_counter()
    deadline = started + args.benchmark if args.benchmark > 0 else None

    try:
        if args.sentences > 0:
            for _ in range(args.sentences):
                text = generate_sentence(source)
                generated += 1
                print(text, flush=True)
            return

        while deadline is None or time.perf_counter() < deadline:
            print(generate_sentence(source), flush=True)
            generated += 1
    except KeyboardInterrupt:
        pass
    finally:
        elapsed = time.perf_counter() - started
        if elapsed > 0:
            print(f'\nEXNIHILO: {generated:,} sentences in {elapsed:.3f}s ({generated / elapsed:,.1f}/s)', file=sys.stderr)


if __name__ == '__main__':
    main()

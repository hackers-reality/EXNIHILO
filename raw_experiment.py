#!/usr/bin/env python3
"""EXNIHILO raw-byte experiment runner.

Generates a binary dataset from the operating system CSPRNG. The generator
contains no alphabet, vocabulary, dictionary, grammar, or language model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from pathlib import Path


def generate(path: Path, size: int, chunk_size: int) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    written = 0
    started = time.perf_counter()

    with path.open("wb") as out:
        while written < size:
            n = min(chunk_size, size - written)
            block = os.urandom(n)
            out.write(block)
            digest.update(block)
            written += n

    elapsed = time.perf_counter() - started
    return {
        "bytes": written,
        "seconds": elapsed,
        "bytes_per_second": written / elapsed if elapsed else None,
        "sha256": digest.hexdigest(),
        "entropy_source": "os.urandom",
        "platform": platform.platform(),
        "python": platform.python_version(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a raw EXNIHILO byte dataset")
    parser.add_argument("--bytes", type=int, default=1_000_000,
                        help="number of random bytes to generate")
    parser.add_argument("--chunk", type=int, default=1_048_576,
                        help="write size per chunk")
    parser.add_argument("--output", type=Path, default=Path("runs/raw.bin"))
    args = parser.parse_args()

    if args.bytes < 1 or args.chunk < 1:
        parser.error("--bytes and --chunk must be positive")

    result = generate(args.output, args.bytes, args.chunk)
    metadata = args.output.with_suffix(args.output.suffix + ".json")
    metadata.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

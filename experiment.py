#!/usr/bin/env python3
"""EXNIHILO experiment runner.

Runs the generator without modifying its randomness, writes raw output to a
log, and records reproducibility metadata. No English knowledge is used here.
"""

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

from exnihilo import generate_sentence, random_byte_stream


def run(sentences: int, output: Path) -> None:
    source = random_byte_stream()
    started = time.perf_counter()
    count = 0
    chars = 0
    digest = hashlib.sha256()

    with output.open("w", encoding="utf-8", newline="\n") as handle:
        while count < sentences:
            text = generate_sentence(source)
            handle.write(text + "\n")
            encoded = (text + "\n").encode("utf-8")
            digest.update(encoded)
            chars += len(text)
            count += 1

    elapsed = time.perf_counter() - started
    metadata = {
        "sentences": count,
        "characters": chars,
        "elapsed_seconds": elapsed,
        "sentences_per_second": count / elapsed if elapsed else None,
        "sha256": digest.hexdigest(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "entropy_source": "os.urandom",
    }

    metadata_path = output.with_suffix(output.suffix + ".json")
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="EXNIHILO reproducible experiment runner")
    parser.add_argument("--sentences", type=int, default=10000)
    parser.add_argument("--output", type=Path, default=Path("results/run.txt"))
    args = parser.parse_args()
    if args.sentences < 1:
        parser.error("--sentences must be >= 1")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    run(args.sentences, args.output)


if __name__ == "__main__":
    main()

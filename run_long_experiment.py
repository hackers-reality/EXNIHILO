#!/usr/bin/env python3
"""EXNIHILO long-run experiment driver.

Generates large batches without printing every sentence. The generator remains
vocabulary-free; analysis is performed only after bytes have been generated.
"""

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

from exnihilo import generate_sentence, random_byte_stream


def run(sentences: int, output: Path, report: Path) -> None:
    source = random_byte_stream()
    digest = hashlib.sha256()
    started = time.perf_counter()
    chars = 0

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        for _ in range(sentences):
            line = (generate_sentence(source) + "\n").encode("ascii")
            handle.write(line)
            digest.update(line)
            chars += len(line) - 1

    elapsed = time.perf_counter() - started
    result = {
        "sentences": sentences,
        "characters": chars,
        "elapsed_seconds": elapsed,
        "sentences_per_second": sentences / elapsed if elapsed else None,
        "characters_per_second": chars / elapsed if elapsed else None,
        "sha256": digest.hexdigest(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "generator": "exnihilo.py",
        "entropy_source": "os.urandom",
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sentences", type=int, default=1_000_000)
    p.add_argument("--output", type=Path, default=Path("results/long_run.txt"))
    p.add_argument("--report", type=Path, default=Path("results/long_run.json"))
    args = p.parse_args()
    if args.sentences < 1:
        p.error("--sentences must be >= 1")
    run(args.sentences, args.output, args.report)


if __name__ == "__main__":
    main()

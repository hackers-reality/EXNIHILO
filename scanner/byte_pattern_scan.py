#!/usr/bin/env python3
"""Post-hoc byte-pattern scanner for EXNIHILO datasets.

The generator never imports this module and never receives its dictionaries.
A detector may search a raw byte stream for UTF-8 encodings of words supplied
by the user/researcher. This keeps language knowledge downstream of generation.

Usage:
    python scanner/byte_pattern_scan.py dataset.bin words.txt --encoding utf-8

words.txt: one candidate word/phrase per line. Blank lines and lines beginning
with '#' are ignored.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def load_patterns(path: Path, encoding: str) -> list[tuple[str, bytes]]:
    patterns: list[tuple[str, bytes]] = []
    for raw in path.read_text(encoding=encoding).splitlines():
        text = raw.strip()
        if not text or text.startswith("#"):
            continue
        patterns.append((text, text.encode(encoding)))
    return patterns


def scan(data: bytes, patterns: list[tuple[str, bytes]]) -> list[dict]:
    hits: list[dict] = []
    for label, pattern in patterns:
        start = 0
        while True:
            pos = data.find(pattern, start)
            if pos < 0:
                break
            hits.append({
                "text": label,
                "byte_offset": pos,
                "byte_length": len(pattern),
            })
            start = pos + 1
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan raw EXNIHILO bytes for post-hoc language patterns.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("wordlist", type=Path)
    parser.add_argument("--encoding", default="utf-8")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    data = args.dataset.read_bytes()
    patterns = load_patterns(args.wordlist, args.encoding)
    hits = scan(data, patterns)

    import json
    result = {
        "dataset": str(args.dataset),
        "dataset_bytes": len(data),
        "dataset_sha256": hashlib.sha256(data).hexdigest(),
        "detector_encoding": args.encoding,
        "candidate_patterns": len(patterns),
        "hits": hits,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Dataset bytes: {len(data):,}")
        print(f"SHA-256:       {result['dataset_sha256']}")
        print(f"Patterns:      {len(patterns):,}")
        print(f"Hits:          {len(hits):,}")
        for hit in sorted(hits, key=lambda h: (-h["byte_length"], h["byte_offset"]))[:50]:
            print(f"{hit['text']!r}\tbyte={hit['byte_offset']}\tbytes={hit['byte_length']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

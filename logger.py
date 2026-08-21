#!/usr/bin/env python3
"""Raw experiment logger for EXNIHILO.

The logger records generated output without modifying the generator's
randomness or feeding detector results back into it.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Record EXNIHILO output with experiment metadata")
    parser.add_argument("input", help="raw generated text file")
    parser.add_argument("--output", default="experiment.json", help="metadata JSON path")
    parser.add_argument("--entropy", default="OS entropy via os.urandom", help="declared entropy source")
    parser.add_argument("--generator-version", default="unknown")
    args = parser.parse_args()

    source = Path(args.input)
    data = source.read_bytes()
    metadata = {
        "experiment_started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_file": str(source),
        "bytes_recorded": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "entropy_source": args.entropy,
        "generator_version": args.generator_version,
        "detector_feedback": False,
    }
    Path(args.output).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()

# EXNIHILO Long-Run Experiment Protocol

## Purpose

Measure how often recognizable English-like strings occur when text is generated from OS-provided random bytes with no English vocabulary, corpus, grammar, language model, or feedback loop.

## Rules

1. The generator must not read an English dictionary or corpus.
2. The detector is downstream-only and cannot influence generation.
3. Every run records its parameters, environment, output hash, and counts.
4. Raw output is preserved for any claimed unusual hit.
5. A single recognizable word is not evidence of language emergence.
6. Longer consecutive sequences are evaluated against the generator's null probability.
7. Do not discard non-interesting runs.

## Suggested stages

- 1,000,000 sentences: smoke test
- 10,000,000 sentences: baseline
- 100,000,000 sentences: long run
- 1,000,000,000 sentences: only after storage and throughput have been validated

## Important statistical note

Because many candidate words and phrases are searched, the experiment must account for multiple comparisons. A rare-looking hit is not automatically statistically significant merely because its individual probability is small.

## Reproducibility

Each run should preserve:

- exact generator revision
- entropy source
- sentence count
- character count
- runtime
- output SHA-256
- machine/platform information
- detector version and dictionary version, if detection is performed

The detector must be run as a separate analysis step after generation.

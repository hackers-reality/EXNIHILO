# EXNIHILO Experimental Runbook

## Purpose

Measure how often recognizable English-like sequences occur when the generator has no English vocabulary, corpus, grammar, or language model.

## Rules

1. The generator must remain independent of all detectors and dictionaries.
2. Analysis dictionaries are applied only after generation.
3. Preserve the complete raw output for every reported result.
4. Record the generator version, mode, entropy source, byte/character counts, duration, and SHA-256 digest.
5. Do not cherry-pick only interesting runs. Report the complete planned run set.
6. A recognizable word is an observation, not a prediction.
7. A long phrase must be compared with its expected probability under the exact null model.
8. If multiple phrases are searched, account for the number of opportunities searched.

## Recommended first run

Start with small reproducibility tests, then benchmark. Only after those pass should long runs be attempted.

Example:

```text
python exnihilo.py
python benchmark.py
python run_long_experiment.py --help
```

For large experiments, write output to a dedicated results directory and keep the generated data immutable after the run.

## What counts as interesting

Prefer metrics that were specified before looking at the output:

- longest consecutive recognized-word run
- frequency of exact target phrases selected before the run
- distribution of recognized-word run lengths
- observed versus null-model expectation

Do not redefine the target after seeing a surprising string.

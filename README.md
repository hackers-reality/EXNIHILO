# EXNIHILO

> **Out of nothing.**
>
> Exploring whether recognizable language can appear in completely unguided random byte streams.

## Principle

EXNIHILO deliberately gives the **generator** no English vocabulary, grammar, corpus, language model, Markov model, or predefined words.

The generator obtains random bytes from the operating system and maps those bytes to random lowercase characters. Word lengths and sentence lengths are also selected from the same random source.

Python's `os.urandom()` provides random bytes from an OS-specific randomness source and is intended to provide unpredictable bytes suitable for cryptographic use. On Windows, Python documents that it uses `BCryptGenRandom()`.

The English detector remains a separate component. It must never influence generation.

## First prototype

Run:

```bash
python exnihilo.py --sentences 20
```

Continuous generation:

```bash
python exnihilo.py
```

Benchmark for 10 seconds:

```bash
python exnihilo.py --benchmark 10
```

## Experimental record

The first raw-data experiments were performed on Android 16 / aarch64 using Python 3.13.13 and `os.urandom()`.

### Dataset 001

A 10,000,000-byte raw random dataset was generated and recorded with SHA-256:

```text
93371df4d2782961822a9076b9f81d23407e3edb2f56c5719c759db2bc55011d
```

A basic scan against a small English word list found:

```text
'a'   hits=38987
'an'  hits=161
```

but found no hits for `the`, `hello`, `world`, `king`, `queen`, `computer`, `random`, or `exnihilo`.

### Dataset 002

A 100,000,000-byte raw random dataset was generated and preserved as the second experimental dataset.

```text
SHA-256: 94d0702f25fa6a78cb040ba2efdce6fdec8d34fdbe152d7cdf19fc8e23589026
```

Generation benchmark:

```text
bytes:            100,000,000
seconds:          0.4029976159799844
bytes_per_second: 248140425.7363316
entropy_source:   os.urandom
platform:         Android-16-aarch64-64bit-ELF
python:           3.13.13
```

A small English `wordfreq` list contained 28,216 candidates. At first, 1,675 words had at least one hit in the 100 MB dataset. The longest hits were initially only 4 bytes.

Using a larger 200,000-entry `wordfreq` candidate set changed the picture: four 5-byte matches were found:

```text
'lakas'
'natin'
'wimer'
"hop's"
```

Context inspection showed each was isolated inside otherwise random-looking bytes. They were not evidence of a sentence or coherent message.

### De-overlapping and clustering

The first cluster detector counted overlapping substrings of the same word as separate hits. For example, `lakas` produced `lak`, `laka`, `lakas`, `aka`, `akas`, and `kas`. This was identified as a detector artifact and the clustering method was corrected to retain the longest non-overlapping match at a location.

With the corrected detector and a 200,000-entry candidate set:

| Minimum word length | Non-overlap hits | Independent clusters | Gap |
|---:|---:|---:|---:|
| 4 | 437 | 0 | 16 bytes |
| 5 | 4 | 0 | 16 bytes |
| 6 | 0 | 0 | 16 bytes |

Thus, Dataset 002 produced **no independent nearby word pairs** under these exact detector settings.

### Initial null-model experiment

A Monte Carlo null-model tool was also run using 1,000 independently generated 1 MB random windows with the same 200,000-entry English candidate set, minimum word length 5, 16-byte gap, and two-hit cluster requirement.

Result:

```text
Observed clusters:  0
Null trials:        1,000
Null mean:          0
Null maximum:       0
Null zero fraction: 1
```

This is **not** a final significance test for Dataset 002 because the real dataset is 100 MB while each null window was 1 MB. The result only establishes that the chosen cluster statistic was absent from all 1 MB null trials. A properly size-matched null model or an analytically justified expectation is still required.

## What the experiments show so far

Random bytes readily contain short recognizable fragments when enough positions are searched. Increasing the minimum word length sharply reduces accidental matches. In the current 100 MB dataset, no two independent 4+ byte dictionary matches occurred within 16 bytes under the tested lexicon and detector rules.

These observations **do not demonstrate that random bytes cannot produce meaningful language**. They only describe the observed results under specific dataset sizes, lexicons, encodings, and detection rules.

The project therefore treats every apparent discovery as a statistical question rather than as evidence of intelligence, prediction, or supernatural structure.

## Scientific rule

A surprising output is **not** evidence of prediction or anything supernatural by itself. Every notable result must preserve the raw output, generation count, entropy source, program version, dataset hash, and detection method so that its probability can be analyzed.

## Analysis tools

The repository now includes tools for:

- raw byte generation and hashing
- exact byte-pattern scanning
- sequence statistics
- word-frequency detection
- word-length statistics
- longest word-hit inspection
- local context inspection
- non-overlapping word clustering
- Monte Carlo null-model experiments

The detector must remain independent of the generator.

## Roadmap

- [x] OS entropy source
- [x] No-vocabulary character generation
- [x] 1–35 character random words
- [x] Random sentence generation
- [x] Benchmark mode
- [x] Raw output logging
- [x] Independent English-word detector
- [x] Local context inspection
- [x] Non-overlapping word clustering
- [x] Initial null-model experiment
- [ ] Size-matched statistical null model
- [ ] Phrase/sentence detector
- [ ] Statistical significance analysis
- [ ] Reproducible experiment reports
- [ ] Optional hardware-RNG experiment

## License

MIT

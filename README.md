# EXNIHILO

> **Out of nothing.**
>
> Exploring whether recognizable language can appear in completely unguided random character streams.

## Principle

EXNIHILO deliberately gives the generator **no English vocabulary, grammar, corpus, language model, Markov model, or predefined words**.

The generator obtains random bytes from the operating system and maps those bytes to random lowercase characters. Word lengths and sentence lengths are also selected from the same random source.

Python's `os.urandom()` provides random bytes from an OS-specific randomness source and is intended to provide unpredictable bytes suitable for cryptographic use. On Windows, Python documents that it uses `BCryptGenRandom()`. citeturn0search0

The English detector will remain a separate component. It must never influence generation.

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

## Scientific rule

A surprising output is **not** evidence of prediction or anything supernatural by itself. Every notable result must preserve the raw output, generation count, entropy source, program version, and detection method so that its probability can be analyzed.

## Roadmap

- [x] OS entropy source
- [x] No-vocabulary character generation
- [x] 1–35 character random words
- [x] Random sentence generation
- [x] Benchmark mode
- [ ] Raw output logging
- [ ] Independent English-word detector
- [ ] Phrase/sentence detector
- [ ] Statistical significance analysis
- [ ] Reproducible experiment reports
- [ ] Optional hardware-RNG experiment

## License

MIT

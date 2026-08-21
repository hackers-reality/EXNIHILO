# EXNIHILO

> **From nothing.**
>
> An experimental study of whether recognizable structure can emerge from raw randomness.

## The idea

EXNIHILO deliberately gives the generator **no English vocabulary, grammar, language model, training corpus, or predefined words**.

The generation pipeline is:

```text
entropy → bits → characters → random strings → random sentences
```

The generator does not know what an English word or sentence is.

A separate analysis layer may inspect generated output after the fact and report whether recognizable English occurs. The analysis layer must never influence generation.

## Goals

- Generate character sequences from raw entropy.
- Allow lengths from 1 to 35 characters per token.
- Assemble tokens into random sentences.
- Record generation counts and throughput.
- Detect and preserve interesting accidental patterns.
- Keep generation and analysis completely separated.

## Scientific rule

**No feedback.** If the detector finds English, the generator must not be changed because of that result. This keeps the experiment reproducible and avoids silently biasing the output.

## Status

🚧 Initial experiment — implementation coming next.

## Name

**EXNIHILO** comes from the Latin phrase *ex nihilo*, meaning **"out of nothing."**

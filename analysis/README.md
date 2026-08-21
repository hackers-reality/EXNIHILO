# EXNIHILO Analysis

This directory contains analysis-only tooling and experiment notes.

## Principle

The generator is blind to English. Analysis may inspect generated output, but analysis must never feed detected words, phrases, scores, or any other information back into the generator.

## Interpretation

A recognizable word is not, by itself, evidence of anything extraordinary. Shannon's classic random-text experiments demonstrated that uniformly random letters produce noise, while progressively adding statistical structure produces increasingly English-like output. EXNIHILO deliberately starts from the unconstrained/random side of that comparison.

Results must therefore report:

- total characters generated
- total tokens/sentences generated
- exact generator configuration
- entropy source
- observed English matches
- expected matches under the null model
- longest consecutive recognized sequence
- exact raw output and integrity hash

Never cherry-pick an interesting phrase without reporting the total search space examined.

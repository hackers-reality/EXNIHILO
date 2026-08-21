# Null Model

For the baseline experiment, characters are sampled independently and uniformly from a defined alphabet. The generator's alphabet and boundary rules are parameters of the experiment, not learned from English.

For an exact fixed string of length `n` over an alphabet of size `A`, the probability of that exact string is:

`P = A^(-n)`

For example, if the alphabet is 26 lowercase letters, one particular 10-character string has probability `1 / 26^10` on one trial.

For dictionary-based detection, the probability of an English hit depends on the exact dictionary and token-length distribution. Therefore the detector must record the dictionary identity/hash and the generator configuration. Expected rates should be estimated analytically where possible and validated with independent null simulations where practical.

A large number of trials creates a multiple-comparisons problem: searching billions of outputs for the most interesting phrase guarantees that some outputs will look interesting by chance. The total search volume must always be reported alongside any selected result.

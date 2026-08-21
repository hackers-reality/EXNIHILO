# EXNIHILO Result Schema

Every controlled run should record the generator configuration separately from any linguistic analysis.

Required fields:

- `mode`: `a`, `b`, or `c`
- `samples`
- `requested_size`
- `characters`
- `elapsed_seconds`
- `characters_per_second`
- `sha256`
- `english_knowledge_in_generator`: must remain `false`

## Interpretation rule

A detected English word or phrase is an observation, not evidence of prediction. Significance must be evaluated against the exact null model and the total amount of text searched.

Do not cherry-pick runs after seeing their output. Preserve failed, boring, and interesting runs alike.

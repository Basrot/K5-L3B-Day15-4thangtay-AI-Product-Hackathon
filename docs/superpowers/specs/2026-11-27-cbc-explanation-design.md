# CBC explanation response design

## Intent

Make explanations answer the user's question about what a CBC index measures, while keeping the comparison factual and short for pregnant users.

## Goals

- Add a plain-language definition for each of the eight supported indices.
- Keep the measured value, normalized unit, trimester range, and status from deterministic comparison logic.
- Keep study limitations and citations in response metadata so a client can render them once, rather than duplicating them in prose.
- Avoid diagnosing or suggesting treatment.

## Non-goals

- Rewriting image OCR, speech recognition, voice synthesis, or clinical thresholds.
- Generating unrestricted medical explanations with the language model.

## Approaches

- Let the LLM write the whole explanation: flexible, but risks invented clinical claims and inconsistent ranges.
- Use deterministic definitions plus the existing deterministic comparison: selected because it answers the question while keeping all patient-specific facts anchored to validated data.
- Add a retrieval/education knowledge base: unnecessary for eight short definitions and adds deployment work.

## Behavior

For a supported index, the answer states what it measures, then the entered value and its status against the selected source and trimester. It ends with one short reminder that the interval is for comparison and a clinician considers the wider context. The source URL and detailed scope note remain structured metadata and are not duplicated in `output`. Summary output follows the same rule.

Definitions follow MedlinePlus descriptions of CBC components and red-cell indices. Research interval metadata continues to cite Pham et al. (2023). The application does not infer a diagnosis from an out-of-range flag.

## Acceptance

- Asking what RBC means explains that RBC is a red-cell count and that red cells contain hemoglobin which carries oxygen.
- All eight supported codes have a non-empty explanation.
- `output` does not contain `reference_note`; the structured `reference_note` and sources remain available.
- Existing comparison values, units, ranges, and flags do not change.

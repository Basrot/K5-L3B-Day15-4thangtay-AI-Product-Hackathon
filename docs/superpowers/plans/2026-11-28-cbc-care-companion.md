# CBC Care Companion implementation plan

**Goal:** Make the current pregnant-user CBC prototype useful beyond a range lookup by providing grounded multi-indicator explanations, meaningful longitudinal context, and a clinician-ready visit brief.

**Design:** `docs/superpowers/specs/2026-11-28-cbc-care-companion-design.md`

**Architecture:** Keep FastAPI/SQLite and the Next.js page. Use only confirmed report data. Keep the approved controlled-response approach: an LLM classifies/recognizes the question, while validated deterministic logic formats findings, caveats, and source links. No diagnosis, treatment, or public health-data share links.

**Verification constraint:** Current session instructions prohibit adding/running tests or builds unless the user asks. Use source review, Python syntax parse, `git diff --check`, and review the plan checklist; do not claim tests/builds passed.

## Tasks

### 1. Make evidence-grounded CBC explanations meaningful

- [x] Route natural questions about one or multiple analytes from confirmed rows; handle common Vietnamese phrasings.
- [x] Produce concise group context with exact values/statuses, what a clinician may consider, what CBC cannot establish, and relevant linked sources.
- [x] Preserve medical-advice/urgent guards and fake-model transparency.

### 2. Explain longitudinal comparisons

- [x] Summarize only comparable values and status changes for the selected pair of confirmed reports.
- [x] State when reference context differs; never call a numerical increase/decrease clinical improvement or deterioration.
- [x] Let the user create a doctor-question draft from the grounded change summary. Assistant interpretation remains scoped to the current confirmed report; it does not claim to assess a two-report clinical trend.

### 3. Create a clinician-ready visit brief

- [x] Build a client-side print view from the confirmed report: gestational age/date when present, selected reference/source, key values/statuses, multi-row explanation, questions, and limitations.
- [x] Add an explicit print/download action; no third-party share link or new persistence.
- [x] Retain text download as a fallback and include the same confirmed context.

### 4. Make the main page guide the user to these outcomes

- [x] Put the grouped explanation, cited assistant answer, trend summary, and visit brief in a clear hierarchy.
- [x] Ensure OCR/unconfirmed values never enter AI explanations or visit brief.
- [x] Clarify that assistant content is educational and not clinician-reviewed diagnosis.

### 5. Static review

- [x] Inspect patient paths, missing dates/gestational age, unavailable rows, within-range-only reports, and fake-model mode.
- [x] Review source attribution and ensure no calculations/reference/API ownership changes.
- [x] Run `git diff --check`. Python is unavailable in this workspace; no tests/builds under this session instruction.

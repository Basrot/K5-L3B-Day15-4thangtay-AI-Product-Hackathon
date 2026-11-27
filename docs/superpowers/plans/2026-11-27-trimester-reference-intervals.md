# Trimester reference intervals implementation plan

> **For agentic workers:** Use executing-plans to implement and verify each task.

**Goal:** Let adults using the pregnancy demo enter test results and units without typing reference bounds; select published trimester intervals deterministically.

**Architecture:** A versioned Python table copies published 2.5th–97.5th point limits from Pham et al. (2023), Tables 2/3, never computes new clinical limits from private rows. The existing comparison tool selects study or lab mode, converts units and emits provenance. The API, SQLite snapshots, controlled explanations and demo consume the same tool.

**Tech stack:** Python, Decimal, FastAPI, SQLite, Streamlit; existing CPU Docker image.

**Design / constraints:** User requested study intervals by trimester. Study mode is explicit in new frontend requests; when mode is omitted, no bounds means study and any supplied bounds retains the previous lab workflow. No mixing of sources within a report. Study mode always uses server bounds and labels them as research reference intervals, not lab-validated ranges or diagnostic thresholds. Missing result units, adult/pregnancy context and gestational age still require clarification. Keep 28w6d in trimester 2, 29w0d in trimester 3 per shared workbook convention. No private Excel/raw records in git. Work on `codex/trimester-reference-intervals`, push only the branch and open a PR into `Basrot/...:main`; no direct main push or merge.

## Tasks

- [ ] Verify published Tables 2/3, units, coverage and point bounds; document discrepancies against abstract and population/instrument limitations.
- [ ] Write failing tests for study-only result input, day boundaries, units, missing context and conflicting/partial lab data; implement deterministic range resolution in `codebase/tools.py` with a small reference module.
- [ ] Preserve selected mode in `codebase/service.py`; expose optional `reference_mode` and authenticated `/v1/references?gestational_age=...` in FastAPI; test confirmation, reload and chat.
- [ ] Make explanations, source links, report output and Streamlit demo identify selected source and stop requesting study bounds; keep lab mode available explicitly.
- [ ] Update Vercel handoff with minimal payload, reference endpoint and OCR workflow. Test all units/24 rows/old lab cases and Docker API smoke.
- [ ] Review changes, commit and push feature branch, open PR against fork main, verify PR URL/base/head.

## Review focus

Use point estimates, not confidence limits; do not label study bounds as anemia thresholds. Explicit study mode ignores OCR lab limits. Missing mode retains old lab records. Switching mode/age invalidates old session history. Frontend discards late replies from old drafts. Study exclusions and method-specific transference limitations must appear with the result rather than being hidden in documentation alone.

# CBC Quality and Accountability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the CBC app's reliability measurable and its limits, error response, and responsibility boundaries clear without claiming unearned clinical accuracy.

**Architecture:** Preserve the confirmed-report and controlled-answer design. Add a standard-library Node quality report over existing human-scored CSV runs, a separate metric manifest and independent-review template, and a UI disclosure that distinguishes OCR, deterministic comparison, and LLM intent routing.

**Tech Stack:** Node.js built-ins (`node:test`, filesystem), TypeScript/React, Markdown/CSV.

**Spec:** `docs/superpowers/specs/2026-11-28-cbc-quality-and-accountability-design.md`

## Global Constraints

- Do not change the locked 24-case benchmark, previous run outputs, or historical scores.
- Never call a fixed-benchmark pass rate clinical accuracy.
- Do not log or transmit report values, images, identifiers, questions, or answers as feedback.
- Do not present a legal-liability conclusion or use disclaimers to waive responsibility.
- User-facing Vietnamese must clearly distinguish OCR draft, deterministic reference comparison, and LLM routing.

## Review Focus

- Quoted CSV fields with commas/newlines must parse without corrupting benchmark rows.
- Missing, duplicate, unscored, or unknown case IDs must not silently inflate a score.
- A small synthetic benchmark must be labeled as such and must not get a misleading clinical-accuracy or confidence-interval claim.
- A displayed historical score must be tied to its run/model and marked stale relative to current code.
- UI disclosure must not imply clinician review or that user confirmation establishes clinical correctness.

---

### Task 1: Generate transparent benchmark summaries

**Files:**
- Create: `eval/quality-metric-map.csv`
- Create: `eval/quality-report.mjs`
- Create: `eval/quality-report.test.mjs`
- Modify: `eval/README.md`

**Interfaces:**
- `scoreRun(runCsv: string, metricMapCsv: string) -> QualityReport`
- `renderReport(report: QualityReport) -> string`
- CLI: `node eval/quality-report.mjs [run.csv]`; default to `eval/run-1.csv`.

- [x] **Step 1: Write failing tests** for quoted CSV parsing, grouping scored cases, excluding unscored rows from denominators, and rejecting duplicate/unknown IDs.
- [x] **Step 2: Run** `node --test eval/quality-report.test.mjs`; confirmed the expected missing-module failure before implementation.
- [x] **Step 3: Implement** a small CSV reader and summary functions using Node built-ins only; include overall, per-group, technical error, missing, and unscored counts.
- [x] **Step 4: Run** the targeted Node test command and `node eval/quality-report.mjs eval/run-1.csv`; confirmed historical result 19/24 and label “fixed synthetic benchmark pass rate — not clinical accuracy”.
- [x] **Step 5: Document** the command and interpretation in `eval/README.md`; source run CSV remains unchanged.

### Task 2: Prepare independent clinical review records

**Files:**
- Create: `eval/clinical-review-template.csv`
- Create: `docs/quality-and-safety.md`

- [x] **Step 1:** Define separate OCR exact-field, deterministic comparison, explanation correctness, evidence support, critical safety error, disagreement, and user comprehension metrics.
- [x] **Step 2:** Document sampling, held-out split, two independent reviewers, adjudication and release-stop criteria; distinguish synthetic test pass rates from clinical validity.
- [x] **Step 3:** Add a blank review template containing only case ID, build/model/source versions, reviewer role code, rubric scores, and non-identifying notes.
- [x] **Step 4:** Record baseline exactly: 24 synthetic cases; historical Qwen3:4b run 19/24 (79.2%), 0 technical errors; double-review agreement 5/5 on a small subset; current-code rerun, OCR accuracy, and clinical validation are unmeasured.
- [x] **Step 5:** Document role-based safety ownership and state that Vietnamese legal classification/liability requires qualified local review.

### Task 3: Explain reliability and safe error handling in the app

**Files:**
- Modify: `frontend/src/app/page.tsx`

- [x] **Step 1:** Add a user-visible expandable “AI và độ tin cậy” panel beside the assistant.
- [x] **Step 2:** Explain OCR, deterministic comparison, and LLM roles; include historical score/date/model and clearly mark it as synthetic, old, and not clinical accuracy.
- [x] **Step 3:** Explain safe handling when OCR or an explanation seems wrong: do not confirm a wrong draft, edit against the original report, do not use the answer for treatment, and discuss uncertainty with a clinician.
- [x] **Step 4:** State not to submit patient identifiers or report images through informal feedback; no automatic report-data collection added.

### Task 4: Review and publish

**Files:**
- Review all files above and the spec/plan.

- [x] Run `node --test eval/quality-report.test.mjs` and the quality report on the historical run.
- [x] Run `git diff --check`; inspect the final diff and ensure no benchmark/history/secrets changed.
- [x] Record unavailable frontend build/runtime verification: `frontend/node_modules` is absent and no global `tsc` is available, so do not claim the web build passed. Python is also not installed in this environment, so no backend suite was run.
- [x] Commit and push to the user's fork `main` after the user-visible scope and static review; Railway/Vercel were not deployed.

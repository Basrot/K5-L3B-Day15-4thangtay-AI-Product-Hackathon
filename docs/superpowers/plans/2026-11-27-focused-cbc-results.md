# Focused CBC Results Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Help users understand all entered CBC indicators and quickly find values they may want to ask their clinician about.

**Architecture:** Keep result calculations and API response unchanged. Restructure only the result panel in Next.js: a brief overview and any out-of-range rows first, followed by a collapsed full list with plain Vietnamese names and short measurement descriptions. Put methodological detail and sources behind a disclosure.

**Tech Stack:** Next.js, React, TypeScript, Tailwind CSS.

**Spec:** `docs/superpowers/specs/2026-11-27-focused-cbc-results-design.md`

## Global Constraints

- Preserve all values, units, reference intervals, computation, and status classifications.
- Do not call values normal/abnormal or infer diagnoses from status.
- Give each of the 8 CBC analytes a Vietnamese name and one short description of what it measures.
- Preserve download, Q&A, and TTS behavior.

## Review Focus

- Partial reports: summary counts only rows returned by the API, not a hard-coded 8.
- All in-range rows: show a calm summary and keep the note that this does not rule out illness.
- Out-of-range rows: surface only those rows in the initial focus section without implying urgency or diagnosis.
- Both reference modes: retain the applicable reference range and source/method note in the expanded details.
- No results yet: keep the existing empty state unchanged.

---

### Task 1: Restructure the results panel

**Files:**
- Modify: `starter-repo/frontend/src/app/page.tsx`

**Interfaces:**
- Consumes: `analysis.rows`, `analysis.reference_mode`, `analysis.reference_note`, `analysis.reference_source`, existing `ANALYTE_LIST` and `STATUS_META`.
- Produces: concise overview; optional “Nên hỏi bác sĩ” focus section; collapsed “Xem và hiểu đủ chỉ số” details; collapsed method/source notes.

- [x] Derive the total number of returned rows and rows whose existing status is `below` or `above`; do not change status computation.
- [x] Display a short overview with counts. If there are out-of-range rows, surface them with full Vietnamese names, code, value/unit, status, and a non-diagnostic sentence inviting the user to ask their clinician. Otherwise say that all returned rows are in the selected range and that this does not rule out illness.
- [x] Add one short “what this measures” description for every CBC analyte, then show the full results table inside a closed-by-default disclosure. Keep values, units, selected ranges, and statuses.
- [x] Move detailed status caveat, HGB study-interval caution, and reference/source note into a separate disclosure. Keep download, Q&A, and TTS controls available.
- [x] Review at narrow and wide layout by code inspection; run `git diff --check` and `python -m compileall -q starter-repo/codebase`. Do not add or run tests under the session instruction.

## Execution note

Ruling: do not add or run tests — the active session instruction prohibits tests unless requested; use static checks and fresh review instead.

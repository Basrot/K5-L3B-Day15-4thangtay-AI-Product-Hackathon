# Maternal CBC UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the CBC workbench easy for a pregnant user to start, understand, and use for preparing questions for a clinician.

**Architecture:** Keep the existing single-page Next.js app and API contracts. Change the signed-in workbench into a progressive flow: data entry first, then a focused results view, with full rows, reference details, trends, and account history still available below.

**Tech Stack:** Next.js, React, TypeScript, Tailwind CSS.

**Spec:** `docs/superpowers/specs/2026-11-28-maternal-cbc-ux-design.md`

## Global Constraints

- Preserve all existing calculations, reference ranges, owner checks, and API payloads.
- Keep clinical language descriptive; never present a reference-range status as a diagnosis or treatment instruction.
- Use only confirmed report rows when generating question suggestions.
- Keep every existing edit, history, comparison, source, download, and audio action reachable.
- No tests or builds will be added or run unless the user asks; perform static inspection and `git diff --check` only.

## Review Focus

- A new report has no analysis: show the entry form as the only primary task and avoid an empty results panel.
- A confirmed report is opened: prioritize the result summary but keep a clear path to edit the saved report.
- Validation or analysis fails: keep the form expanded so the user can see and correct it.
- OCR leaves some rows blank: suggestions and result summaries mention only rows that actually contain analyzed values.
- A report contains only within-range rows: generate a relevant status question without implying “normal” or diagnosis.
- On narrow screens: preserve accessible labels and use page scrolling instead of nested scrolling in the analyte list.

## File Map

- `starter-repo/frontend/src/app/page.tsx`: flow state, page hierarchy, form guidance, result overview, contextual question suggestions, history disclosure.
- `starter-repo/frontend/src/app/globals.css`: only small touch-target/focus adjustments if required by the existing styles.
- `docs/superpowers/specs/2026-11-28-maternal-cbc-ux-design.md`: product behavior and copy constraints.

## Tasks

### Task 1: Put the workbench in a clear sequence

**Files:** `starter-repo/frontend/src/app/page.tsx`

- [x] Add a concise page introduction and a three-state progress cue: add report, check and confirm, understand results.
- [x] Make the form full-width when there is no confirmed analysis; hide the empty analysis placeholder.
- [x] After a successful analysis or opening a saved report with a successful analysis, collapse the form by default and show an obvious keyboard-accessible “Sửa thông tin phiếu” control.
- [x] Keep the form open after validation/analysis errors or when a legacy report cannot load analysis.
- [x] Ensure a new session or an unconfirmed restored session opens the form.
- [x] Make the analyte list use normal page scrolling rather than a nested 360px scroll region.

### Task 2: Simplify data entry and help

**Files:** `starter-repo/frontend/src/app/page.tsx`

- [x] Rewrite section titles and helper copy as short actions (“Thêm phiếu”, “Tuổi thai lúc xét nghiệm”, “Khoảng dùng để đối chiếu”).
- [x] Move long trimester/reference explanation into a disclosure while keeping the selected method understandable.
- [x] Add accessible input labels tied to the analyte name/code and numeric keyboard hints for values/reference limits.
- [x] Explain specimen date as optional for comparing reports and retain OCR-as-draft warning.

### Task 3: Make the result and assistant useful at first glance

**Files:** `starter-repo/frontend/src/app/page.tsx`

- [x] Lead with a plain-language summary of analyzed row counts and surface any rows that could not be compared.
- [x] Keep statuses and their meanings adjacent; use neutral wording for rows outside the selected range.
- [x] Replace fixed HGB/WBC sample questions with suggestions derived from analyzed rows; include a summary prompt.
- [x] Label the assistant as help with the confirmed CBC and clarify that it cannot diagnose or decide treatment.
- [x] Keep the full table, reference source, trends, and history available in a clear secondary hierarchy.

### Task 4: Static review of the full flow

**Files:** changed files above.

- [x] Inspect new-report, confirmed-report, edit, and restored-report render paths for unreachable content or contradictory copy.
- [x] Inspect textual/current-step state, accessibility labels, keyboard actions, and mobile stacking in the changed JSX/CSS.
- [x] Review the diff for unintended API, calculation, or medical-language changes.
- [x] Run `git diff --check`; do not run tests/builds under the active session instruction.

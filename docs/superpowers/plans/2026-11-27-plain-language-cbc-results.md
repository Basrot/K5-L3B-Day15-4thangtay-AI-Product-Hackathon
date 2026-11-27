# Plain Language CBC Results Implementation Plan

> **For agentic workers:** Use `superpowers:executing-plans` to implement this plan in the current worktree.

**Goal:** Make pregnancy-stage labels, CBC comparison states, and assistant replies understandable to users without medical training.

**Architecture:** Preserve deterministic CBC/unit comparison and the existing LLM intent router. Update the Next.js result UI and the Python response templates so the displayed and spoken messages explain the selected range without diagnosing.

**Tech Stack:** Next.js/React/TypeScript, FastAPI Python response module, existing VieNeu TTS.

**Spec:** `docs/superpowers/specs/2026-11-27-plain-language-cbc-results-design.md`

## Global Constraints

- Do not change CBC values, units, trimester assignment, reference intervals, or numeric comparison logic.
- Keep the LLM limited to intent/analyte routing; use controlled response templates for medical-data language.
- Refer to the assistant as “em” and the user as “anh/chị”.
- Explain that comparison status alone does not diagnose or rule out illness.
- Keep trimester date boundaries aligned with current logic: stage 1 through 13w6d, stage 2 from 14w0d through 28w6d, stage 3 from 29w0d.
- Do not add or run tests unless requested; use static review and an available frontend build check only.

## Review Focus

- Gestational ages at week boundaries must display the correct existing stage and week range.
- “Within” must not read as a claim that the user is healthy or has no condition.
- “Below” and “above” must explain comparison direction without implying a diagnosis.
- Summary, question response, download text, and spoken TTS content should use compatible wording and pronouns.
- Fake/demo sample values must remain identified as sample data; no data or threshold changes.

---

### Task 1: Clarify pregnancy stage and result states in the frontend

**Files:**
- Modify: `starter-repo/frontend/src/app/page.tsx`

**Interfaces:**
- Consumes: `AnalysisResult.trimester`, `gestational_age`, `reference_mode`, and each row's `status`.
- Produces: plain-language stage title, status labels, and short explanations beside the result table.

- [x] Replace the result heading “Tam cá nguyệt N” with the plain-language pregnancy stage and exact week span, preserving the existing server-provided trimester value.
- [x] Add a short legend explaining below/within/above as positions relative to the selected range and saying the app cannot diagnose from that comparison.
- [x] Show a prominent study-mode caution that being within the study interval does not rule out illness and that the HGB study bound is not a standalone anemia diagnosis.
- [x] Check all three stage labels and all three status descriptions against the design; keep CBC numbers and range selection untouched.

### Task 2: Make assistant and summary replies natural and consistent

**Files:**
- Modify: `starter-repo/codebase/agent.py`

**Interfaces:**
- Consumes: deterministic comparison output and LLM's current `intent`/`analyte` decision.
- Produces: controlled Vietnamese summary, explanation, clarification, medical-advice, and urgent response templates consumed by UI and TTS.

- [x] Rewrite the response templates so the assistant speaks as “em” and addresses the user as “anh/chị”.
- [x] Explain whether the value is below, within, or above the selected range, what comparison that describes, and what the user can ask a doctor; do not diagnose or recommend treatment.
- [x] Use the stage's Vietnamese label and week span in study-range explanations; keep lab-mode language tied to the range printed on the report.
- [x] Keep the LLM routing schema, deterministic numbers, units, and reply construction behavior unchanged.
- [x] Review the changed Python and TypeScript files with `git diff --check` and Python compilation. Run `npm run build` only if frontend dependencies are already available; do not run the test suite.

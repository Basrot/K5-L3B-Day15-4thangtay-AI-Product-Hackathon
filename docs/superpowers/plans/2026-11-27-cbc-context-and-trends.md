# CBC Context and Trends Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let each user compare their confirmed CBC reports over time and prepare specific, neutral questions for their clinician.

**Architecture:** Store a user-confirmed specimen date on each session. Add owner-filtered API access to saved reports and deterministic comparison output; the frontend lets a user select an earlier report and presents matched values, per-report reference statuses, comparability notes, and question prompts.

**Tech Stack:** FastAPI, Pydantic, SQLite, Python; Next.js, TypeScript, React.

**Spec:** `docs/superpowers/specs/2026-11-27-cbc-context-and-trends-design.md`

## Global Constraints

- No diagnosis, severity assessment, or treatment recommendation.
- Do not label a numeric rise or fall as improvement or worsening.
- Do not let an LLM calculate values, classify ranges, or create clinical interpretations.
- Never treat session creation time as specimen date.
- Scope all historical report reads to the authenticated `owner_id`.
- Preserve existing range tables, unit normalization, and status calculations.

## Review Focus

- Legacy sessions have no specimen date: omit them from dated comparison and label them as undated in history.
- A requested comparison uses another owner's session: return not found without exposing report details.
- A CBC row exists in only one report: show it as unavailable for pair comparison.
- Units cannot be safely normalized to the same unit: withhold numeric delta and state why.
- The two reports use different reference modes or pregnancy stages: show each saved status separately and call out the mismatch.

## File Map

- `starter-repo/codebase/api.py`: request schema, owner-scoped history and comparison routes.
- `starter-repo/codebase/service.py`: SQLite migration for specimen date and owner-scoped report listing/loading.
- `starter-repo/codebase/tools.py`: deterministic row pairing and comparison using existing normalized comparison values.
- `starter-repo/frontend/src/lib/types.ts`: history/comparison response types.
- `starter-repo/frontend/src/lib/api.ts`: authenticated history and comparison requests.
- `starter-repo/frontend/src/app/page.tsx`: specimen date input, personal report history selector, comparison view and question prompts.
- `docs/superpowers/specs/2026-11-27-cbc-context-and-trends-design.md`: user-facing behavior and safety constraints.

## Tasks

### Task 1: Save specimen date and expose private report history

**Files:** `starter-repo/codebase/service.py`, `starter-repo/codebase/api.py`

- [x] Add optional ISO `specimen_date` to `Report`, reject future or malformed dates at the API boundary, and preserve compatibility with older reports.
- [x] Add a SQLite migration adding nullable `specimen_date` to sessions; existing sessions stay undated.
- [x] Extend `confirm_report` to save the supplied date and preserve it in session state.
- [x] Add `CBCService.list_reports(owner_id)` returning only confirmed reports for that account, with session ID, specimen date, gestational age, and supported analyte/value/unit summaries.
- [x] Add authenticated `GET /v1/reports/history` that returns that list without another user's data.
- [x] Inspect response shape and SQL filters for legacy rows, deleted rows, and account isolation.

### Task 2: Build deterministic pair comparison

**Files:** `starter-repo/codebase/tools.py`, `starter-repo/codebase/service.py`, `starter-repo/codebase/api.py`

- [x] Add a comparison function taking two confirmed reports and returning per-analyte prior/current values, normalized delta when units match, each report's existing status/range, and explicit `comparable` reasons.
- [x] Do not compute a delta for absent rows or incompatible units; retain each report's own reference metadata.
- [x] Add authenticated `GET /v1/reports/history/{prior_session_id}/compare?current_session_id=...`, verifying both sessions belong to the requester and both are confirmed.
- [x] Return a non-disclosing not-found response when either session is missing or owned by another user.
- [x] Check that output contains only factual value changes and no clinical trend classification.

### Task 3: Add date, history selection, and patient-ready summary

**Files:** `starter-repo/frontend/src/lib/types.ts`, `starter-repo/frontend/src/lib/api.ts`, `starter-repo/frontend/src/app/page.tsx`

- [x] Add an explicit “Ngày lấy mẫu trên phiếu” date field; do not default it from session creation time.
- [x] Add types and API methods for report history and pair comparison.
- [x] Add a “Phiếu trước đây” selector populated only from the current account's confirmed reports; exclude the active report and undated reports from automatic trend comparison.
- [x] Present matched CBC rows as previous value → current value, with neutral wording; show the saved reference status for each date separately.
- [x] Explain missing rows, incompatible units, and changed reference contexts inline.
- [x] Generate fixed, analyte-specific questions from actual present rows, including each current value; do not ask the model to author clinical implications.
- [x] Make history deletion use the existing session-delete path and refresh the history list after deletion.

### Task 4: Review wording and API boundaries

**Files:** changed files above.

- [x] Review every patient-facing sentence against the design constraints; remove “improved”, “worsened”, diagnostic, severity, and treatment wording.
- [x] Review the API paths to confirm all report-history reads and comparisons filter by authenticated account owner.
- [x] Check API schema compatibility for old saved reports and the local demo sample.
- [x] Report verification honestly; automated tests are not part of this plan unless the user explicitly asks to add or run them.

# CBC clinician alert implementation plan

**Goal:** Fix the clinician-question action and add a clear, non-diagnostic summary when several confirmed CBC rows are outside their selected reference ranges.

**Files:** `starter-repo/frontend/src/app/page.tsx`, `starter-repo/codebase/agent.py`, relevant existing output/download behavior, and focused documentation.

**Constraints:** Preserve calculations, references, session ownership, and API contracts. Keep the previously approved controlled-response model: the LLM routes the request; status and safety language come from confirmed structured data and controlled copy. No tests/builds will run in this session unless explicitly requested; verify with code inspection and `git diff --check`.

## Tasks

1. [x] Fix doctor-question action placement: render the draft beside the alert card, scroll/focus it after creation, and remove the hidden duplicate from the comparison area.
2. [x] Add a group alert for confirmed out-of-range rows: list values and statuses, group by CBC system, explain cautiously, and create an explicit AI question from only confirmed rows.
3. [x] Include the visible alert summary in downloaded results; retain existing ranges and status math.
4. [x] Static review and `git diff --check`; no tests/builds.

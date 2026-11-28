# Contextual CBC assistant answers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make every ordinary CBC question receive a concise Gemini-generated answer grounded in the confirmed report and recent same-report conversation, while keeping exact CBC facts server-generated.

**Architecture:** `CBCService` supplies a bounded tail of current-revision chat history to the assistant. The assistant retains deterministic validation and urgent/medical-safety boundaries, then uses one structured model call to compose a conversational explanation and select relevant analytes. The server attaches trusted verified facts separately; the frontend renders them beside the generated prose. Gemini calls use a concise output budget and low reasoning effort where supported.

**Tech Stack:** Python 3.12, FastAPI, SQLite, Gemini OpenAI-compatible Chat Completions, Next.js 15, React 19, TypeScript.

**Spec:** `docs/superpowers/specs/2026-11-28-contextual-cbc-assistant-design.md`

## Global Constraints

- Keep CBC arithmetic, unit conversion, reference intervals, and result status deterministic in `tools.py`.
- Use only confirmed report data and same-report/current-revision recent history; do not send account identifiers or other reports to the model.
- Urgent handling and direct diagnosis/treatment/medicine/dose refusals stay before model generation. Do not diagnose, prescribe, recommend medicine/doses, or invent lab values or sources.
- All ordinary valid questions, including direct status questions, use one generation call; invalid input, missing confirmed report, urgent requests, and direct diagnosis/treatment/medicine/dose refusals may bypass it.
- Keep model output concise, in Vietnamese, with assistant “em” and user “anh/chị”.
- Do not change report ownership, doctor sharing, reference-science, OCR, STT, or TTS behavior.
- Do not add or run tests in this implementation unless the user separately asks for testing; use code review and hosted build/deploy results for verification.

## Review Focus

1. Follow-up like “vậy thấp thì có thể do đâu?” must resolve from same-revision turns without guessing when context is ambiguous.
2. Model output with invalid JSON, unknown analytes, or unsupported numbers must not override verified facts or crash the chat.
3. Urgent wording must bypass generation and preserve immediate-care guidance.
4. Cause questions must remain educational; diagnosis, medicine, and dose requests must stay within refusal/safety behavior.
5. History from an old report revision or another user's session must never enter the prompt.

---

### Task 1: Add bounded same-report conversation context

**Files:**
- Modify: `starter-repo/codebase/service.py`
- Modify: `starter-repo/codebase/agent.py`

**Interfaces:**
- `CBCService.ask(...)` may read prior messages for the same `session_id` and `revision`, bounded to the latest four question/answer pairs.
- `answer(text, *, confirmed=False, history=None)` accepts an optional list of `{question, output}` dictionaries; existing `run.py` calls remain compatible with the default `None`.

- [ ] Read prior current-revision messages before composing the current answer; exclude the current request and trim each stored question/output to bounded lengths before passing to the model.
- [ ] Ensure cached request-id retries return the stored answer without invoking the model again.
- [ ] Confirm via code inspection that history query predicates still bind to session owner and current revision.

### Task 2: Replace intent-only classification with grounded answer generation

**Files:**
- Modify: `starter-repo/codebase/agent.py`
- Modify: `starter-repo/codebase/ai.py` only if provider options need a new optional argument.

**Interfaces:**
- The structured model response contains `{answer: string, analytes: string[], needs_clarification: boolean}`; analytes must be a subset of the confirmed CBC rows.
- Chat result keeps `status` and `output`; add `verified_facts: array` with exact `{analyte, value, unit, ref_low, ref_high, status}` objects from `comparison["rows"]`.
- The existing deterministic `analyze_report`, unit comparison, source catalog, `model_call` tracing, and request cache contracts remain intact.

- [ ] Keep hard urgent routing before any model call.
- [ ] Refine the medical boundary so general educational “what could cause this?” questions can be explained, while direct diagnosis and treatment/medicine/dose requests remain safely refused.
- [ ] Build model context from confirmed comparison rows, indicator descriptions, reference provenance, current question, and only the bounded same-revision conversation turns.
- [ ] Replace classifier-plus-template routes for ordinary valid questions with one schema-constrained generated explanation. Map `needs_clarification=true` to the existing clarify status; use a safe fallback if the model returns invalid structure.
- [ ] Validate every returned analyte against confirmed rows; choose supporting sources only from the existing known catalog; never accept model-provided values, ranges, or citations.
- [ ] Return a separate `verified_facts` list from deterministic comparison rows, limited to selected analytes (or the full panel for summary requests).
- [ ] Retain deterministic status and source metadata in the response and preserve trace/token accounting.

### Task 3: Reduce generation latency without changing model/provider

**Files:**
- Modify: `starter-repo/codebase/ai.py`
- Modify: `starter-repo/codebase/agent.py`

**Interfaces:**
- Add an optional `reasoning_effort` argument to `call_model`; send it only to OpenAI-compatible Gemini requests when explicitly requested.
- Ordinary CBC generation requests `reasoning_effort="low"` for the configured Gemini 4 Hydrogen model and sets a concise response budget (maximum 280 completion tokens).
- Other providers and Ollama requests keep their existing payload contracts.

- [ ] Add provider-aware optional `reasoning_effort` support without altering vision/OCR calls.
- [ ] Set the generated answer prompt to answer directly in 1–3 short paragraphs, normally at most 100 Vietnamese words, and avoid unnecessary preamble. Use at most 280 completion tokens so the answer can explain a follow-up without excessive latency.
- [ ] Keep all ordinary valid questions to a single model call; do not add a separate intent-classification call.

### Task 4: Render verified facts separately from generated prose

**Files:**
- Modify: `starter-repo/frontend/src/lib/types.ts`
- Modify: `starter-repo/frontend/src/app/page.tsx`

**Interfaces:**
- Extend `ChatResult` with optional `verified_facts` entries using the server's exact analyte, value, unit, reference bounds, and status values.
- Render a compact “Dữ kiện từ phiếu đã xác nhận” block from those fields, then the model-generated explanation as the main answer.

- [ ] Update the chat card to distinguish exact verified result/status facts from generated explanation text.
- [ ] Keep existing source links, audio button, and history display working.
- [ ] Change the “AI làm gì” help text to say the model writes explanations from confirmed report facts and recent turns; keep the statement that answers are not clinician-approved.
- [ ] Preserve the user-visible response loading/error behavior.

### Task 5: Document the updated answer behavior and inspect the final diff

**Files:**
- Modify: relevant existing AI safety/handoff documentation only where current text says replies are controlled templates or intent-only.

- [ ] Search documentation and update only statements contradicted by the new implementation.
- [ ] Run `git diff --check` and inspect the complete diff for secret exposure, unrelated scope, response contract consistency, and the five Review Focus cases.
- [ ] Push the commit to the user's fork branches used by Railway and Vercel; confirm hosted builds/deployments report success before saying the version is ready to try.

**Verification note:** Automated tests are intentionally excluded in accordance with the current instruction. Local package/runtime availability is limited; hosted build status and a manual review of endpoint contracts are the available verification evidence.

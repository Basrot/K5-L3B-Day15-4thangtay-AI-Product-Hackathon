# Contextual CBC assistant answers

## Intent

Make the CBC question assistant answer the user's actual question in natural Vietnamese and carry the context into follow-up questions. The current behavior feels scripted: the model classifies an intent, then `agent.py` returns a fixed template. `service.ask()` stores chat history but does not pass previous turns to `answer()`, so follow-ups are not conversational.

The user has approved a hybrid approach: let the model compose explanations and understand follow-ups, while keeping CBC values, units, reference intervals, and range status grounded in the server's deterministic comparison.

## User experience

Example conversation:

1. User: “HGB của tôi có ổn không?”
2. Assistant: shows the exact confirmed result and comparison in a trusted fact block, then generates an explanation of what that status means in plain language.
3. User: “Nếu thấp thì có thể do đâu?”
4. Assistant: understands that “thấp” refers to HGB from the current report and gives a cautious explanation of possibilities and what a clinician may consider, without diagnosing or recommending treatment.

The answer should use “em” for the assistant and “anh/chị” for the user. It should answer first, avoid repeating a generic invitation to name an analyte when context already identifies it, and keep the explanation concise.

## Approaches considered

1. **Expand fixed templates.** Fast and easy to constrain, but still fails on natural follow-ups and open-ended questions. Not selected because the user says the current templated experience has no depth.
2. **Unconstrained model-generated medical answers.** Natural and flexible, but risks unsupported interpretations and incorrect CBC facts. Not selected.
3. **Grounded generation with deterministic facts (selected).** The model writes the explanation and interprets follow-up context from the current report conversation. The server remains the source of truth for numbers, units, ranges, and statuses; urgent-safety and diagnosis/treatment boundaries remain enforced before generation.

## Goals

- Answer follow-up questions using a bounded history from the same confirmed report and revision.
- Generate a model-written answer for every ordinary, valid question instead of returning a fixed analyte definition for every question.
- Preserve deterministic CBC comparison and clear separation between an observation and a diagnosis.
- Reduce avoidable latency by making one concise generation call for ordinary questions, keeping urgent and invalid-input handling local, and using a low reasoning setting for Gemini where supported.
- Keep the doctor-facing and patient-facing data ownership and sharing rules unchanged.

## Non-goals

- Diagnose a condition, prescribe medication, recommend a dose, or replace clinician judgment.
- Let the model calculate, normalize, invent, or modify CBC values, units, reference ranges, or comparison status.
- Add web search, patient-wide memory, new clinical sources, or additional stored health data.
- Change OCR, STT, TTS, reference interval science, report ownership, or doctor portal behavior.
- Promise that provider outages (including HTTP 503) can be fixed in application code.

## Safety and grounding

- Recompute/verify the confirmed comparison on the server before each answer.
- Give the model only the confirmed report facts needed for the question, the existing safe explanation metadata, and a bounded recent conversation from the same report revision. Do not send account identifiers or unrelated history.
- Keep urgent symptom routing deterministic and before model calls. Keep diagnosis, medication, and treatment requests inside the existing safety boundary; allow general educational explanations such as what clinicians may consider, without presenting a cause as established.
- Keep verified values and status in server-generated fields. Model prose must not be treated as the source of numerical truth; UI continues to display the trusted comparison separately. Do not accept unsupported analyte codes, sources, or diagnosis claims from model output.
- Use the existing source catalog only; the model must not invent citations.
- If structured output is malformed or violates the answer contract, return a clear fallback that preserves the verified facts and invites the user to rephrase, rather than silently reverting to the generic “which indicator?” template.

## Latency

- Remove the current “classify, then choose a canned response” path and use one model generation call for ordinary explanatory questions.
- Keep only urgent, invalid-input, and no-confirmed-report handling as local fast paths. Every ordinary, valid question—including a direct status question—goes through one generation call, matching the user's request that answers be generated.
- Render the exact confirmed result, unit, range, and status in a separate trusted fact block from server fields. Generated prose explains those facts but is not authoritative for numeric values.
- Set a concise output budget and low Gemini reasoning effort where supported by the configured Gemini OpenAI-compatible API. Preserve support for other OpenAI-compatible providers without sending provider-specific fields to them.
- Surface a clear retry message for provider 5xx errors. Measure model latency separately from UI loading and upstream failures; do not claim a latency improvement until measured.

## Conversation state

- Reuse the existing `messages` table, scoped by session and revision. Pass a small bounded tail (proposed: up to 4 prior question/answer pairs) to the model; do not add a new table or store more history.
- When report data changes, the existing revision behavior continues to isolate or clear stale conversation turns.
- Preserve request-id idempotency and current ownership checks.

## Files likely affected

- `codebase/agent.py`: prompt, answer contract, contextual model generation, deterministic safety boundaries, and fallback handling.
- `codebase/service.py`: provide bounded same-revision conversation context to the answer workflow.
- `codebase/ai.py`: provider-aware low-reasoning/output options only if needed to meet the selected latency design.
- `frontend/src/app/page.tsx`: update the assistant description so it no longer claims answers are fixed templates, and ensure concise generated replies remain readable.
- Relevant docs may be updated to describe the actual generated-answer behavior and its limits.

## Success criteria

- A direct status question receives generated explanatory prose, while a separate trusted fact block shows the confirmed analyte, result, unit, reference interval, and status.
- A second-turn question like “vậy thấp thì có thể do đâu?” resolves to the analyte discussed earlier when there is adequate recent context.
- A follow-up asking to elaborate produces a relevant explanation instead of a generic clarify template.
- Urgent, diagnosis, and treatment boundaries still work.
- Model output cannot override the server's calculated status or add a fabricated source.
- On a healthy configured provider, concise answer latency is measured and compared against the current implementation; provider 5xx failures are recorded separately.

## Open implementation calls

- Builder may settle the exact structured response schema, message window trimming, and safe-output validation strategy, provided all goals and safety constraints above are met.
- The currently selected model is `gemini-4-hydrogen`; retain it initially and use low reasoning effort before considering a provider/model change.
- Ordinary valid questions all use generated prose; only urgent and invalid/no-confirmed-report requests bypass generation. This follows the user's explicit request that every question receive a generated answer.

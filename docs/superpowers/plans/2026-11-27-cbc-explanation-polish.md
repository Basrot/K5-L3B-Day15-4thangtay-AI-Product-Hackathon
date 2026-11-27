# CBC Explanation Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the eight supported CBC answers explain what each index measures and remove duplicated study caveats from prose.

**Architecture:** Keep reference selection, unit normalization, and status calculation unchanged. Add concise definitions in the existing answer module and return scope/source details only through the existing metadata fields.

**Tech Stack:** Python 3.12, unittest.

**Spec:** `docs/superpowers/specs/2026-11-27-cbc-explanation-design.md`

## Global Constraints

- Support only HGB, RBC, HCT, MCV, MCH, MCHC, WBC, and PLT.
- Do not turn a reference interval flag into a diagnosis or treatment recommendation.
- Do not change research values, units, trimester boundaries, or source metadata.
- Preserve the existing model-call boundary and constrained routing output.

## Review Focus

- A question asking what an index means should include a definition; verify for RBC and coverage of all eight definitions.
- Study caveats should remain accessible without being appended to generated prose; verify in both analysis and chat output.
- Existing exact range and conversion behavior must remain unchanged; run reference and CBC tests after implementation.

---

### Task 1: Improve deterministic explanations

**Files:**
- Modify: `starter-repo/codebase/agent.py`
- Test: `starter-repo/tests/test_study_references.py`

**Interfaces:**
- Consumes `compare_cbc(report)` output and the existing `reference_note` metadata.
- Produces the existing response shape with more informative `output`; metadata remains unchanged.

- [x] Add failing tests for an RBC definition in chat output, definitions for all eight codes, and absence of duplicated `reference_note` in summary/chat prose.
- [x] Run `python -m unittest discover -s tests -p test_study_references.py -v` and confirm the new assertions fail for the current response.
- [x] Add a fixed definition for every supported index and remove the scope note from prose while preserving the structured note and source metadata.
- [x] Re-run the focused test module and existing CBC AI tests.
- [x] Run the full unittest suite after final source links and inspect the branch diff.

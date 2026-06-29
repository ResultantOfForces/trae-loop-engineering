# Cross-Model Task Packet — Fillable Template

> Fillable task-packet for `dual_mode: cross_model_manual`. The main agent produces plan-A (or review-A) in the current session, then packs this packet containing ONLY the brief/context + required headings + independence declaration + a planning-only (or read-only) write constraint. The user transports the packet to a different-model TRAE multi-task session; the returned B output is written verbatim into the B artifact. The packet must NOT contain plan-A, review-A, or any main-agent conclusion — it is the audit trail proving B's input did not contain A. See `references/hybrid-dual.md` for the full 6-step flow and honesty markers.

## Hard Rules

- The packet must not contain A (plan-A or review-A) or any main-agent conclusion.
- The different-model session does not share context with the main session.
- The human only transports; does not edit, summarize, add, or remove.
- The main agent is the first role allowed to compare A and B (as merger / arbitrator).
- The returned B output is written verbatim into the B artifact with only a cross-model provenance header.

---

## Variant: Plan-B Task Packet (`11-plan-B-task-packet.md`)

```markdown
# Task: Independent Plan B (Cross-Model)

You are an independent planning agent. A separate planner has been working on the same brief, but you must NOT assume any prior plan exists. Produce your own independent plan from the brief below.

## Brief (00-brief.md)

<paste brief full text — verbatim>

## Context Pack

<paste relevant complete code excerpts, constraints, known risks, prior final report summary>

## Required Output

Write a plan with exactly these sections:
## Goal
## Scope
## Tasks
## Tests / Verification
## Risks
## Not Doing

## Constraints

- Do not modify any code files. You are planning only.
- Do not ask follow-up questions. Work with the information provided.
- If the brief is missing a strategic "good enough" target, note it as `strategy-gap: <missing decision>` and still produce your best plan.

## Independence Declaration

No other plan has been shared with you. Your output will be compared against an independent Plan A only after both are complete.
```

---

## Variant: Review-B Task Packet (`31-review-B-task-packet.md`)

```markdown
# Task: Independent Read-Only Review (Cross-Model)

You are an independent review agent. Perform a read-only review of the execution below. Do not modify any code. Do not assume any other review exists.

## Evidence Bundle

### Merged Plan (12-plan-merged.md)
<paste or attach path>

### Execution Report (20-execution-report.md)
<paste or attach path>

### Changed Diff
<paste precise diff hunks + surrounding lines>

### Relevant Complete Functions
<paste complete function bodies — do not replace judged logic with ellipses>

### Test Output
<paste full command + pass/fail count>

### Acceptance Criteria
<paste criteria>

## Required Output

Write a review with exactly these sections:
## Source
## Findings
- P0/P1/P2/P3: <title>
  Claim: <what is wrong>
  Evidence: <path:line / command output / artifact path>
  Why it matters: <impact>
  Suggested action: <fix>
## Criteria Check

## Constraints

- Read-only. Do not modify any files.
- Do not ask follow-up questions.
- Every factual claim must carry path:line, command output, or `not verified`.
- Focus on bugs, regressions, missing tests, evidence-boundary violations, and user workflow failures.

## Independence Declaration

No other review has been shared with you. Your output will be compared against an independent Review A only after both are complete.
```

---

## Cross-Model Provenance Header

When the transported B output is written back into the main session, prefix the artifact body with exactly this header (no other edits, no summarizing, no cleanup):

For plan-B (`11-plan-B.md`):

```text
<!-- source: cross-model plan-B / model: <model name> / task_packet: 11-plan-B-task-packet.md / transported_by: user / dispatched: <ISO-8601 time> -->
```

For review-B (`31-review-B.md`):

```text
<!-- source: cross-model review-B / model: <model name> / task_packet: 31-review-B-task-packet.md / transported_by: user / dispatched: <ISO-8601 time> -->
```

---

## Honesty Markers (record when `dual_mode: cross_model_manual`)

- `loop-state.md`: `dual_mode: cross_model_manual`; `subagent_dispatches` for plan-B/review entries have status `unavailable` or are absent (because they were transported, not dispatched).
- `strategic-loop-contract.md`: `dual_mode: cross_model_manual`; record the model name and task-packet path.
- `12-plan-merged.md` Source Plans: note plan-B source as "cross-model manual, model: <name>".
- `50-final-report.md`: record `dual_mode: cross_model_manual` and the transport fact.

Do not pretend a cross-model manual dual was an automatic subagent dual. The task-packet artifact is the audit trail proving plan-B's input did not contain plan-A.

---

## Workflow Checklist

1. Main agent produces A (`10-plan-A.md` / `30-review-A.md`) in the current session.
2. Generate the task-packet artifact (`11-plan-B-task-packet.md` / `31-review-B-task-packet.md`) using a variant above — no A inside.
3. User opens a TRAE multi-task with a model from a different family.
4. Run the packet in the new session (paste content or point it at the file path).
5. Transport the model's output back to the main session.
6. Main agent writes the output verbatim into `11-plan-B.md` / `31-review-B.md` with the cross-model provenance header only.
7. Main agent merges / arbitrates by evidence (identity-blind, per `references/evidence-standards.md`).

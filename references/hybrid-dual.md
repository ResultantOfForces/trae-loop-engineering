# Hybrid Dual

Use this reference when choosing between same-model automatic dual (default) and cross-model manual dual (upgrade). This is the core adaptation for the fact that TRAE Task subagents inherit the session model and cannot run a different model.

## TRAE Subagent Model Constraint

TRAE's Task tool dispatches subagents that run in the SAME model as the current session. There is no API to select a different model for a subagent. Therefore:

- Same-model dual (plan-A and plan-B from the same model, isolated contexts) CAN be automated via Task subagents.
- Cross-model dual (plan-A from model X, plan-B from model Y) CANNOT be automated via Task. It requires manual transport via TRAE's multi-task feature.

This is a capability boundary, not a preference. Be honest about which path a loop used.

## Two Paths

| path | dual_mode | mechanism | when |
|---|---|---|---|
| same-model auto (default) | `same_model_auto` | Task subagent, inherits session model, automatic return | T3+ default |
| cross-model manual (upgrade) | `cross_model_manual` | TRAE multi-task with different models, user transports task-packet | high-risk + user decides cross-model independence needed |
| no dual | `not_needed` | single-agent | T0-T2 |

## Default Path: Same-Model Auto

Unchanged from `subagent-dispatch.md`. The main agent dispatches plan-B / review-A / review-B as Task subagents. The subagent inherits the session model, returns output, the main agent writes it verbatim. Independence is preserved by prompt isolation (subagent sees only brief/evidence bundle, never A).

Honesty note: same-model dual is weaker than codex's cross-model dual. The same model may share systematic blind spots across both calls. This is the tradeoff for automation. For high-risk work, escalate to cross-model manual.

## Upgrade Path: Cross-Model Manual

### When To Escalate
- task is high-risk: auth, data migration, architecture change, data-loss risk, cross-module impact;
- the user explicitly wants cross-model independent judgment (e.g. two different model families checking each other);
- same-model dual already ran but the two plans/reviews were highly similar, suggesting low independence value.

The main agent may SUGGEST escalation; the user decides. Do not auto-escalate.

### The 6 Steps

1. **Main agent produces A and packs a task-packet.**
   - Complete `10-plan-A.md` (or `30-review-A.md`) in the current session.
   - Generate a task-packet artifact (e.g. `11-plan-B-task-packet.md`) containing ONLY: brief full text + context pack + required headings + independence declaration + planning-only write constraint. It must NOT contain plan-A or any main-agent conclusion. This packet follows the exact template in `subagent-dispatch.md`.

2. **User opens a TRAE multi-task with a different model.**
   - In TRAE, create a new multi-task and select a model from a different family than the current session.
   - The multi-task session is an independent context; it does not share history with the main session (this satisfies independence).

3. **Run the task-packet in the new session.**
   - Paste the task-packet content into the new session (or have it read the task-packet file path).
   - Ask that model to independently produce plan-B. It does not know plan-A exists.

4. **Transport B back to the main session.**
   - Copy the model's output verbatim back to the main session.

5. **Main agent writes B verbatim into the artifact.**
   - Write the output into `11-plan-B.md` with a cross-model provenance header only:
     ```
     <!-- source: cross-model plan-B / model: <model name> / task_packet: 11-plan-B-task-packet.md / transported_by: user / dispatched: <iso time> -->
     ```
   - Do not edit, summarize, or compress the output (same verbatim rule as subagents).

6. **Main agent merges by evidence.**
   - As merger, write `12-plan-merged.md` using the same conflict-resolution discipline as same-model dual.
   - Arbitration cites evidence, not model identity (`evidence-standards.md` unchanged).

### Dual Review Cross-Model Upgrade
Same flow: main agent produces review-A + packs `31-review-B-task-packet.md` (evidence bundle only, no review-A) -> user opens different-model session -> runs packet -> transports review-B back -> main agent writes `31-review-B.md` verbatim with cross-model provenance header -> arbitrates by evidence.

### Independence Rules (Same As Same-Model Dual)
- The task-packet must not contain A.
- The different-model session does not share context with the main session.
- The human only transports; does not edit, summarize, add, or remove.
- The main agent is the first role allowed to compare A and B (as merger/arbitrator).

## Honesty Markers

When `dual_mode: cross_model_manual`, record it honestly in:

- `loop-state.md`: `dual_mode: cross_model_manual`; `subagent_dispatches` for plan-B/review entries have status `unavailable` or are absent (because they were transported, not dispatched).
- `strategic-loop-contract.md`: `dual_mode: cross_model_manual`; record the model name and task-packet path.
- `12-plan-merged.md` Source Plans: note plan-B source as "cross-model manual, model: <name>".
- `50-final-report.md`: record `dual_mode: cross_model_manual` and the transport fact.

Do not pretend a cross-model manual dual was an automatic subagent dual. The task-packet artifact is the audit trail proving plan-B's input did not contain plan-A.

## When Not To Escalate

- T0-T2: no dual at all (`dual_mode: not_needed`).
- T3 low-risk: same-model auto dual is sufficient.
- User has not decided to escalate: default to same-model auto; the main agent does not auto-escalate.

## Relationship To subagent-dispatch.md

`subagent-dispatch.md` remains the authority for the same-model auto path (Task subagent dispatch, prompt templates, failure handling, verbatim write rule). This file is the cross-model extension. When `dual_mode: same_model_auto`, follow `subagent-dispatch.md` fully. When `dual_mode: cross_model_manual`, replace the Task dispatch steps (3-4 of Dual Plan, 3-6 of Dual Review) with the manual transport steps above; the independence rules, evidence standards, and verbatim write rule still apply.

# loop-state.md — Fillable Template

> Copy this file to `docs/loop-engineering/<YYYY-MM-DD-slug>/loop-state.md`, overwrite it on each state change, and read it first on resume. It is the single snapshot that every resume reads before the worklog and artifacts. Field structure, update timing, and consistency constraints live in `references/loop-state-schema.md`; validate the result with `scripts/validate-loop-state.ps1` (or `scripts/validate-loop-state.py` on macOS/Linux).

```yaml
# loop-state.md — TRAE Loop Engineering single state snapshot
# Overwrite on each change. Read first on resume.

loop_id: <YYYY-MM-DD-slug>                  # same as the artifact dir name; unique across sessions
artifact_dir: docs/loop-engineering/<YYYY-MM-DD-slug>

# --- current progress ---
phase: <brief|dual_plan|plan_merge|execution|execution_report|dual_review|arbitration|final>
phase_step: <1-8>                           # which of the 8 phases
role: <planning|execution|review|arbitration|manager>
loop_status: <active|blocked|completed|paused|limit_reached>

# --- resume directives ---
next_action: "<the concrete next action this role should take>"
next_role: <planning|execution|review|arbitration|manager>
next_phase: <phase entered after the current one completes>

# --- blockers and gaps ---
blockers: []                                # each entry: {type, detail, artifact}
                                            # type: plan_gap|strategy_gap|subagent_unavailable|user_decision|loop_limit_reached|external
open_gaps: []                               # active markers: strategy-gap|plan-gap|loop-limit-reached

# --- routing and policy ---
route_tier: <T0|T1|T2|T3|T4|T5>
subagent_policy: <not_needed|conditional|required>
dual_mode: <same_model_auto|cross_model_manual|not_needed>
auto_iteration: <enabled|disabled>           # disabled = confirm each step (requires TRAE auto-run ON to take effect)

# --- artifact pointers ---
latest_artifacts:
  brief: 00-brief.md
  plan_a: 10-plan-A.md
  plan_b: 11-plan-B.md
  plan_merged: 12-plan-merged.md
  execution_report: null                     # null = not yet produced
  review_a: null
  review_b: null
  arbitration: null
  final_report: null
worklog: worklog.md

# --- iteration counters ---
repair_iteration: 0                          # current brief's repair count, cap 2
open_p0_count: 0
open_p1_count: 0

# --- subagent tracking ---
subagent_dispatches: []                     # each entry: {role, subagent_id, artifact, status, dispatched_at}
                                            # status: dispatched|returned|failed|unavailable

# --- user decisions ---
user_decisions_pending: []                  # non-empty => loop_status must be blocked
user_decisions_resolved: []

# --- resume metadata ---
resume_count: 0
created_at: <ISO-8601 timestamp with timezone, e.g. 2026-06-28T10:00:00+08:00>
last_updated: <ISO-8601 timestamp with timezone>
last_event: "<one-line description of the latest state change>"
```

## Consistency Constraints

Checked by `scripts/validate-loop-state.{ps1,py}`:

- `blockers` non-empty AND `loop_status=active` -> warning.
- `open_gaps` non-empty -> `loop_status` must be `blocked` / `paused` / `limit_reached`.
- `user_decisions_pending` non-empty -> `loop_status` must be `blocked`.
- `repair_iteration > 2` -> `open_gaps` must contain `loop-limit-reached`.
- `dual_mode=cross_model_manual` -> plan-B/review entries in `subagent_dispatches` must have status `unavailable` or be absent (they are transported manually, not dispatched).
- `phase=final` AND `loop_status=active` -> warning (final phase should complete or block).

## Update Triggers

Overwrite the relevant fields whenever state changes. Always update `last_updated` and `last_event`.

| trigger | fields to update |
|---|---|
| loop start | all initialized; `loop_status=active`; `resume_count=0` |
| phase change | `phase`, `phase_step`, `next_phase`, `role`, `next_action` |
| role change | `role`, `next_action`, `next_role` |
| artifact landed | `latest_artifacts.<key>`, `last_event` |
| blocker appears | `blockers`, `loop_status=blocked`, `user_decisions_pending` |
| blocker resolved | `blockers`, `loop_status=active`, `user_decisions_resolved` |
| subagent dispatch | `subagent_dispatches` (append entry) |
| repair iteration | `repair_iteration`, `open_p0_count`, `open_p1_count` |
| gap marker | `open_gaps`, `loop_status=blocked` |
| user decision | `user_decisions_pending` / `user_decisions_resolved`, `loop_status` |
| resume | `resume_count+1`, `last_updated`, `last_event="resumed from <phase>"` |
| completion | `loop_status=completed`, `next_action=null` |

After writing a `state_event` to the worklog, sync the matching fields here. The worklog records the transition; this file records the resulting state.

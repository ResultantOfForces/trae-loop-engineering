# Loop State Schema

Use this reference when a loop needs a resumable single-source-of-truth snapshot. `loop-state.md` is the **current state** file that every resume reads first.

## Snapshot vs Event Stream

There are three memory layers. Do not confuse them:

| layer | file | role | update style |
|---|---|---|---|
| snapshot | `loop-state.md` | current phase/role/next_action/blockers — the first file read on resume | overwrite on each change |
| event stream | `worklog.md` + state/feedback events | history of phase transitions, decisions, repairs | append-only |
| artifacts | `00-brief.md` through `50-final-report.md` | durable outputs | one owner each, append-only notes |

`loop-state.md` answers "where is the loop right now?". `worklog.md` answers "how did it get here?". Resume reads the snapshot first, then the event stream for context, then the relevant artifacts.

## File Location

`docs/loop-engineering/YYYY-MM-DD-slug/loop-state.md` — at the artifact directory root, next to `00-brief.md`. One per loop. The file name is always `loop-state.md` (not dated), so resume can find it by convention.

## Field Structure

```yaml
# loop-state.md — TRAE Loop Engineering single state snapshot
# Overwrite on each change. Read first on resume.

loop_id: 2026-06-28-auth-async-await     # same as artifact dir name; unique across sessions
artifact_dir: docs/loop-engineering/2026-06-28-auth-async-await

# --- current progress ---
phase: execution                          # brief|dual_plan|plan_merge|execution|execution_report|dual_review|arbitration|final
phase_step: 4                             # 1-8, which of the 8 phases
role: execution                           # planning|execution|review|arbitration|manager
loop_status: active                       # active|blocked|completed|paused|limit_reached

# --- resume directives ---
next_action: "Rewrite src/auth/login.ts per 12-plan-merged.md; write 20-execution-report.md"
next_role: execution
next_phase: execution_report              # phase entered after current completes

# --- blockers and gaps ---
blockers: []                              # each: {type, detail, artifact}
                                          # type: plan_gap|strategy_gap|subagent_unavailable|user_decision|loop_limit_reached|external
open_gaps: []                             # active markers: strategy-gap|plan-gap|loop-limit-reached

# --- routing and policy ---
route_tier: T3
subagent_policy: required                 # not_needed|conditional|required
dual_mode: same_model_auto                # same_model_auto|cross_model_manual|not_needed
auto_iteration: enabled                   # enabled|disabled (disabled = confirm each step)

# --- artifact pointers ---
latest_artifacts:
  brief: 00-brief.md
  plan_a: 10-plan-A.md
  plan_b: 11-plan-B.md
  plan_merged: 12-plan-merged.md
  execution_report: null                  # null = not yet produced
  review_a: null
  review_b: null
  arbitration: null
  final_report: null
worklog: worklog.md

# --- iteration counters ---
repair_iteration: 0                       # current brief's repair count, cap 2
open_p0_count: 0
open_p1_count: 0

# --- subagent tracking ---
subagent_dispatches: []                   # each: {role, subagent_id, artifact, status, dispatched_at}
                                          # status: dispatched|returned|failed|unavailable

# --- user decisions ---
user_decisions_pending: []                # non-empty => loop_status must be blocked
user_decisions_resolved: []

# --- resume metadata ---
resume_count: 0
created_at: 2026-06-28T10:00:00+08:00
last_updated: 2026-06-28T14:30:00+08:00
last_event: "execution started on src/auth/login.ts"
```

## Update Timing

Overwrite the relevant fields whenever the loop state changes. Always update `last_updated` and `last_event`.

| trigger | fields to update |
|---|---|
| loop start | all initialized; loop_status=active; resume_count=0 |
| phase change | phase, phase_step, next_phase, role, next_action |
| role change | role, next_action, next_role |
| artifact landed | latest_artifacts.<key>, last_event |
| blocker appears | blockers, loop_status=blocked, user_decisions_pending |
| blocker resolved | blockers, loop_status=active, user_decisions_resolved |
| subagent dispatch | subagent_dispatches (append entry) |
| repair iteration | repair_iteration, open_p0_count, open_p1_count |
| gap marker | open_gaps, loop_status=blocked |
| user decision | user_decisions_pending/resolved, loop_status |
| resume | resume_count+1, last_updated, last_event="resumed from <phase>" |
| completion | loop_status=completed, next_action=null |

After writing a `state_event` to the worklog, sync the matching fields here. The worklog records the transition; this file records the resulting state.

## Consistency Constraints

These are checked by `scripts/validate-loop-state.ps1`:

- `blockers` non-empty AND `loop_status=active` -> warning
- `open_gaps` non-empty -> `loop_status` must be blocked/paused/limit_reached
- `user_decisions_pending` non-empty -> `loop_status` must be blocked
- `repair_iteration > 2` -> `open_gaps` must contain `loop-limit-reached`
- `dual_mode=cross_model_manual` -> plan-B/review entries in `subagent_dispatches` must have status `unavailable` or be absent (because they are transported manually, not via subagent)
- `phase=final` AND `loop_status=active` -> warning (final phase should complete or block)

## Relationship To Other Files

- `state-feedback-schema.md` defines the append-only event structure written to `worklog.md`. This file is the snapshot that event stream produces.
- `resume-protocol.md` defines how a new session reads this file first to continue the loop.
- `strategic-loop-contract.md` records the planned route/dual_mode; this file records the live state.
- `strategic-loop-contract.md`'s `operation.loop_state_path` should point at this file.

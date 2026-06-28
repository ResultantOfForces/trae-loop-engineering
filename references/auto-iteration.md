# Auto-Iteration

Use this reference when the loop should advance automatically to complete a task with minimal manual intervention. Auto-iteration is the default mode for long-running work; it is gated by halt points so it never runs away.

## Prerequisite: TRAE Auto-Run Setting

Auto-iteration requires TRAE's auto-run setting to be ON. Path: Settings > Conversation flow > Auto-run. When enabled, the agent executes commands, MCP tools, and subagent dispatches without per-step confirmation.

- If auto-run is ON and `auto_iteration: enabled` in `loop-state.md` -> the loop advances automatically, stopping only at halt points.
- If auto-run is OFF, or `auto_iteration: disabled` -> the loop still works, but each execution step pauses for user confirmation. This is useful for high-risk phases or first runs.

Auto-run only removes per-step confirmation. It does NOT bypass halt points. The halt points below apply regardless of the auto-run setting.

## Auto-Advance (No Pause)

The loop may advance without asking when:

- writing or repairing a planning/control artifact (brief, plan, merged plan, worklog, state-feedback, loop-state.md);
- running a validator or verification command;
- dispatching a Task subagent and writing its output verbatim into the artifact;
- transitioning sequentially between phases (brief -> dual_plan -> plan_merge -> execution -> execution_report -> dual_review -> arbitration -> final), PROVIDED no halt trigger is active;
- performing a repair iteration within the cap (repair_iteration <= 2);
- updating `loop-state.md` and appending worklog events.

## Halt Points (Must Stop, Never Bypass)

The loop MUST stop and wait when any of these is true. These are the union of stop rules and must-ask checkpoints:

- any stop rule in `stop-rules.md` triggers (third new P0, max repair iterations, P0 blocking final, two reviews agree on P0 without counter-evidence);
- any must-ask checkpoint in `user-checkpoints.md` (multiple product directions, underspecified UX, brief/goal change, plan-gap, required subagent artifact missing/malformed, proceeding degraded after a required gate, review/arbitration changing scope, two reviews agree on P0, detected drift);
- any blocker in `loop-state.md` is non-empty;
- any gap marker is active (`strategy-gap` / `plan-gap` / `loop-limit-reached`);
- `user_decisions_pending` is non-empty;
- a required subagent artifact is unavailable and the user has not approved degraded continuation for that exact phase;
- resume discovered `resume-with-gap` (per `resume-protocol.md` Step 6).

## Controlled Transition: Planning -> Execution

The planning-to-execution boundary is a controlled auto-advance point, not a free pass. The loop may auto-advance from planning to execution only when ALL auto-dispatch conditions in `user-checkpoints.md` are met:

- the user already participated in the planning direction or asked to keep the loop moving;
- the plan selects the user-confirmed strategic direction;
- subagent/validator/required-gate status is clean, or the user approved the recorded degraded mode;
- no `plan-gap`, `strategy-gap`, disputed scope, malformed artifact, destructive action, or unclear acceptance criterion;
- the next execution handoff preserves the plan's hard boundaries and stop condition.

If any condition fails, stop at the planning closeout for a checkpoint. Record `checkpoint_resolved_by: manager` only when all conditions hold, then dispatch execution.

This controlled transition preserves the planning-execution firewall: planning never self-promotes into execution; it auto-advances only through a validated gate.

## Auto-Iteration And Subagents

Subagent dispatch is auto-advance-eligible (it is in the auto-advance list). But:

- a `subagent_policy: required` gate that comes back unavailable is a halt point;
- the main agent must still write subagent output verbatim and validate required headings;
- cross-model manual dual (`dual_mode: cross_model_manual`) is NOT auto-advance-eligible — it requires human transport by definition (see `hybrid-dual.md`).

## Recording Auto-Iteration In loop-state.md

- `auto_iteration: enabled|disabled` records the mode.
- When the loop auto-advances a phase, update `phase`, `phase_step`, `next_phase`, `role`, `next_action`, `last_event` in `loop-state.md` and append a `state_event` to the worklog.
- When the loop halts, set `loop_status` appropriately (blocked / paused / limit_reached) and record the halt reason in `blockers` or `open_gaps`.

## What Auto-Iteration Must Not Do

- Bypass a halt point because auto-run is enabled.
- Auto-advance through the planning->execution gate without satisfying all auto-dispatch conditions.
- Skip writing `loop-state.md` updates because the loop is "moving fast".
- Convert a cross-model manual dual into an auto-advance step.
- Treat "the user has not responded yet" as consent to proceed through a must-ask checkpoint.
